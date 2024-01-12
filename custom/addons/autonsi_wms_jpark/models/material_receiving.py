from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_batch = fields.Boolean()
    is_check = fields.Boolean()
    is_confirm = fields.Boolean()
    complete_check = fields.Boolean(compute="_compute_complete_check")
    is_lot = fields.Boolean()
    is_iqc = fields.Boolean()
    can_lot = fields.Boolean(default=False)
    can_print = fields.Boolean(default=False)
    can_iqc = fields.Boolean(default=False)
    can_complete_receiving = fields.Boolean(default=False)

    @api.depends("move_line_nosuggest_ids")
    def _compute_complete_check(self):
        for rec in self:
            rec.complete_check = any(
                rec.move_line_nosuggest_ids.filtered(lambda line: line.check_date)
            )

    def popup_receiving(self):
        if self.operation_type == "m_receiving":
            view = self.env.ref("autonsi_wms_jpark.receive_view_check_lot_form")
        if self.operation_type == "m_shipping":
            view = self.env.ref("autonsi_wms_jpark.shipping_view_check_lot_form")
        is_check = self.env.context.get("is_check", False)
        is_lot = self.env.context.get("is_lot", False)
        is_print = self.env.context.get("is_print", False)
        self.is_check_popup = is_check
        self.is_lot_popup = is_lot
        self.is_print_popup = is_print

        return {
            "name": _("Receiving"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.picking",
            "views": [(view.id, "form")],
            "view_id": view.id,
            "target": "new",
            "res_id": self.id,
            "context": dict(
                self.env.context,
                is_check=is_check,
                is_lot=is_lot,
                is_print=is_print,
            ),
        }

    def action_confirm_check(self):
        selected_ids = self.env.context.get("selected_ids", [])
        selected_records = self.env["stock.move.line"].browse(selected_ids)
        if not selected_ids:
            raise ValidationError("You must choose at least one record.")
        if selected_records.filtered(lambda l: not l.qty_done):
            raise ValidationError("You must enter the quantity received.")
        for rec in selected_records.filtered(lambda l: not l.check_date):
            rec.check_date = fields.datetime.utcnow()
        self.is_check = True
        self.can_lot = True
        self.is_batch = True

        return self.popup_receiving()

    def action_batch_qty(self):
        self.ensure_one()
        selected_ids = self.env.context.get("selected_ids", [])
        selected_records = self.env["stock.move.line"].browse(selected_ids)
        if not selected_ids:
            raise ValidationError("You must choose at least one record.")
        for rec in selected_records:
            rec.write({"qty_done": rec.demand_qty})
        self.is_batch = True
        return self.popup_receiving()

    def action_confirm_lot(self):
        selected_ids = self.env.context.get("selected_ids", [])
        if not selected_ids:
            raise ValidationError("You must choose at least one record.")
        move_lines = self.move_line_nosuggest_ids.browse(selected_ids)
        for line in move_lines.filtered(lambda l: not l.lot_name):
            new_lot_name = line.move_id.generateLotCode(
                line.product_id, self.partner_id
            )
            line.lot_name = new_lot_name
            line.create_lot_date = fields.datetime.utcnow()
        self.is_lot = True
        self.can_iqc = True
        self.can_lot = False
        return self.popup_receiving()

    def action_print(self):
        return self.popup_receiving()

    def action_complete(self):
        self.is_complete = True
