# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

import logging
from collections import defaultdict, namedtuple

from dateutil.relativedelta import relativedelta

from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero, html_escape
from odoo.tools.misc import split_every

from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    semi_product_is = fields.Boolean(string="Is Semi Product", help="This is Semi Product")



class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = "stock.rule"


    @api.model
    def _run_pull(self, procurements):
        _logger.info('-_run_pull-- %s', procurements)
        tloc = self.env['stock.location'].search([('id','=',19)])
        for procurement, rule in procurements:
            _logger.info('-_run_pull-- %s', procurements)
            if rule.location_id.name == 'Pre-Production':
                if tloc :
                    _logger.info('-tloc1-- %s', tloc)
                    # procurement['location_id'] = tloc

        moves_values_by_company = defaultdict(list)
        mtso_products_by_locations = defaultdict(list)

        # To handle the `mts_else_mto` procure method, we do a preliminary loop to
        # isolate the products we would need to read the forecasted quantity,
        # in order to to batch the read. We also make a sanitary check on the
        # `location_src_id` field.
        for procurement, rule in procurements:
            if not rule.location_src_id:
                msg = _('No source location defined on stock rule: %s!') % (rule.name, )
                raise ProcurementException([(procurement, msg)])

            if rule.procure_method == 'mts_else_mto':
                mtso_products_by_locations[rule.location_src_id].append(procurement.product_id.id)

        # Get the forecasted quantity for the `mts_else_mto` procurement.
        forecasted_qties_by_loc = {}
        for location, product_ids in mtso_products_by_locations.items():
            products = self.env['product.product'].browse(product_ids).with_context(location=location.id)
            forecasted_qties_by_loc[location] = {product.id: product.free_qty for product in products}

        # Prepare the move values, adapt the `procure_method` if needed.
        procurements = sorted(procurements, key=lambda proc: float_compare(proc[0].product_qty, 0.0, precision_rounding=proc[0].product_uom.rounding) > 0)
        for procurement, rule in procurements:
            procure_method = rule.procure_method
            if rule.procure_method == 'mts_else_mto':
                qty_needed = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_id)
                if float_compare(qty_needed, 0, precision_rounding=procurement.product_id.uom_id.rounding) <= 0:
                    procure_method = 'make_to_order'
                    for move in procurement.values.get('group_id', self.env['procurement.group']).stock_move_ids:
                        if move.rule_id == rule and float_compare(move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) > 0:
                            procure_method = move.procure_method
                            break
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                elif float_compare(qty_needed, forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id],
                                   precision_rounding=procurement.product_id.uom_id.rounding) > 0:
                    procure_method = 'make_to_order'
                else:
                    forecasted_qties_by_loc[rule.location_src_id][procurement.product_id.id] -= qty_needed
                    procure_method = 'make_to_stock'

            move_values = rule._get_stock_move_values(*procurement)

            move_values['procure_method'] = procure_method
            moves_values_by_company[procurement.company_id.id].append(move_values)
            _logger.info('-move_values-- %s', move_values)

        for company_id, moves_values in moves_values_by_company.items():
            # create the move as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
            nmovesvalues = []
            # LJY
            for line in moves_values:
                _logger.info('-line-- %s', line)
                product = self.env['product.product'].browse(line['product_id'])
                if product and product.semi_product_is == False :
                   nmovesvalues.append(line)

            moves = self.env['stock.move'].with_user(SUPERUSER_ID).sudo().with_company(company_id).create(nmovesvalues)
            # Since action_confirm launch following procurement_group we should activate it.

            moves._action_confirm()
        return True

class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_relevant_state_among_moves(self):
        # We sort our moves by importance of state:
        #     ------------- 0
        #     | Assigned  |
        #     -------------
        #     |  Waiting  |
        #     -------------
        #     |  Partial  |
        #     -------------
        #     |  Confirm  |
        #     ------------- len-1
        sort_map = {
            'assigned': 4,
            'waiting': 3,
            'partially_available': 2,
            'confirmed': 1,
        }
        moves_todo = self\
            .filtered(lambda move: move.state not in ['cancel', 'done'] and not (move.state == 'assigned' and not move.product_uom_qty))\
            .sorted(key=lambda move: (sort_map.get(move.state, 0), move.product_uom_qty))
        # LJY
        moves_todo = moves_todo.filtered(lambda move: move.product_id.semi_product_is == False)

        if not moves_todo:
            return 'assigned'
        # The picking should be the same for all moves.
        if moves_todo[:1].picking_id and moves_todo[:1].picking_id.move_type == 'one':
            most_important_move = moves_todo[0]
            if most_important_move.state == 'confirmed':
                return 'confirmed' if most_important_move.product_uom_qty else 'assigned'
            elif most_important_move.state == 'partially_available':
                return 'confirmed'
            else:
                return moves_todo[:1].state or 'draft'
        elif moves_todo[:1].state != 'assigned' and any(move.state in ['assigned', 'partially_available'] for move in moves_todo):
            return 'partially_available'
        else:
            least_important_move = moves_todo[-1:]
            if least_important_move.state == 'confirmed' and least_important_move.product_uom_qty == 0:
                return 'assigned'
            else:
                return moves_todo[-1:].state or 'draft'
