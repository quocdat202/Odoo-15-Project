import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MesMfgProcess(models.Model):
    _name = "mes.mfg.process"
    _rec_name = "title"
    _description = "Mes MFG Process"

    title = fields.Char(string="Title")
    user = fields.Many2one("res.users", ondelete="cascade")
    update_date = fields.Datetime(
        "Update Date",
        default=lambda self: fields.Datetime.now())
    remark = fields.Text()
    process_type = fields.Selection([
        ('receive', 'Receive'),
        ('pick_component', 'Pick Component'),
        ('storing_product', 'Storing Product'),
        ('outgoing_shipment', 'Outgoing Shipment'),
        ('stock_transfer', 'Stocks Transfer')], string='Process Type')
    process_sub_ids = fields.One2many('mes.mfg.process.sub', 'process_id')
    route_id = fields.Many2one('stock.location.route', string="Route")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True, ondelete="cascade")

    def sync_rules(self):
        process_sub_list = [(5, 0, 0)]
        StockPicking = self.env['stock.picking.type']
        receipts = StockPicking.search([
            ('is_receipt', '=', True), ('warehouse_id', '=', self.warehouse_id.id)])
        StockRule = self.env['stock.rule']
        if self.process_type == 'receive':
            process_sub_list.append((0, 0, {
                "picking_type_id": receipts.id,
                "location_src_id": receipts.default_location_src_id.id,
                "location_id": receipts.default_location_dest_id.id,
                "flag": True
            }))
            rule_ids = StockRule.search([
                ("rule_type", "=", "receive"),
                ("warehouse_id", "=", self.warehouse_id.id)
            ])
            if rule_ids:
                self.route_id = rule_ids[0].route_id.id
                for rule in rule_ids:
                    process_sub_list.append((0, 0, {
                        "rule_id": rule.id,
                        "picking_type_id": rule.picking_type_id.id,
                        "location_src_id": rule.location_src_id.id,
                        "location_id": rule.location_id.id,
                        "flag": True
                    }))
                self.write({"process_sub_ids": process_sub_list})

        if self.process_type == 'pick_component':
            rule_ids = StockRule.search([
                ("rule_type", "=", "pick_component"),
                ("warehouse_id", "=", self.warehouse_id.id)
            ])
            if rule_ids:
                self.route_id = rule_ids[0].route_id.id
                for rule in rule_ids:
                    process_sub_list.append((0, 0, {
                        "rule_id": rule.id,
                        "picking_type_id": rule.picking_type_id.id,
                        "location_src_id": rule.location_src_id.id,
                        "location_id": rule.location_id.id,
                        "flag": True
                    }))
                self.write({"process_sub_ids": process_sub_list})

        if self.process_type == 'storing_product':
            rule_ids = StockRule.search([
                ("rule_type", "=", "storing_product"),
                ("warehouse_id", "=", self.warehouse_id.id)
            ])
            if rule_ids:
                self.route_id = rule_ids[0].route_id.id
                for rule in rule_ids:
                    process_sub_list.append((0, 0, {
                        "rule_id": rule.id,
                        "picking_type_id": rule.picking_type_id.id,
                        "location_src_id": rule.location_src_id.id,
                        "location_id": rule.location_id.id,
                        "flag": True
                    }))
                self.write({"process_sub_ids": process_sub_list})

        if self.process_type == 'outgoing_shipment':
            rule_ids = StockRule.search([
                ("rule_type", "=", "outgoing_shipment"),
                ("warehouse_id", "=", self.warehouse_id.id)])
            if rule_ids:
                self.route_id = rule_ids[0].route_id.id
                for rule in rule_ids:
                    process_sub_list.append((0, 0, {
                        "rule_id": rule.id,
                        "picking_type_id": rule.picking_type_id.id,
                        "location_src_id": rule.location_src_id.id,
                        "location_id": rule.location_id.id,
                        "flag": True
                    }))
                self.write({"process_sub_ids": process_sub_list})

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        StockRule = self.env['stock.rule']
        self.sync_rules()

    # def delete_rules(self):
    #     for rule in self.process_sub_ids:
    #         if rule.delete == True:
    #             self.write({"process_sub_ids": [(3, rule.id, 0)]})
    #             self.route_id.write({"rule_ids": [(3, rule.rule_id.id, 0)]})

class MesMfgProcessSub(models.Model):
    _name = "mes.mfg.process.sub"
    _description = "Mes MFG Process Sub"

    rule_id = fields.Many2one('stock.rule')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type')
    location_src_id = fields.Many2one(
        'stock.location',
        'Source Location')
    location_id = fields.Many2one(
        'stock.location',
        'Destination Location')
    include_qc = fields.Boolean(string="Include QC")
    is_qc_process = fields.Boolean(string="Is Qc Process")
    process_id = fields.Many2one('mes.mfg.process', invisible=True)
    flag = fields.Boolean(default=False)
    delete = fields.Boolean(default=False)

    @api.model
    def create(self, vals):
        res = super(MesMfgProcessSub, self).create(vals)
        route_id = res.process_id.route_id.id
        StockRule = self.env['stock.rule']
        if res.process_id.process_type == 'receive':
            if not res.flag:
                rec = StockRule.create({
                    "name": "Pull And Push",
                    "action": "pull_push",
                    "procure_method": "make_to_order",
                    "rule_type": res.process_id.process_type,
                    "route_id": route_id,
                    "warehouse_id": res.process_id.warehouse_id.id,
                    "picking_type_id": vals.get("picking_type_id"),
                    "location_src_id": vals.get("location_src_id"),
                    "location_id": vals.get("location_id"),
                })
                res.rule_id = rec.id
                res.flag = True

        if res.process_id.process_type == 'pick_component':
            if not res.flag:
                rec = StockRule.create({
                    "name": "Pull From",
                    "action": "pull",
                    "procure_method": "make_to_order",
                    "rule_type": res.process_id.process_type,
                    "route_id": route_id,
                    "warehouse_id": res.process_id.warehouse_id.id,
                    "picking_type_id": vals.get("picking_type_id"),
                    "location_src_id": vals.get("location_src_id"),
                    "location_id": vals.get("location_id"),
                })
                res.rule_id = rec.id
                res.flag = True

        if res.process_id.process_type == 'storing_product':
            if not res.flag:
                rec = StockRule.create({
                    "name": "Push To",
                    "action": "push",
                    "rule_type": res.process_id.process_type,
                    "route_id": route_id,
                    "warehouse_id": res.process_id.warehouse_id.id,
                    "picking_type_id": vals.get("picking_type_id"),
                    "location_src_id": vals.get("location_src_id"),
                    "location_id": vals.get("location_id"),
                })
                res.rule_id = rec.id
                res.flag = True

        if res.process_id.process_type == 'outgoing_shipment':
            if not res.flag:
                rec = StockRule.create({
                    "name": "Pull From",
                    "action": "pull",
                    "procure_method": "make_to_order",
                    "rule_type": res.process_id.process_type,
                    "route_id": route_id,
                    "warehouse_id": res.process_id.warehouse_id.id,
                    "picking_type_id": vals.get("picking_type_id"),
                    "location_src_id": vals.get("location_src_id"),
                    "location_id": vals.get("location_id"),
                })
                res.rule_id = rec.id
                res.flag = True
        return res

    def write(self, vals):
        res = super(MesMfgProcessSub, self).write(vals)
        if 'picking_type_id' in vals or 'location_src_id' in vals or 'location_id' in vals:
            self.rule_id.write({
                "picking_type_id": vals.get("picking_type_id") or self.picking_type_id,
                "location_src_id": vals.get("location_src_id") or self.location_src_id,
                "location_id": vals.get("location_id") or self.location_id,
            })
        return res

    def delete_rules(self):
        process = self.process_id
        process.write({"process_sub_ids": [(3, self.id, 0)]})
        process.route_id.write({"rule_ids": [(3, self.rule_id.id, 0)]})


