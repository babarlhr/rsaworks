# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class SaleNonstockProduct(models.TransientModel):
    _name = 'sale.nonstock.product'
    _description = 'Sale Nonstock Product'

    product_template_id = fields.Many2one('product.template', string="Product to Copy", required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, help="Vendor for Non Stock")

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy_nonstock(self, default=None):
#         raise UserError(_(self.product_template_id.name))
        prod_copy = self.env['product.template'].browse(self.id)
        line_values = prod_copy.copy()
        raise UserError(line_values)
        if default is None:
            default = {}
        default['name'] = _("%s (copy)") % self.product_template_id.name
        return prod_copy.copy(default)


