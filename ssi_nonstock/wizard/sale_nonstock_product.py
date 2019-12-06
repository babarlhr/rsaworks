# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class SaleNonstockProduct(models.TransientModel):
    _name = 'sale.nonstock.product'
    _description = 'Sale Nonstock Product'

    product_template_id = fields.Many2one('product.template', string="Template", required=True)
    product_desc = fields.Char(string="Description", default='', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True, help="Vendor for Non Stock")
    price = fields.Float(string='Sale Price', default=1.0, required=True, help="Sale Price for Order")
    cost = fields.Float(string='Vendor Cost', default=1.0, required=True, help="Vendor Cost for PO")
    categ_id = fields.Many2one('product.category', string='Product Category', help="Product Category")
    order_id = fields.Many2one(
        'sale.order', 'Sale Order', 
        default=lambda self: self.env.context.get('active_id', False))

    @api.multi
    def copy_nonstock(self, default=None):
        # Create New NS Product
        prod_template = self.env['product.template']
        ns_name = self.product_template_id.default_code + self.env['ir.sequence'].next_by_code('ssi_non_stock')
#         category = self.env['product.category'].search([('name','=','Non Stock Job Material')], limit=1).id
        vals = {
            'categ_id':self.categ_id.id,
            'sale_ok':self.product_template_id.sale_ok,
            'purchase_ok':self.product_template_id.purchase_ok,
            'type':self.product_template_id.type,
            'taxes_id':[(6, 0, self.product_template_id.taxes_id.ids)],
            'invoice_policy':self.product_template_id.invoice_policy,
            'list_price':self.price,
            'default_code':ns_name,
            'name':self.product_desc,
            'hide_on_print':self.product_template_id.hide_on_print,
       }
        new_prod_id = prod_template.sudo().create(vals)
#         # Routes
#         route = self.env['stock.location.route']
#         r_vals = {
#             'name':self.product_template_id.route_ids[0].name,
#             'product_tmpl_id':new_prod_id.id,
#         },
#         prod_supplier.create(s_vals)
        # Create Vendor Relationship
        prod_supplier = self.env['product.supplierinfo']
        s_vals = {
            'name':self.partner_id.id,
            'product_tmpl_id':new_prod_id.id,
            'min_qty':self.product_template_id.seller_ids[0].min_qty,
            'delay':self.product_template_id.seller_ids[0].delay,
            'price': self.cost,
            'currency_id':self.product_template_id.seller_ids[0].currency_id.id,
        },
        prod_supplier.sudo().create(s_vals)
        # Create Reordering Rule
        order_point = self.env['stock.warehouse.orderpoint']
        p_vals = {
            'product_id':new_prod_id.product_variant_id.id,
            'product_min_qty':0,
            'product_max_qty':0,
            'qty_multiple':1,
        },
        order_point.sudo().create(p_vals)

        # Add to the sale order
        active_obj = self.env['sale.order'].browse(self._context.get('active_id'))
        order_line_obj = self.env['sale.order.line']
        line_vals = {
            'product_id':new_prod_id.product_variant_id.id,
            'product_uom_qty':1,
            'product_uom':new_prod_id.uom_id.id,
            'price_unit':self.price,
            'purchase_price':self.cost,
            'name':new_prod_id.name,
            'order_id':self.order_id.id,
        }
        order_line_obj.sudo().create(line_vals)

        
        
        
        
        
        #         raise UserError(_(self.product_template_id.name))
#         prod_copy = self.env['product.template'].browse(self.id)
#         line_values = prod_copy.copy()
#         raise UserError(line_values)
#         if default is None:
#             default = {}
#         default['name'] = _("%s (copy)") % self.product_template_id.name
#         return prod_copy.copy(default)


