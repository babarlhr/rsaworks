# -*- coding: utf-8 -*-
# Copyright (C) 2012 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'OSI PO Backorder Report',
    'version': '12.0.0.0.1',
    'author': 'Open Source Integrators',
    'summary': 'Adds the ability to view and print a report of UIGR and Backorder quantities and values',
    'category': 'Purchase',
    'maintainer': 'Open Source Integrators',
    'website': 'http://www.opensourceintegrators.com',
    'depends': ['purchase', 'purchase_stock'],
    'data': [
        'views/po_backorder_view.xml',
        'views/purchase_view.xml',
        'report/po_backorder_report.xml',
        'wizard/po_backorder_wizard_view.xml',
    ],
    'qweb': [        
    ],
    'installable': True,
}
