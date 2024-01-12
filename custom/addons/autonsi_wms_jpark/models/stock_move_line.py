from lxml import etree

from odoo import _, api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    demand_qty = fields.Float(string="Demand Qty", related="move_id.product_uom_qty")
    demand_weight = fields.Float(
        string="Demand Weight", related="move_id.demand_weight"
    )
    received_weight = fields.Float(string="Received Weight")
    check_date = fields.Datetime("Check Date")
    create_lot_date = fields.Datetime("Create Date")
    print_lot_date = fields.Datetime("Print Date")
    status = fields.Char("Status", compute="compute_status")
    weight_uom = fields.Many2one(
        "uom.uom", string="UoM", related="product_id.weight_uom_id"
    )
    jwp_label = fields.Char("JWP Label #", related="product_id.jwp_label")
    packaging_code = fields.Char("Packaging")

    def compute_status(self):
        for test in self:
            test.status = True
        print(self.filtered(lambda x: x.weight_uom).mapped("weight_uom"))

    def action_label(self):
        return 1

    def action_create_lot_name(self):
        new_lot_name = self.move_id.generateLotCode(
            self.product_id, self.picking_id.partner_id
        )
        self.lot_name = new_lot_name

    def action_check_input(self):
        return 1

    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     result = super(StockMoveLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    #     if view_type == 'tree':
    #         doc = etree.XML(result['arch'])
    #         qty_done = doc.xpath("//field[@name='qty_done']")
    #         default_picking_sequence_code = self.env.context.get('default_picking_sequence_code')
    #         if qty_done and default_picking_sequence_code == 'IN':
    #             qty_done[0].set("string", "Received Qty")
    #             result['arch'] = etree.tostring(doc, encoding='unicode')
    #
    #
    #     return result
