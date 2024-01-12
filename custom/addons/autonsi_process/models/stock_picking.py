from odoo import api, fields, models


class PickingType(models.Model):
    _inherit = "stock.location"

    warehouse_id = fields.Many2one('stock.warehouse', compute='_compute_warehouse_id', store=True)

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    is_receipt = fields.Boolean(string='Is Receipt', default=False)

    @api.model
    def default_get(self, fields):
        res = super(PickingType, self).default_get(fields)
        res['code'] = "internal"
        return res

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        stock_location = self.env['stock.location'].search([
            ('name', '=', 'Stock'), ('warehouse_id', '=', self.warehouse_id.id)
        ],limit=1)
        self.default_location_src_id = stock_location
        self.default_location_dest_id = stock_location
