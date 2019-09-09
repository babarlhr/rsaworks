# -*- coding: utf-8 -*-

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class product_product(models.Model):
    """
    Overwrite to calculate lst_price on attributes extra and coefficients
    """
    _inherit = "product.product"

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        """
        Fully re-write to avoid relying upon price_extra

        Methods:
         * _return_price_with_surplus
        """
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            force_company = company and company.id or self._context.get('force_company', self.env.user.company_id.id)
            products = self.with_context(force_company=force_company).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                # invasion start
                prices[product.id] = product._return_price_with_surplus(prices[product.id])
                # invasion end
            if uom:
                prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)
        return prices

    @api.multi
    @api.depends("list_price", "product_template_attribute_value_ids.price_plus",
                 "product_template_attribute_value_ids.price_multiple",
                 "product_template_attribute_value_ids.sequence_esp")
    def _compute_product_lst_price(self):
        """
        Compute method for the attribute lst_price

        Methods:
         * _return_price_with_surplus
        """
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse([self._context['uom']])
        for product in self:
            price = product.list_price
            if to_uom:
                price = product.uom_id._compute_price(price, to_uom)
            price = product._return_price_with_surplus(price)
            product.lst_price = price + product.esp_price

    @api.multi
    def _return_price_with_surplus(self, price=None):
        """
        The method to return prices with attributes coefficients

        Args:
         * price - basic price of product (list_price or pricelist adapted list_price)

        Returns:
         * float

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        res_price = price
        all_values = self.product_template_attribute_value_ids
        if self._context.get('no_variant_attributes_price_extra_advanced'):
            # to the case of no_create attributes
            all_values += self._context.get('no_variant_attributes_price_extra_advanced')
        value_ids = all_values.sorted(lambda v: v.sequence_esp)
        for attr_value in value_ids:
            res_price = (res_price + attr_value.price_plus) * (1 + attr_value.price_multiple / 100)
        return res_price


    lst_price = fields.Float(compute=_compute_product_lst_price)
    esp_price = fields.Float(
        string='Variant Extra Beside Attributes',
        help='Beside attributes multipliers and extras',
        digits=dp.get_precision('Product Price'),
    )
