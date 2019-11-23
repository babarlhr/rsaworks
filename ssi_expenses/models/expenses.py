# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

# FIX TEXT FIELD

class ExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    merchant = fields.Char(string='Merchant')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', ondelete='restrict', required=True,
        domain="[('customer', '=', 1)])
