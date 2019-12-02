# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

# FIX TEXT FIELD

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def _default_bank_journal_id(self):
        return self.env['account.journal'].search([('code', '=', 'AMEX')], limit=1)

    bank_journal_id = fields.Many2one('account.journal', string='Bank Journal', states={'done': [('readonly', True)], 'post': [('readonly', True)]}, default=_default_bank_journal_id, help="The payment method used when the expense is paid by the company.")
    merchant = fields.Char(string='Merchant')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', ondelete='restrict', required=True,
        domain="[('customer', '=', 1)]")

