# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Report Designer (XLSX, XLSM)',
    'version': '1.4.9',
    'category': 'Extra Tools',
    'summary': 'Report Designer allows to Create and Print various Financial and Analytical reports in MS Excel format (XLSX, XLSM)',     
    'price': 399.00,
    'currency': 'EUR',
    "license": "OPL-1",     
    'description': """
Report Designer for Odoo.
====================================
Design various Reports and Print Reports in MS Excel format (XLSX)
Generate the Excel Report from a Template.
Report Excel Designer for Odoo. 
    Odoo Report XLSX  Create Excel Report Excel Reports Accounting Reports Financial Report Financial Reports Stock Reports Inventory Reports \
    Dynamic Sale Analysis Reports Export Excel Export xlsx Project Reports Warehouse Reports Purchases Reports Marketing Reports Sales Reports \
    Report Designer Reports Designer Report Builder Reports Builder Product Report Customer Report POS Reports POS Report Analysis Report \
    BI Report BI Reports BI Business Intelligence Report Business Intelligence Reports BI Analytics BI Analytic Data Analysis Reporting Tool
    """,
    'author': 'GTECH',
    'support': 'vk.3141592653@gmail.com',
    'depends': ['base','web','attachment_indexation','mail','base_sparse_field'],
    'images': ['static/description/reports.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/reports_designer_views.xml',
        'views/menuitem.xml',
        'data/ir_sequence_data.xml',
        'data/aggregate_data.xml',
        'wizard/reports_designer_wizard_view.xml',
        'wizard/reports_designer_export_import_wizard_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'reports_designer/static/src/css/reports_designer_modal_dialog.css',
            'reports_designer/static/src/js/basic_model_param.js',
            'reports_designer/static/src/js/domain_param.js',
            'reports_designer/static/src/js/domain_selector_param.js',
            'reports_designer/static/src/js/domain_selector_dialog_param.js',
            'reports_designer/static/src/js/domain_field_param.js',
            'reports_designer/static/src/js/report_model_field_selector.js',
            'reports_designer/static/src/js/report_field.js',
            'reports_designer/static/src/js/form_view_dialog_modal.js',
            'reports_designer/static/src/js/web_export_xlsx.js',
        ],
        'web.assets_qweb': [
            'reports_designer/static/src/xml/templates.xml',
        ],
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    "pre_init_hook": "pre_init_check",
}
