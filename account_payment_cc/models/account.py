# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    support_creditcard_transactions = fields.Boolean(
                            'Transfer AP to Credit Card Company')
    partner_id = fields.Many2one('res.partner', 'Credit Card Company')
    liability_account_id = fields.Many2one('account.account','Liability Account')