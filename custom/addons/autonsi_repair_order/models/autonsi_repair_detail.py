from odoo import api, fields, models


class AutonsiRepairDetail(models.Model):
	_name = "autonsi.repair.detail"
	
	ro_id = fields.Many2one('autonsi.repair.order', 'Repair Order', required=True)
	product_id = fields.Many2one('product.product', string="Product", readonly=True,related="ro_id.mo.product_id")
	lot_id = fields.Many2one(
		'stock.production.lot', 'Lot', required=True)
	qty = fields.Float("Qty")
	weight = fields.Float("Weight")
	reason = fields.Char("Reason")
	staff = fields.Many2one("res.users",string="Staff")
	remark = fields.Char("Remark")
	status = fields.Selection([
		('ok', 'OK'),
		('ng', 'NG')],string="Status")
	mrp_pro_id = fields.Many2one("mrp.production")
	
	@api.onchange('product_id')
	def _onchange_product_id(self):
		mrp_pro_ng_ids = self.ro_id.mo.cwo_ids.filtered(lambda l: len(l.mrp_pro_ng_ids)>0).mapped("mrp_pro_ng_ids")
		lot_domain = mrp_pro_ng_ids.mapped("lot_producing_id").mapped("id")
		return {'domain':{'lot_id':[('id','in',lot_domain)]}}
	@api.onchange('lot_id')
	def _onchange_lot_id(self):
		if self.lot_id:
			mrp_pro_ng_ids = self.ro_id.mo.cwo_ids.filtered(lambda l: len(l.mrp_pro_ng_ids)>0).mapped("mrp_pro_ng_ids").filtered(lambda l: l.lot_producing_id == self.lot_id)
			self.qty = mrp_pro_ng_ids.qty_producing
			self.mrp_pro_id = mrp_pro_ng_ids

	