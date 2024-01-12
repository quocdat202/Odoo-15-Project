from odoo import api, fields, models


class Route(models.Model):
    _inherit = 'stock.rule'

    rule_type = fields.Selection([
        ('receive', 'Receive'),
        ('pick_component', 'Pick Component'),
        ('storing_product', 'Storing Product'),
        ('outgoing_shipment', 'Outgoing Shipment'),
        ('stock_transfer', 'Stocks Transfer')], string='Rule Type')


class StockMove(models.Model):
    _inherit = 'stock.move'

    rule_id = fields.Many2one(
        'stock.rule', 'Stock Rule', ondelete='set null', help='The stock rule that created this stock move',
        check_company=True)