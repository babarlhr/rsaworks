# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_round


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_material_variance_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Material Variance Account',
        help="This account will be used for material variance"
    )
    property_account_labor_variance_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Variance Account',
        help="This account will be used for Labor variance"
    )
    property_account_manufacturing_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Absorption Account',
        help="This account will be used for Labor absorption for manufacturing"
    )
    property_account_overhead_variance_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Overhead Variance Account',
        help="This account will be used for Overhead variance"
    )
    property_account_overhead_absorp_categ_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Overhead Absorption Account',
        help="This account will be used for Overhead Absorption."
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_bom_std_costs(self):

        for product in self:

            total_std_labor = 0
            total_std_overhead = 0
            total_std_material = 0

            bom_obj = self.env['mrp.bom']
            precision = 4

            bom = bom_obj._bom_find(product_tmpl=product)                     
            if bom:
                for sbom in bom.bom_line_ids:
                    new_qty = sbom.product_qty / sbom.product_efficiency
                    if not sbom.attribute_value_ids:
                        # No attribute_value_ids means the bom line is not
                        # variant specific
                        total_std_material += \
                            sbom.product_id.uom_id._compute_price(
                                sbom.product_id.standard_price,
                                sbom.product_uom_id) * new_qty

                if bom.routing_id:
                    for wline in bom.routing_id.operation_ids:
                        wc = wline.workcenter_id
                        total_std_labor += wline.cycle_nbr * wc.costs_cycle + \
                                           (wc.time_start + wc.time_stop +
                                            wline.hour_nbr * wline.cycle_nbr) \
                                           * wc.costs_hour
                        total_std_overhead += (wc.time_start + wc.time_stop +
                                               wline.hour_nbr * wline.cycle_nbr
                                              ) * wc.overhead_cost_per_cycle
                        total_std_labor = bom.product_uom_id._compute_price(
                            total_std_labor, bom.product_id.uom_id)
                        total_std_overhead = bom.product_uom_id._compute_price(
                            total_std_overhead, bom.product_id.uom_id)
                product.std_labor = float_round(
                    total_std_labor, precision_digits=precision)
                product.std_overhead = float_round(
                    total_std_overhead, precision_digits=precision)
                product.std_material = float_round(
                    total_std_material, precision_digits=precision)
            else:
                total_std_material = float_round(
                    product.standard_price, precision_digits=precision)
                product.std_material = total_std_material


    property_account_material_variance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Material Variance Account',
        help="This account will be used for material variance"
    )
    property_account_labor_variance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Variance Account',
        help="This account will be used for Labor variance"
    )
    property_account_manufacturing_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Labor Absorption Account',
        help="This account will be used for Labor absorption for manufacturing"
    )
    property_account_overhead_variance_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Overhead Variance Account',
        help="This account will be used for Overhead variance"
    )
    property_account_overhead_absorp_id = fields.Many2one(
        'account.account',
        company_dependent=True,
        string='Overhead Absorption Account',
        help="This account will be used for Overhead Absorption."
    )
    std_labor = fields.Float('Std. Labor', compute='_get_bom_std_costs')
    std_overhead = fields.Float('Std. Overhead', compute='_get_bom_std_costs')
    std_material = fields.Float('Std. Material', compute='_get_bom_std_costs')

    @api.multi
    def _get_product_accounts(self):
        """ Add the MRP accounts related to product to the result of super()
        """
        accounts = super(ProductTemplate, self)._get_product_accounts()
        accounts.update({
            'material_variance_acc_id':
                self.property_account_material_variance_id or
                self.categ_id.property_account_material_variance_categ_id,
            'labor_variance_acc_id':
                self.property_account_labor_variance_id or
                self.categ_id.property_account_labor_variance_categ_id,
            'manufacturing_acc_id':
                self.property_account_manufacturing_id or
                self.categ_id.property_account_manufacturing_categ_id,
            'overhead_variance_acc_id':
                self.property_account_overhead_variance_id or
                self.categ_id.property_account_overhead_variance_categ_id,
            'overhead_absorption_acc_id':
                self.property_account_overhead_absorp_id or
                self.categ_id.property_account_overhead_absorp_categ_id
        })
        return accounts


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _compute_bom_price(self, bom, boms_to_recompute=False):
        price = super()._compute_bom_price(bom,
                                           boms_to_recompute=boms_to_recompute)
        overhead_cost = 0
        precision = 4
        if bom.routing_id:
            for wline in bom.routing_id.operation_ids:
                wc = wline.workcenter_id
                overhead_cost += \
                    (wc.time_start + wc.time_stop + wline.hour_nbr *
                     wline.cycle_nbr) * wc.overhead_cost_per_cycle
                overhead_cost = bom.product_uom_id._compute_price(
                    overhead_cost, bom.product_id.uom_id)

        # Convert on product UoM quantities
        if overhead_cost > 0:
            overhead_cost = bom.product_uom_id._compute_price(
                (overhead_cost / bom.product_qty), bom.product_id.uom_id)
            price += overhead_cost
            price = float_round(price, precision_digits=precision)
        return price