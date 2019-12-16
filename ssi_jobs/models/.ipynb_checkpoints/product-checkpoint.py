# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hide_on_print = fields.Boolean('Do Not Print', default=False)

class ProductCategory(models.Model):
    _inherit = "product.category"

    hide_on_print = fields.Boolean('Do Not Print', default=False)
    profit_center = fields.Selection(
        [('Disassembly', 'Disassembly'), ('Machine Shop', 'Machine Shop'), ('Winding', 'Winding'), ('Assembly', 'Assembly'), ('Field Services', 'Field Services'), ('New Product Sales', 'New Product Sales'), ('Storage', 'Storage'), ('Training', 'Training')], string='Profit Center')

class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    rebate_amount = fields.Float('Rebate Amount', digits=dp.get_precision('Product Price'))
