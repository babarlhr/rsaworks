# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Job Costing Manufacture",
    "summary": "Adds journal entries for labor and overhead"
               "absorption. Associates workcenter and analytic account"
               "to journal entries and analytic entries",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators",
    "category": "Manufacturing",
    "website": "http://www.opensourceintegrators.com",
    "depends": [
        "account",
        "mrp",
        "mrp_account",
        "mrp_bom_cost",
        "mrp_production_add_middle_stuff",
        "ssi_jobs"
    ],
    "data": [
        "wizard/wizard_addition_view.xml",
        "wizard/wizard_product_remove_view.xml",
        "wizard/wizard_addition_wo_view.xml",
        "wizard/wizard_update_source_location_view.xml",
        "views/account_view.xml",
        "views/product_view.xml",
        "views/stock_view.xml",
        "views/mrp_view.xml",
        "data/schedule_action.xml",
    ],
    "installable": True,
}
