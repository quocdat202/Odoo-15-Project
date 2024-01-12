from base64 import b64encode

from odoo import http
from odoo.http import request, route

from ..constants import Api_Prefix
from ..jwt.login import http_route, token_required


class ApiStockPicking(http.Controller):
    @http_route(
        route=["%s/stock-picking/get-put-away/" % (Api_Prefix)], methods=["GET"]
    )
    @token_required()
    def get_put_away(self, **kwargs):
        result = {}
        page = int(request.httprequest.args.get("page", 1))
        pageSize = int(request.httprequest.args.get("pageSize", 10))

        data = (
            request.env["stock.picking"]
            .with_user(kwargs.get("uid", 1))
            .api_get_put_away(page, pageSize)
        )
        result["result"] = data
        return result

    @http_route(
        route=[
            "%s/stock-picking/get-put-away-move-line/<int:picking_id>" % (Api_Prefix)
        ],
        methods=["GET"],
    )
    @token_required()
    def api_get_put_away_move_line(self, picking_id=0, **kwargs):
        result = {}

        data = (
            request.env["stock.picking"]
            .with_user(kwargs.get("uid", 1))
            .api_get_put_away_move_line(picking_id)
        )

        result["result"] = data
        return result

    @http_route(
        route=["%s/stock-picking/scan-put-away" % (Api_Prefix)],
        methods=["POST"],
    )
    @token_required()
    def api_scan_put_away(self, **kwargs):
        body = request.jsonrequest
        move_line_id = body.get("move_line_id", False)
        bin = body.get("bin", False)
        picking_id = body.get("picking_id", False)
        result = {}

        data = (
            request.env["stock.picking"]
            .with_user(kwargs.get("uid", 1))
            .api_scan_put_away(move_line_id, bin, picking_id)
        )

        result["result"] = data
        return result
