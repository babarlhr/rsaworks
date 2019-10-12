# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleNonstockProduct(models.TransientModel):
    _name = 'sale.nonstock.product'
    _description = 'Sale Nonstock Product'

    product_template_id = fields.Many2one('product.template', string="Product", required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, help="Vendor for Non Stock")
