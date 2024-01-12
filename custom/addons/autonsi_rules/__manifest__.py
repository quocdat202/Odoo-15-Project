# Part of Softhealer Technologies.
{
    'name': 'Auto&S.I Action Rules',
    "author": "Auto&S.I",
    "website": "https://www.autonsi.com",
    "support": "s",
    "category": "Stock",
    "license": "OPL-1",
    "summary": "Warehouse Quality Control,Check Stock Quality,Inventory Quality Management,Warehouse Quality Checker,Set Product Quality Control,Stock Quality Control,Product Quality Assurance,MRP Quality Control, Work Order Quality Control,quality inspection Odoo",
    "description": """Currently, in odoo there are no options for ‘Quality Control’ so don’t worry about that, here we build a module that will help you to manage the quality of your products. Nowadays all business have to import and export products, So you can receive goods(products) via transportation. Transportation increases the likelihood of goods being damaged. That’s why you need to check product quality while you receiving or delivering products. Good quality control helps companies meet consumer demand with better products. This module will help you to analyze data of product quality checks. Stock Quality Control Odoo, Inventory Quality Control Management Odoo, Analyze Product Quality Module, Stock Quality Check, Inventory Quality Management, Quality Control In Warehouse, Warehouse Quality Checker, Set Quality Control In Product, Goods Quality Control, Product Stock Quality Control Odoo, Warehouse Quality Control, Analyze Product Quality Module, Check Stock Quality App, Inventory Quality Management, Warehouse Quality Checker, Set Product Quality Control, Goods Quality Control, Stock Quality Control, Product Quality Control Odoo""",
    "version": "15.0.1",
    'depends': [
                'mrp',
                'stock',
                'purchase',
                'sale',
                'l10n_vn',
    ],
    'data': [ 'views/product.xml',],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
}
