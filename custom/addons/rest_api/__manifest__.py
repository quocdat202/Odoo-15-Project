{
    'name': 'Odoo Rest API2',
    'version': '13.0.0',
    'author': 'Arkana Solusi Digital',
    'category': 'Backend',
    'website': 'https://www.arkana.co.id/',
    'summary': 'Restful Api Service',
    'description': '''''',
    # 'external_dependencies': {
    #      'python': ['pyjwt','simplejson'],
    # },
    'depends': ['base','web','product',"stock"],
    'data': [
            'security/ir.model.access.csv',
            'views/refresh_token.xml',
    ],
   
}
