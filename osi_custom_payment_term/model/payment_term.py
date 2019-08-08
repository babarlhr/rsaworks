# Copyright (C) Camptocamp Austria (<http://www.camptocamp.at>)
# Copyright 2018 Open Source Integrators (http://www.opensourceintegrators.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_discount = fields.Boolean(
        string='Early Payment Discount',
        help="Check this box if this payment term has a discount. "
             "If discount is used the remaining amount of the invoice "
             "will not be paid"
    )


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    is_discount = fields.Boolean(related='payment_id.is_discount',
                                 string='Early Payment Discount', readonly=True)
    discount = fields.Float('Discount (%)', digits=(4,2))
    discount_days = fields.Integer('Discount Days')
    discount_income_account_id = fields.Many2one(
        'account.account',
        string='Discount Income Account',
        view_load=True,
        help="This account will be used to post the discount income"
    )
    discount_expense_account_id = fields.Many2one(
        'account.account',
        string='Discount Expense Account',
        view_load=True,
        help="This account will be used to post the discount expense"
    )

    @api.onchange('discount')
    def OnchangeDiscount(self):
        if not self.discount: return {}
        self.value_amount = round(1-(self.discount/100.0),2)
