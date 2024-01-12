from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from lxml import etree


class StockPicking(models.Model):
    _inherit = "stock.picking"

    received_date = fields.Datetime("Received Date")
    is_check_popup = fields.Boolean()
    is_lot_popup = fields.Boolean()
    is_print_popup = fields.Boolean()
    is_packaging_popup = fields.Boolean()
    is_complete = fields.Boolean()
    product_quants = fields.Many2many(
        "product.product", compute="_compute_product_quants"
    )

    @api.depends("location_id")
    def _compute_product_quants(self):
        for rec in self:
            rec.product_quants = (
                rec.env["stock.quant"]
                .search([("location_id", "=", rec.location_id.id)])
                .filtered(lambda x: x.available_quantity > 0)
                .mapped("product_id")
            )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("waiting", "Waiting Another Operation"),
            ("confirmed", "Waiting"),
            ("shipping", "Shipping"),
            ("assigned", "Operation"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
    )

    operation_type = fields.Char(
        readonly=True, compute="_compute_operation_type", store=True
    )

    @api.depends("picking_type_id.operation_type")
    def _compute_operation_type(self):
        for record in self:
            record.operation_type = record.picking_type_id.operation_type

    def action_show_check_lot_print(self):
        view = self.env.ref("autonsi_wms_jpark.autonsi_wms_jpark_view_check_lot_form")
        title = self.env.context.get("title", False)
        is_check = self.env.context.get("is_check", False)
        is_lot = self.env.context.get("is_lot", False)
        is_print = self.env.context.get("is_print", False)
        is_packaging = self.env.context.get("is_packaging", False)
        self.is_check_popup = is_check
        self.is_lot_popup = is_lot
        self.is_print_popup = is_print
        self.is_packaging_popup = is_packaging

        return {
            "name": _(title),
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
                is_packaging=is_packaging,
            ),
        }

    def action_confirm(self):
        result = super(StockPicking, self).action_confirm()
        for rec in self:
            if rec.operation_type == "m_receiving":
                move_lines = []
                for move in rec.move_ids_without_package:
                    vals_line = {
                        "product_id": move.product_id.id,
                        "location_dest_id": move.location_dest_id.id,
                        "lot_name": "",
                        "qty_done": 0,
                        "product_uom_id": move.product_uom.id,
                        "location_id": move.location_id.id,
                        "picking_id": rec.id,
                    }
                    move_lines.append((0, 0, vals_line))
                rec.move_line_nosuggest_ids = move_lines
            elif rec.operation_type == "m_putaway":
                move_lines = []
                for move in rec.move_ids_without_package:
                    vals_line = {
                        "product_id": move.product_id.id,
                        "location_dest_id": move.location_dest_id.id,
                        "qty_done": 0,
                        "product_uom_id": move.product_uom.id,
                        "location_id": move.location_id.id,
                        "picking_id": rec.id,
                    }
                    move_lines.append((0, 0, vals_line))
                rec.move_line_ids_without_package = move_lines

            rec.received_date = fields.datetime.utcnow()
            rec.is_confirm = True
        return result

    def action_change_is_complete(self):
        check_can_done = self._pre_action_done_hook()
        if check_can_done is True:
            self.is_complete = True
        else:
            return check_can_done

    def button_validate_custom(self):
        return self.button_validate()

    @api.model
    def default_get(self, fields_list):
        res = super(StockPicking, self).default_get(fields_list)
        operation_type = self.env.context.get("default_operation_type")

        if operation_type and res:
            picking_type_id = self.env["stock.picking.type"].search(
                [("operation_type", "=", operation_type)], limit=1
            )
            res["picking_type_id"] = picking_type_id.id if picking_type_id else False
        return res

    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super(StockPicking, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            doc = etree.XML(result["arch"])
            context = self.env.context.get("0")
            if context and context.get("pickings"):
                pickings = self.env["stock.picking"].browse(context["pickings"])
                default_picking_sequence_code = pickings[
                    0
                ].picking_type_id.sequence_code
                print(context)
            # button_print = doc.xpath("//button[@string='Print']")
            # button_return = doc.xpath("//button[@string='Return']")
            # button_validate_custom = doc.xpath("//button[@name='button_validate_custom']")
            # if button_print:
            #     for node in button_print:
            #         node.getparent().remove(node)
            # if button_return:
            #     for node in button_return:
            #         node.getparent().remove(node)
            # if button_validate_custom:
            #     if default_picking_sequence_code == "FGR":
            #         button_validate_custom[0].set("string", "Complete Receiving")
            #     if default_picking_sequence_code == "FGP":
            #         button_validate_custom[0].set("string", "Complete Packing")
            #     if default_picking_sequence_code == "FGSH":
            #         button_validate_custom[0].set("string", "Complete FG Shipping")
        return result
