# -*- coding: utf-8 -*-

#################################################################################
# Systems Services, Inc.
# Desc: To extend sales order module to add non stock
#################################################################################

{
    'name': 'SSI Non Stock',
    'summary': "Adds Non Stock module to Odoo.",
    'version': '1.0.1',
    'category': 'SSI',
    'author': 'Systems Services, Inc. '
              'Chad Thompson',
    'website': 'https://ssibtr.com',
    "depends":  [
        'base',
        'sale'
    ],
    'data': [
        'views/ssi_sales.xml',
        'wizard/sale_nonstock_product_views.xml',
    ],
    'installable': True,
    'application': True,
}
