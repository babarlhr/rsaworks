# -*- coding: utf-8 -*-

from odoo import api, fields, models


class product_template(models.Model):
    """
    Overwrite to the case when a variant is only to create
    """
    _inherit = "product.template"

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        """
        Fully re-write to avoid relying upon price_extra
        """
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        templates = self
        if price_type == 'standard_price':
            force_company = company and company.id or self._context.get('force_company', self.env.user.company_id.id)
            templates = self.with_context(force_company=force_company).sudo()
        if not company:
            if self._context.get('force_company'):
                company = self.env['res.company'].browse(self._context['force_company'])
            else:
                company = self.env.user.company_id
        date = self.env.context.get('date') or fields.Date.today()

        prices = dict.fromkeys(self.ids, 0.0)
        for template in templates:
            prices[template.id] = template[price_type] or 0.0
            if price_type == 'list_price' and self._context.get('current_attributes_price_extra_advanced'):
                # invasion start - needed only to the case when 'create_product' is set to attribute
                price = prices[template.id]
                valueids = self._context.get('current_attributes_price_extra_advanced').sorted(lambda v: v.sequence_esp)
                for attr_value in valueids:
                    price = (price + attr_value.price_plus) * (1 + attr_value.price_multiple / 100)
                prices[template.id] = price
                # invasion end
            if uom:
                prices[template.id] = template.uom_id._compute_price(prices[template.id], uom)
            if currency:
                prices[template.id] = template.currency_id._convert(prices[template.id], currency, company, date)
        return prices

    @api.multi
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False,
                              parent_combination=False, only_template=False):
        """
        Fully re-write to pass proper context to price_compute
        """
        self.ensure_one()
        display_name = self.name
        quantity = self.env.context.get('quantity', add_qty)
        context = dict(self.env.context, quantity=quantity, pricelist=pricelist.id if pricelist else False)
        product_template = self.with_context(context)
        combination = combination or product_template.env['product.template.attribute.value']
        if not product_id and not combination and not only_template:
            combination = product_template._get_first_possible_combination(parent_combination)
        if only_template:
            product = product_template.env['product.product']
        elif product_id and not combination:
            product = product_template.env['product.product'].browse(product_id)
        else:
            product = product_template._get_variant_for_combination(combination)
        if product:
            no_variant_attributes_price_extra = [
                ptav.price_extra for ptav in combination.filtered(
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
            no_variant_attributes_price_extra_advanced = combination.filtered(lambda ptav:
                ptav not in product.product_template_attribute_value_ids
            )
            if no_variant_attributes_price_extra_advanced:
                product = product.with_context(
                    no_variant_attributes_price_extra_advanced=no_variant_attributes_price_extra_advanced
                )
             # invasion end
            list_price = product.price_compute('list_price')[product.id]
            price = product.price if pricelist else list_price
        else:
            # invasion start
            product_template = product_template.with_context(
                current_attributes_price_extra=[v.price_extra or 0.0 for v in combination],
                current_attributes_price_extra_advanced=combination,
            )
            # invasion end
            list_price = product_template.price_compute('list_price')[product_template.id]
            price = product_template.price if pricelist else list_price

        filtered_combination = combination._without_no_variant_attributes()
        if filtered_combination:
            display_name = '%s (%s)' % (display_name, ', '.join(filtered_combination.mapped('name')))

        if pricelist and pricelist.currency_id != product_template.currency_id:
            list_price = product_template.currency_id._convert(
                list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                fields.Date.today()
            )
        price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
        has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount, price) == 1
        return {
            'product_id': product.id,
            'product_template_id': product_template.id,
            'display_name': display_name,
            'price': price,
            'list_price': list_price,
            'has_discounted_price': has_discounted_price,
        }
