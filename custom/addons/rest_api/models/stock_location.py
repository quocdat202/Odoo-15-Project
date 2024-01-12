import werkzeug.exceptions

from odoo import models

from ..exceptions import RestException


class StockLocation(models.Model):
    _inherit = "stock.location"

    def api_get_location(self, location_code):
        read_list = [
            "name",
            "complete_name",
            "location_code",
        ]

        search_list = [
            ("location_code", "=", location_code),
        ]
        data = self.search(
            search_list,
        )
        if not data:
            raise RestException(404, "Location not found")

        result = data.read(read_list)
        total = data.search_count(search_list)
        return {"list": result, "count": total}
