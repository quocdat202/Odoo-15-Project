from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_view_mo_delivery(self):
        result = super().action_view_mo_delivery()
        pickings = self.mapped("picking_ids")
        if len(pickings) > 1:
            result["context"] = (
                dict(
                    result["context"],
                    clear_cache=True,
                    picking_ids=pickings.mapped("id"),
                    time=fields.datetime.now(),
                ),
            )
        return result
