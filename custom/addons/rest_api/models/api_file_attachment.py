from odoo import fields,models

class ApiFileAttachment(models.Model):
    _name = 'api.file.attachment'
    _description = 'file upload manegement'

    name = fields.Char(string='name')
    file_data = fields.Binary()
    file_name = fields.Char(string='Image', help="save file path string")
    image_small = fields.Image("Image 256", related="file_data", max_width=256, max_height=256, store=False, help="resize image for showing the list")

    res_model = fields.Char(string='res_model')
    res_id = fields.Integer(string='res_id')

    
    
 