# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_labor_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Absorption Account',
        help="This account will be used for Labor absorption on work orders"
    )
    property_account_overhead_absorp_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Burden Account',
        help="This account will be used for Overhead Absorption on work orders"
    )

    property_account_labor_wip_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor WIP Account',
        help="This account will be used for Labor absorption on work orders"
    )
    property_account_overhead_wip_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Burden WIP Account',
        help="This account will be used for Overhead Absorption on work orders"
    )
    property_account_cogs_material_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='COGS Accounts (Material)',
        help="This account will be used for COGS Accounts material on manufaturing orders."
    )
    property_account_cogs_labor_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='COGS Accounts (Labor)',
        help="This account will be used for COGS Accounts labor on manufaturing orders."
    )
    is_job_type = fields.Boolean("Job Costing Required?")


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_labor_absorp_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Absorption Account',
        help="This account will be used for Labor absorption on work orders"
    )
    property_account_overhead_absorp_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Burden Account',
        help="This account will be used for Overhead Absorption on work orders."
    )

    property_account_labor_wip_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor WIP Account',
        help="This account will be used for Labor absorption on work orders"
    )
    property_account_overhead_wip_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Burden WIP Account',
        help="This account will be used for Overhead Absorption on work orders."
    )
    property_account_cogs_material_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='COGS Accounts (Material)',
        help="This account will be used for COGS Accounts material on manufaturing orders."
    )
    property_account_cogs_labor_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='COGS Accounts (Labor)',
        help="This account will be used for COGS Accounts labor on manufaturing orders."
    )
    is_job_type = fields.Boolean(related="categ_id.is_job_type", string="Job Costing Required?")

    @api.multi
    def _get_product_accounts(self):
        """ Add the MRP accounts related to product to the result of super()
        """
        accounts = super(ProductTemplate, self)._get_product_accounts()
        accounts.update({
            'labor_absorption_acc_id':
                self.property_account_labor_absorp_id or
                self.categ_id.property_account_labor_categ_id,
            'overhead_absorption_acc_id':
                self.property_account_overhead_absorp_id or
                self.categ_id.property_account_overhead_absorp_categ_id,
            'production_account_id': self.property_stock_production and
            self.property_stock_production.valuation_in_account_id,
            'labor_wip_acc_id':
                self.property_account_labor_wip_id or
                self.categ_id.property_account_labor_wip_categ_id,
            'overhead_wip_acc_id':
                self.property_account_overhead_wip_id or
                self.categ_id.property_account_overhead_wip_categ_id,
            'cogs_material_id':
                self.property_account_cogs_material_id or
                self.categ_id.property_account_cogs_material_categ_id,
            'cogs_labor_id':
                self.property_account_cogs_labor_id or
                self.categ_id.property_account_cogs_labor_categ_id,

        })
        return accounts