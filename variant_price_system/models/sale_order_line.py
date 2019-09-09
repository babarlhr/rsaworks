# -*- coding: utf-8 -*-

from odoo import api, fields, models


class sale_order_line(models.Model):
    """
    Re-write to pass context in case of no_variant option
    """
    _inherit = 'sale.order.line'

    @api.multi
    def _get_display_price(self, product):
        """
        Rw-write to reflect no_create prices
        """
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=no_variant_attributes_price_extra
            )
        # invasion start
        no_variant_attributes_price_extra_advanced = [
            ptav for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra_advanced:
            product = product.with_context(
                no_variant_attributes_price_extra_advanced=no_variant_attributes_price_extra_advanced
            )
        # invasion end
        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)
        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
                                                self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                 self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.user.company_id, self.order_id.date_order or fields.Date.today())
        return max(base_price, final_price)

