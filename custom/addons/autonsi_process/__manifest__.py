# Part of Softhealer Technologies.
{
    'name': 'Auto&S.I Process',
    "author": "Auto&S.I",
    "website": "https://www.autonsi.com",
    "support": "s",
    "category": "Stock",
    "license": "OPL-1",
    "version": "15.0.1",
    'depends': ['sale_management', 'stock', 'purchase', 'mrp', 'autonsi_rules'],
    'data': [
        'data/mes_mfg_process_demo.xml',
        'security/ir.model.access.csv',
        'views/mes_mfg_process_menu.xml',
        'views/mes_mfg_process_view.xml',
        'views/stock_rule.xml',
        'views/stock_picking_view.xml',
    ],
    "images": ["static/description/background.png"],
    "auto_install": True,
    "installable": True,
}
