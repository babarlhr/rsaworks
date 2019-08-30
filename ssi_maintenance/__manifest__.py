# -*- coding: utf-8 -*-

#################################################################################
# Systems Services, Inc.
# Desc: To extend maintenance module to add fields to equipment
#################################################################################

{
    "name":  "SSI Maintenance Mods",
    "summary":  "Add feilds to the equipment table",
    "category":  "SSI",
    "version":  "1.0",
    "sequence":  1,
    "author":  "Systems Services, Inc.",
    "website":  "https://ssibtr.com",
    "depends":  [
        'maintenance',
        'mrp',
        'mrp_maintenance',
        'sale_subscription',
        'ssi_jobs',
    ],
    "data":  [
        'views/ssi_maintenance.xml',
        'views/ssi_storage.xml',
        'views/ssi_subscription.xml',
        'views/ssi_budgets.xml',
        'report/ssi_maintenance_report.xml',
        'security/ir.model.access.csv',

    ],
    "application":  False,
    "installable":  True,
    "auto_install":  False,
}
