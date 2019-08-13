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
