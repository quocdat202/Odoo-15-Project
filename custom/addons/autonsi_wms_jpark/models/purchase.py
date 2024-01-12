from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Your customizations here

    def _get_action_view_picking(self, pickings):
        result = super()._get_action_view_picking(pickings)

        if "views" in result:
            for i, view in enumerate(result["views"]):
                if len(view) >= 2 and view[0] and view[1] == "form":
                    res = self.env.ref(
                        "autonsi_wms_jpark.view_jpark_material_receiving_form", False
                    )
                    result["views"][i] = (res and res.id or False, "form")

        return result
