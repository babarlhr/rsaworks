# -*- coding: utf-8 -*-
{
    'name': "ODOO Salesforce Connector",
    'version': '1.0',
    'category': 'Sales',
    'summary': 'ODOO Salesforce',
    'author': 'Techloyce',
    'website': 'http://www.techloyce.com',
    'images': [
        'static/description/icon.png',
    ],
    'depends': ['sale', 'crm', 'sale_crm'],
    'price': 499,
    'currency': 'EUR',
    'license' : 'OPL-1', 
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/schedule.xml',
    ],

    'installable': True,
    'application': True,
}
