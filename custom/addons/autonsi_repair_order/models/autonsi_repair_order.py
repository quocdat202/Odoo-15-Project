from odoo import api, fields, models
from odoo.exceptions import UserError


class AutonsiRepairOrder(models.Model):
	_name = "autonsi.repair.order"
	_order = "create_date desc"
	name = fields.Char("Name", readonly=True, default='New')
	state = fields.Selection([
		('draft', 'Draft'),
		('confirmed', 'Confirmed'),
		('in_progress', 'In Progress'),
		('done', 'Done'),
		('cancel', 'Cancelled')], default="draft")

	mo = fields.Many2one(string="MO", comodel_name='mrp.mop', required=True)
	source = fields.Many2one('stock.location', 'Source', readonly=True, compute="_compute_source")
	detail_ids_order = fields.One2many("autonsi.repair.detail", "ro_id",string="Detail")
	detail_ids_repair = fields.One2many("autonsi.repair.detail", "ro_id",string="Detail")
	lot_domain = fields.One2many('stock.production.lot', compute="_compute_lot_domain")
	def _compute_lot_domain(self):
		mrp_pro_ng_ids = self.mo.cwo_ids.filtered(lambda l: len(l.mrp_pro_ng_ids)>0).mapped("mrp_pro_ng_ids")
		self.lot_domain = mrp_pro_ng_ids.mapped("lot_producing_id")
		#self.lot_domain = None
	def _compute_source(self):
		mrp_pro_ng_ids = self.mo.cwo_ids.filtered(lambda l: len(l.mrp_pro_ng_ids)>0).mapped("mrp_pro_ng_ids")
		source = mrp_pro_ng_ids.mapped("location_dest_id")
		if source:
			self.update({'source':source[0]})
			
		else: 
			self.source = False

	@api.onchange('mo')
	def _onchange_mo(self):
		if self.mo:
			mrp_pro_ng_ids = self.mo.cwo_ids.filtered(lambda l: len(l.mrp_pro_ng_ids)>0).mapped("mrp_pro_ng_ids")
			source = mrp_pro_ng_ids.mapped("location_dest_id")
			if not source:
				raise UserError("The MO not have NG LOT")
				
			
	def check_have_lot(self):
		if not self.detail_ids_order:
			raise UserError("You must choose at least 1 LOT")

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('autonsi.repair.order') or _('New')
		result = super(AutonsiRepairOrder, self).create(vals)
		return result

	def action_confirm(self):
		self.check_have_lot()
		
			
		self.write({'state':'confirmed'})
		
	
	def action_cancel(self):
		self.write({'state':'cancel'})

	def action_in_progress(self):
		self.check_have_lot()
		self.write({'state':'in_progress'})

	def action_done(self):
		self.check_have_lot()
		for detail in self.detail_ids_order:
			if not detail.staff:
				raise UserError("Please select staff")
			if not detail.status:
				raise UserError("Please select status")
			
		for detail in self.detail_ids_order:
			if detail.status == "ok":
				detail.mrp_pro_id.is_ng = False
		self.write({'state':'done'})