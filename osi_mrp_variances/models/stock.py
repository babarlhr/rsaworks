# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    add_consumption = fields.Boolean(
        'Additional Consumption',
        help="It enables additional stock move.",
    )

    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock 
        valuation difference due to the processing of the given quant.
        """
        self.ensure_one()
        # Check if additional consumption
        if self.add_consumption:
            cost = self.product_id.standard_price * self.product_qty
            journal_id, acc_src, acc_dest, acc_valuation = \
                self._get_accounting_data_for_valuation()
            accounts = self.product_id.product_tmpl_id.get_product_accounts()
            # Use Material Variance account instead WIP
            acc_src = accounts['material_variance_acc_id'].id
            credit_account_id = acc_valuation
            debit_account_id = acc_src
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)

        # adjust account move line name to show product name
        result=[]
        for item in res:
            item[2]['name'] = self.product_id.name
            result.append(item)
            
        return result

    def _run_valuation(self, quantity=None):
        self.ensure_one()
        value_to_return = 0
        if self._is_in():
            valued_move_lines = self.move_line_ids.filtered(lambda ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
            valued_quantity = 0
            for valued_move_line in valued_move_lines:
                valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)

            # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
            # matter which cost method is set, to ease the switching of cost method.
            vals = {}
            price_unit = self._get_price_unit()
            value = price_unit * (quantity or valued_quantity)
            value_to_return = value if quantity is None or not self.value else self.value
            vals = {
                'price_unit': price_unit,
                'value': value_to_return,
                'remaining_value': value if quantity is None else self.remaining_value + value,
            }
            vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity

            if self.product_id.cost_method == 'standard' and not self.production_id:
                value = self.product_id.standard_price * (quantity or valued_quantity)
                value_to_return = value if quantity is None or not self.value else self.value
                vals.update({
                    'price_unit': self.product_id.standard_price,
                    'value': value_to_return,
                })
            self.write(vals)
        else:
            super()._run_valuation(quantity=quantity)

class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(StockLocation, self).name_search(name, args=args,
                                                     operator=operator,
                                                     limit=limit)
        if 'is_update_location' in self._context:
            new_result = []
            # Suffix Qty with Stock Location name
            move = self.env['stock.move'].browse(self._context.get('move_id'))
            product = move.product_id
            for r in res:
                qty = product.with_context(location=r[0])
                qty = qty._product_available()[product.id]['qty_available']
                new_result.append((r[0],r[1] + ' [%s]'%qty)) 
            return new_result
        return res
