# -*- coding: utf-8 -*-

#################################################################################
# Systems Services, Inc.
# Desc: To extend maintenance module to add fields to equipment
#################################################################################

{
    'name': 'Jobs',
    'summary': "Adds jobs module to Odoo.",
    'version': '1.0.1',
    'category': 'SSI',
    'author': 'Systems Services, Inc. '
              'Chad Thompson ',
    'website': 'https://ssibtr.com',
    "depends":  [
        'base',
        'account',
        'base',
        'mrp',
        'mrp_workorder',
        'product',
        'purchase',
        'sale',
        'stock',
        'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/add_default_job_stages.xml',
        'views/jobs.xml',
        'views/wo.xml',
        'views/ssi_mrp_production.xml',
        'views/ssi_account_invoice.xml',
    ],
    'installable': True,
    'application': True,
}
