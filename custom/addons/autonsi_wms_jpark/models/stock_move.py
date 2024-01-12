import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"


    demand_weight = fields.Float("Demand Weight", default=0.0)
    received_weight = fields.Float("Received Weight", default=0.0, compute="_compute_weight")
    lot_code = fields.Char("Lot code")
    confirm_date = fields.Datetime("Confirmation Date")
    weight_uom = fields.Many2one('uom.uom', string="UoM", related='product_id.weight_uom_id')

    @api.depends('picking_id.move_line_nosuggest_ids.received_weight')
    def _compute_weight(self):
        for rec in self:
            filtered_lines = rec.picking_id.move_line_nosuggest_ids.filtered(
                lambda line: line.product_id == rec.product_id)
            total_weight = sum(filtered_lines.mapped('received_weight'))
            rec.received_weight = total_weight
