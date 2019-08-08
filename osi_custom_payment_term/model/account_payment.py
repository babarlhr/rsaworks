# Copyright 2018 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
    )

    @api.model
    def default_get(self, fields):
        res = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids',
                                                       res.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            res['invoice_id'] = invoice and invoice['id']
        return res

    @api.onchange('amount', 'payment_difference', 'payment_date')
    def onchange_payment_amount(self):
                
        if self.invoice_id \
                and self.invoice_id.payment_term_id \
                and self.invoice_id.payment_term_id.is_discount \
                and self.invoice_id.payment_term_id.line_ids \
                and self.payment_difference:

            self.payment_difference_handling = 'open'
            self.writeoff_account_id = False
            self.writeoff_label = False
                
            for line in self.invoice_id.payment_term_id.line_ids:
                # Check payment date discount validation
                invoice_date = fields.Date.from_string(
                    self.invoice_id.date_invoice)
                till_discount_date = invoice_date + relativedelta(
                    days=line.discount_days)
                payment_date = fields.Date.from_string(self.payment_date)
                if line.discount and payment_date <= till_discount_date:
                    discount_amt = round(
                        (self.invoice_id.amount_total * line.discount) / 100.0,
                         2)
                    
                    # compute payment difference                     
                    payment_difference = self.payment_difference                      
                    if self.invoice_id.type in ('in_invoice','out_refund'):
                        if self.payment_difference < 0:
                            payment_difference = abs(self.payment_difference)
                        # overpayment case -- manual write-off if needed
                        else:
                            payment_difference = discount_amt + 1.0
                    elif self.invoice_id.type in ('out_invoice','in_refund'):
                        if self.payment_difference > 0:
                            payment_difference = self.payment_difference
                        # overpayment case -- manual write-off if needed    
                        else:
                            payment_difference = discount_amt + 1.0
                            
                    # is payment difference applicable for a discount
                    if payment_difference <= discount_amt:
                        self.payment_difference_handling = 'reconcile'
                        self.writeoff_account_id = \
                            line.discount_expense_account_id.id
                        self.writeoff_label = 'Payment Discount' 
                        break;
