from odoo import models
import uuid


class RestCr(models.Model):
    _name = 'rest.cr'
    _description = 'rest handler'

    def login(self, uid, store_id=False):
        result = {}
        res_user_doc = self.env['res.users'].browse(uid)
      
        search_list = [['user_id', '=', uid], ['state', '=', 'granted']]
        refresh_token_doc = self.env['refresh.token'].sudo().search(
            search_list, limit=1)
        if not refresh_token_doc.exists():
            refresh_token = uuid.uuid1().hex
            self.env['refresh.token'].sudo().create(
                {"name": refresh_token, "user_id": uid})
        else:
            refresh_token = refresh_token_doc.name

        result['refresh_token'] = refresh_token

         # So that the return is only one User
        res_user = res_user_doc.read(["name"])[0]
      
        user=res_user_doc[0].env
        if (user.su or user.user._is_admin()):
            res_user['is_admin'] = True
        else:
            res_user['is_admin'] = False
        
        result['res_user'] = res_user

        return result

    def get_refresh_token(self, uid, refresh_token):
        uid = int(uid)
        search_list = [['user_id', '=', uid], [
            'name', '=', refresh_token], ['state', '=', 'granted']]
        refresh_token_doc = self.env['refresh.token'].search(
            search_list, limit=1)
        if not refresh_token_doc.exists():
            return False
        return (refresh_token_doc.user_id.id, refresh_token_doc.user_id.name)
    
 