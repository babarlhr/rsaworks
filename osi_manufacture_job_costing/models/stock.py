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
            acc_src = accounts['production_account_id'].id
            credit_account_id = acc_valuation
            debit_account_id = acc_src
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)

        # adjust account move line name to show product name
        result=[]
        production = self.production_id or self.workorder_id.production_id or False
        job_id = self.production_id.ssi_job_id or self.workorder_id.production_id.ssi_job_id or False
        
        for item in res:
            item[2]['name'] = self.product_id.name
            item[2]['partner_id'] = job_id and job_id.partner_id.id or False
            item[2]['analytic_account_id'] = job_id and job_id.aa_id.id or False
            result.append(item)
            
        return result

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move']
        quantity = self.env.context.get('forced_quantity', self.product_qty)
        quantity = quantity if self._is_in() else -1 * quantity

        # Make an informative `ref` on the created account move to differentiate between classic
        # movements, vacuum and edition of past moves.
        ref = self.picking_id.name
        if self.env.context.get('force_valuation_amount'):
            if self.env.context.get('forced_quantity') == 0:
                ref = 'Revaluation of %s (negative inventory)' % ref
            elif self.env.context.get('forced_quantity') is not None:
                ref = 'Correction of %s (modification of past move)' % ref

        move_lines = self.with_context(forced_ref=ref)._prepare_account_move_line(quantity, abs(self.value), credit_account_id, debit_account_id)
        if move_lines:            
            production = self.production_id or self.workorder_id.production_id or False
            job_id = self.production_id.ssi_job_id or self.workorder_id.production_id.ssi_job_id or False
            if job_id and production:
                ref = job_id.name + '-' + production.name
            else:
                ref = False
            partner_id = job_id and job_id.partner_id.id or False
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'stock_move_id': self.id,
            })
            new_account_move.write({'ref': ref,
                'partner_id': partner_id})
            new_account_move.post()
                
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

    def _account_entry_move(self):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.product_id.type == 'product':
            # no stock valuation for consumable products
            return super(StockMove, self)._account_entry_move()
        if self.product_id.type == 'service':
            # no stock valuation for consumable products
            return False
        if self.restrict_partner_id:
            # if the move isn't owned by the company, we don't make any valuation
            return False

        location_from = self.location_id
        location_to = self.location_dest_id
        company_from = self._is_out() and self.mapped('move_line_ids.location_id.company_id') or False
        company_to = self._is_in() and self.mapped('move_line_ids.location_dest_id.company_id') or False

        # Create Journal Entry for products arriving in the company; in case of routes making the link between several
        # warehouse of the same company, the transit location belongs to this company, so we don't need to create accounting entries
        if self._is_in():
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_from and location_from.usage == 'customer':  # goods returned from customer
                self.with_context(force_company=company_to.id)._create_account_move_line(acc_dest, acc_valuation, journal_id)
            else:
                self.with_context(force_company=company_to.id)._create_account_move_line(acc_src, acc_valuation, journal_id)

        # Create Journal Entry for products leaving the company
        if self._is_out():
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if location_to and location_to.usage == 'supplier':  # goods returned to supplier
                self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_src, journal_id)
            else:
                self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_dest, journal_id)

        if self.company_id.anglo_saxon_accounting:
            # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
            journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
            if self._is_dropshipped():
                self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_src, acc_dest, journal_id)
            elif self._is_dropshipped_returned():
                self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_dest, acc_src, journal_id)

        if self.company_id.anglo_saxon_accounting:
            #eventually reconcile together the invoice and valuation accounting entries on the stock interim accounts
            self._get_related_invoices()._anglo_saxon_reconcile_valuation(product=self.product_id)

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
