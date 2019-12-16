# -*- coding: utf-8 -*-

#################################################################################
# Systems Services, Inc.
# Desc: To extend accounting modules
#################################################################################

{
    'name': 'SSI Accounting',
    'summary': "Accounting Customizations",
    'version': '1.0.1',
    'category': 'SSI',
    'author': 'Systems Services, Inc. '
              'Chad Thompson',
    'website': 'https://ssibtr.com',
    "depends":  [
        'base',
        'account',
        'ssi_lead',
        'account_reports',
    ],
    'data': [
        'views/ssi_accounting.xml',
        'views/ssi_reports.xml',
        'report/ssi_gross_margin_report.xml',
        'report/ssi_wip_report.xml',
        'data/payment_notification.xml'
    ],
    'installable': True,
    'application': False,
}
