# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI Credit Card Reconciliation",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
	"description": """
    Provide Feature to Support Credit Card Reconciliation.
    """,
    "author": "Open Source Integrators",
    "maintainer": "Open Source Integrators",
    "website": "http://www.opensourceintegrators.com",
    "category": "Account",
    "images": [],
    "depends": [
        'account',
        'account_payment_cc',
    ],
    "data": [
        "security/credit_card_reconciliation_security.xml",
        'security/ir.model.access.csv',
        "views/credit_card_reconciliation_view.xml",
        "views/account_move_line_view.xml",
        "views/credit_card_report_view.xml",
        "views/report_card_detail.xml",
        "views/report_card_summary.xml",
    ],
    "post_init_hook": 'post_init',
    "auto_install": False,
    "application": False,
    "installable": True,
}
