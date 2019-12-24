# -*- coding: utf-8 -*-

#################################################################################
# Systems Services, Inc.
# Desc: To extend expemses module to add fields
#################################################################################

{
    'name': 'SSI Expenses',
    'summary': "Adds Fields to Expenses module.",
    'version': '1.0.0',
    'category': 'SSI',
    'author': 'Systems Services, Inc. '
              'Chad Thompson',
    'website': 'https://ssibtr.com',
    "depends":  [
        'base',
        'hr_expense',
        'sale_expense',
    ],
    'data': [
        'views/ssi_expenses.xml',
    ],
    'installable': True,
    'application': False,
}
