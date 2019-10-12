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
    def copy_nonstock(self, default=None):
        active_obj = self.env['sale.order'].browse(self._context.get('active_id'))
        order_line_obj = self.env['sale.order.line']
        # Create New NS Product
        prod_template = self.env['product.template']
        vals = {
            'categ_id':self.product_template_id.categ_id,
            'sale_ok':self.product_template_id.sale_ok,
            'purchase_ok':self.product_template_id.purchase_ok,
            'route_ids':self.product_template_id.route_ids,
            'name':self.product_template_id.name,
            'type':self.product_template_id.type,
        }
        prod_template.create(vals)
        for rec in self:
            vals = {
                'product_id':rec.bundle_id.id,
                'product_uom_qty':rec.qty,
                'product_uom':rec.bundle_id.uom_id.id,
                'price_unit':rec.sale_price,
                'name':rec.bundle_id.name,
                'order_id':active_obj.id,
            }
            order_line_obj.create(vals)
            for product in rec.bundle_id.bundle_product_ids:
                qty = product.qty * rec.qty
                vals = {
                    'product_id':product.product_id.id,
                    'product_uom_qty':qty,
                    'product_uom':product.uom_id.id,
                    'price_unit':0.0,
                    'name':product.product_id.name,
                    'order_id':active_obj.id,
                }
                order_line_obj.create(vals)

        
        
        
        
        
        #         raise UserError(_(self.product_template_id.name))
#         prod_copy = self.env['product.template'].browse(self.id)
#         line_values = prod_copy.copy()
#         raise UserError(line_values)
#         if default is None:
#             default = {}
#         default['name'] = _("%s (copy)") % self.product_template_id.name
#         return prod_copy.copy(default)


