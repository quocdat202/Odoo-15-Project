# -*- coding: utf-8 -*-
{
    "name": "Autonsi Demo Menu",
    "summary": "",
    "description": "",
    "author": "Truong",
    "website": "http://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Autonsi",
    "version": "0.1",
    "sequence": 0,
    # any module necessary for this one to work correctly
    "depends": ["autonsi_quality", "autonsi_wms", "autonsi_process"],
    "data": [
        "views/menu.xml",
    ],
}
