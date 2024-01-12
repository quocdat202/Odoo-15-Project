import secrets

from odoo import api, fields, models


API_KEY_SIZE = 20  # in bytes


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zld_allowed_models = fields.Many2many(
        'ir.model',
        readonly=False,
        related='company_id.zld_allowed_models',
    )

    zld_api_key = fields.Char(
        string='ZLD API Key',
        compute='_compute_zld_api_key',
        help='API key for the access from ZPL Label Designer',
    )

    printer_name = fields.Char(
        string='Printer Name',
        required=False,
         readonly=False,
    )
    host_ip = fields.Char(
        string='Host IP',
        required=False,
         readonly=False,
    )

    status_printer = fields.Char(
        string='Status printer connected',
        required=False,
         readonly=True,
    )

    def _compute_zld_api_key(self):
        """
        Update API key for all config settings
        """
        for record in self:
            record.zld_api_key = self.get_zld_api_key()

    def generate_zld_api_key(self):
        """
        Generate API key to use for API requests from designer to Odoo.
        """
        api_key = secrets.token_hex(API_KEY_SIZE)
        self.env['ir.config_parameter'].sudo().set_param('zpl_label_designer.api_key', api_key)
        return

    def get_values(self):
        """
        Get values for the installed integration.
        """
        res = super(ResConfigSettings, self).get_values()
        printer_name=self.env['ir.config_parameter'].sudo().get_param('printer_name')
        host_ip=self.env['ir.config_parameter'].sudo().get_param('host_ip')
        status_printer=self.env['ir.config_parameter'].sudo().get_param('status_printer')
        
        zld_api_key = self.get_zld_api_key()
        res.update(zld_api_key=zld_api_key,printer_name=printer_name,host_ip=host_ip,status_printer=status_printer)

        return res
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('printer_name',self.printer_name)
        self.env['ir.config_parameter'].sudo().set_param('host_ip',self.host_ip)
        #self.env['ir.config_parameter'].sudo().set_param('status_printer',self.status_printer)
        return 
    

    @api.model
    def get_zld_api_key(self):
        """
        Get API key for the installed integration.
        """
        return self.env['ir.config_parameter'].sudo().get_param('zpl_label_designer.api_key')
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
        submenu=False):
        res = super(ResConfigSettings, self).fields_view_get(
        view_id=view_id, view_type=view_type, toolbar=toolbar,
        submenu=submenu)
        #------- called you method here--------





        return res