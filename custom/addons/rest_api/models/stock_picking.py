import werkzeug.exceptions

from odoo import models

from ..exceptions import RestException


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def api_get_put_away(self, page=1, pageSize=10):
        read_list = [
            "name",
            "location_id",
            "location_dest_id",
            "partner_id",
            "scheduled_date",
            "origin",
        ]

        search_list = [
            ("picking_type_id.name", "=", "Put Away"),
            ("state", "=", "assigned"),
        ]

        order = "name desc"
        data = self.search(
            search_list, offset=(page - 1) * pageSize, limit=pageSize, order=order
        )
        total = data.search_count(search_list)
        result = data.read(read_list)
        return {"list": result, "count": total}

    def api_get_put_away_move_line(self, picking_id=0):
        read_list = [
            "product_id",
            "location_id",
            "location_dest_id",
            "lot_id",
            "product_uom_qty",
            "qty_done",
        ]

        search_list = [
            ("id", "=", picking_id),
        ]
        data = self.search(
            search_list,
        )
        if not data:
            raise RestException(404, "Put Away not found")
        if data.state != "assigned":
            raise RestException(400, "Put Away not in state Ready")

        result = data.move_line_ids.read(read_list)
        total = data.search_count(search_list)
        return {"list": result, "count": total}

    def api_scan_put_away(self, move_line_id, bin, picking_id):
        read_list = [
            "product_id",
            "location_id",
            "location_dest_id",
            "lot_id",
            "product_uom_qty",
            "qty_done",
        ]

        search_list = [
            ("id", "=", picking_id),
        ]
        data = self.search(
            search_list,
        )
        if not data:
            raise RestException(404, "Put Away not found")
        if data.state != "assigned":
            raise RestException(400, "Put Away not in state Ready")

        move_line = data.move_line_ids.search([("id", "=", move_line_id)])
        if not move_line:
            raise RestException(404, "Lot not found")

        move_line.update({"qty_done": move_line.product_qty, "location_dest_id": bin})

        check_can_done = data._pre_action_done_hook()
        if check_can_done is True:
            data.button_validate()
        else:
            check_can_done = False
        result = data.move_line_ids.read(read_list)
        total = data.search_count(search_list)
        return {"list": result, "count": total, "check_can_done": check_can_done}
