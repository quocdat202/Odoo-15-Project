from base64 import b64encode

from odoo import http
from odoo.http import request, route

from ..constants import Api_Prefix
from ..jwt.login import http_route, token_required


class ApiStockLocation(http.Controller):
    @http_route(
        route=["%s/stock-location/get-location/<string:location_code>" % (Api_Prefix)],
        methods=["GET"],
    )
    @token_required()
    def api_get_location(self, location_code, **kwargs):
        result = {}
        data = (
            request.env["stock.location"]
            .with_user(kwargs.get("uid", 1))
            .api_get_location(location_code)
        )

        result["result"] = data
        return result
