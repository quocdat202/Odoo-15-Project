import datetime
import functools
import json
import logging

import jwt
import werkzeug

from odoo import _, http
from odoo.http import request, route

from ..constants import Api_Prefix, Secret_key

_logger = logging.getLogger(__name__)


def _response(headers, body, status=200, request_type="http"):
    if request_type == "json":
        response = {}
        response["error"] = [
            {
                "code": status,
                "message": body["message"],
            }
        ]
        response["route"] = True
        return response
    try:
        fixed_headers = {str(k): v for k, v in headers.items()}
    except:
        fixed_headers = headers
        response = werkzeug.Response(
            response=json.dumps(body), status=status, headers=fixed_headers
        )
    return response


def token_required(**kw):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kw):
            headers = dict(request.httprequest.headers.items())
            request_type = request._request_type
            auth = headers.get("Authorization", None)
            if not auth:
                return {"error": {"code": 403, "message": "No Authorization"}}
            # parts = auth.split()
            # if parts[0].lower() != 'bearer':
            #     return {'error' : {'code': 403, 'message': 'Authorization header must start with Bearer'}}
            # elif len(parts) == 1:
            #     return {'error' : {'code': 403, 'message': 'Token not found'}}
            # elif len(parts) > 2:
            #     return {'error' : {'code': 403, 'message': 'Authorization header must be Bearer + \s + token'}}
            token = auth  # parts[1]
            try:
                data = jwt.decode(token, Secret_key, "HS256")
                kw["uid"] = data["uid"]
            except jwt.ExpiredSignatureError:
                return {"error": {"code": 401, "message": "Token is expired"}}
            except jwt.DecodeError:
                return {"error": {"code": 401, "message": "Token signature is invalid"}}
            response = f(*args, **kw)
            return response

        return wrapper

    return decorator


def http_route(*args, **kwargs):
    def decorator(controller_method):
        @route(
            route=kwargs["route"] if len(args) == 0 else args[0],
            methods=kwargs["methods"],
            type=kwargs.get("type", "json"),
            auth=kwargs.get("auth", "public"),
            csrf=kwargs.get("csrf", False),
        )
        @functools.wraps(controller_method)
        def controller_method_wrapper(*iargs, **ikwargs):
            response = controller_method(*iargs, **ikwargs)
            return response

        return controller_method_wrapper

    return decorator


class ApiLogin(http.Controller):
    def _response(self, headers, body, status=200):
        try:
            fixed_headers = {str(k): v for k, v in headers.items()}
        except:
            fixed_headers = headers
        response = werkzeug.Response(
            response=body, status=status, headers=fixed_headers
        )
        return response

    @http_route(
        "%s/login" % (Api_Prefix),
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def get_login(self, **kw):
        headers = dict(request.httprequest.headers.items())
        body = request.jsonrequest
        username = body.get("username", False)
        password = body.get("password", False)
        grant_type = body.get("grant_type", False)
        refresh_token = body.get("refresh_token", False)
        uid = body.get("user_id", False)
        if grant_type == "refresh_token" and (refresh_token and uid):
            request_result = (
                request.env["rest.cr"].sudo().get_refresh_token(uid, refresh_token)
            )
            if request_result:
                uid = request_result[0]
                username = request_result[1]
                token = jwt.encode(
                    {
                        "uid": uid,
                        "user": username,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(seconds=86400),
                    },
                    Secret_key,
                )
                result = {}

                result["token"] = token.decode("UTF-8")
                result["token_live"] = 86400
                result["refresh_token"] = refresh_token
                return {"result": result}
            else:
                return {"error": {"code": 401, "message": "Invalid Refresh Token"}}

        if username and password:
            uid = request.session.authenticate(
                request.session.db, username, password
            )  # or request.cr.dbname for dbname
            if uid:
                token = jwt.encode(
                    {
                        "uid": uid,
                        "user": username,
                        "exp": datetime.datetime.utcnow()
                        + datetime.timedelta(seconds=86400),
                    },
                    Secret_key,
                    algorithm="HS256",
                )

                request_result = request.env["rest.cr"].login(uid)
                if request_result:
                    _logger.info("hasattr" + str(hasattr(token, "decode")))
                    _logger.info("is byte" + str(type(token) is bytes))
                    if hasattr(token, "decode") and type(token) is bytes:
                        request_result["access_token"] = token.decode("UTF-8")
                    else:
                        request_result["access_token"] = token
                    request_result["token_live"] = 86400
                    return {"result": request_result}

    @http_route(
        "%s/list-menus" % (Api_Prefix),
        type="json",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    @token_required()
    def get_list_menu(self, **kwargs):
        menu_ids = request.env["ir.ui.menu"].with_user(kwargs.get("uid", 1)).search([])

        list2 = menu_ids.read([], load=False)
        res_dict_menus = {}
        for m in list2:
            res_dict_menus[m["id"]] = m

        top_menus = list(filter(lambda x: x.get("parent_id", False) == False, list2))

        res_lst = []
        for m in top_menus:
            top_parent = {"text": m["name"], "value": "#", "child_id": m["child_id"]}
            res_lst.append(top_parent)
            self.menu_info_recursion(top_parent, res_dict_menus)

        return {"result": res_lst}

    def menu_info_recursion(self, m, dict_menus):
        if "children" not in m:
            m["children"] = []

        if "child_id" in m:
            for c_id in m["child_id"]:
                m_child = dict_menus[c_id]
                m_obj = {
                    "text": m_child["name"],
                    "value": "#",
                    "child_id": m_child["child_id"],
                }
                m["children"].append(m_obj)
                self.menu_info_recursion(m_obj, dict_menus)
