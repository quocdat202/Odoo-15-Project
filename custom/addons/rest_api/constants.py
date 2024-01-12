from odoo.tools.config import config

Api_Prefix = "/api"
Secret_key = config.options.get("jwt_secret_key", "nnhieu.htb@2023")
