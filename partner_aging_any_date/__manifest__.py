# -*- coding: utf-8 -*-
{
    'name': 'Interactive Partner Aging for any date',
    'version': '12.0.1.0.0',
    'author': 'Open Source Integrators',
    'summary': 'Aging as a view - invoices and credits (OSI)',
    'category': 'Accounting & Finance',
    'maintainer': 'Open Source Integrators',
    'website': 'http://www.opensourceintegrators.com',
    'depends': ['account',
                'account_accountant',
                'account_voucher'
    ],
    'data': [
        'wizard/partner_aging_customer.xml',
        'wizard/partner_aging_supplier.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
