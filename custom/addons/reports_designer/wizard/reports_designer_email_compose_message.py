# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
# import re
from odoo import api, fields, models, _
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
class ReportsDesignerMailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'
    @api.onchange('template_id')
    def _onchange_template_id_wrapper(self):
        self.ensure_one()
        values = self._onchange_template_id(self.template_id.id, self.composition_mode, self.model, self.res_id)['value']
        for fname, value in values.items():
            if 'active_model' in self._context :
                if not (self._context['active_model'] == 'reports_designer_wizard' and fname == 'attachment_ids'):
                    setattr(self, fname, value)     
            else:
                setattr(self, fname, value)                 
