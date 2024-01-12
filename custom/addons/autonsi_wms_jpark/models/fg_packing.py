from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_pack_mapping(self):
        return 1

    def action_show_packing_popup(self):
        view = self.env.ref('autonsi_wms_jpark.autonsi_wms_jpark_view_packing_popup')
        return {
            'name': _("Packaging"),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context, 
            ),
        }
    def action_pack_create_packaging(self):
        selected_ids = self.env.context.get('selected_ids', [])
        selected_records = self.env['stock.move.line'].browse(selected_ids)
        for rec in selected_records.filtered(lambda l: not l.packaging_code):
            packaging_code = rec.move_id.generateLotCode(
                rec.product_id, self.partner_id
            )
            rec.packaging_code = packaging_code
        return self.action_show_packing_popup()
    
    def action_pack_confirm_packaging(self):
        selected_ids = self.env.context.get('selected_ids', [])
        selected_records = self.env['stock.move.line'].browse(selected_ids)
        if selected_records.filtered(lambda l: not l.packaging_code):
            raise ValidationError("Please create packaging code for all products.")
        for rec in selected_records.filtered(lambda l: not l.check_date):
            rec.check_date = fields.datetime.utcnow()
        return self.action_show_packing_popup()
    
    def action_change_complete_fg_packing(self):
        if self.move_line_ids_without_package.filtered(lambda l: not l.packaging_code):
            raise ValidationError("Please create packaging code for all products.")
        check_can_done = self._pre_action_done_hook()
        if check_can_done is True:
            self.is_complete = True
        else: return check_can_done
    
    
  