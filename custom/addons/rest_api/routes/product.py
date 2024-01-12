from odoo import http
from odoo.http import request, route
from base64 import b64encode
from ..jwt.login import token_required, http_route
from ..constants import Api_Prefix

class ApiProduct(http.Controller):
    @http_route(route=['%s/product/'%(Api_Prefix),
                  '/api/v1/product/<int:product_id>'],
           methods=['GET'])
    @token_required()
    def get_product(self, product_id=False, **kwargs):
            result = {}
            product = request.env['product.product'].with_user(
            kwargs.get('uid', 1)).api_get_product(product_id=product_id)
            result['result'] = product
            return result
   
    @route(route=['%s/category/'%(Api_Prefix),
                  '/api/v1/category/<int:category_id>'],
           methods=['GET'])
    @token_required()
    def get_category(self, category_id=False, debug=False, **kwargs):
        category = request.env['product.category'].with_user(
            kwargs.get('uid', 1)).api_get_category(category_id=category_id)
        result = {}
        result['result'] = category
        return result

    @route('%s/category'%(Api_Prefix),methods=['POST'])
    @token_required()
    def post_category(self, **kwargs):
        body = request.jsonrequest
        result = request.env['product.category'].api_post_category(body,**kwargs)
        return {'result': result,'code':201}
    
    @http_route('%s/category/<int:category_id>'%(Api_Prefix),methods=['PUT'], type='http')
    @token_required()
    def edit_category(self, category_id, **kwargs):
        if 'file01' in request.params:
            files = request.httprequest.files.getlist('file01')  
            for attachment in files:
                attached_file = attachment.read()
                request.env['api.file.attachment'].sudo().create({
                            'name': attachment.filename,
                            'res_model': 'project.task',
                            'res_id': 1,
                            'file_name': attachment.filename,
                            'file_data': b64encode(attached_file),
                })                  
       
       # result = request.env['product.category'].api_edit_category(category_id, body,**kwargs)
        return {'result': '','code':200}
    