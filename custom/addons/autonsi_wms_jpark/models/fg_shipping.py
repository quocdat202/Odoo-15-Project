from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

   
    def action_change_complete_fg_shipping(self):
        check_can_done = self._pre_action_done_hook()
        if check_can_done is True:
            self.is_complete = True
        else: return check_can_done
    
    
  