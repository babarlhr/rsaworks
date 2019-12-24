# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.tools import pycompat

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    _description = 'Bank Accounts'


    _sql_constraints = [
        ('unique_number', 'Check(1=1)', 'Account Number must be unique'),
    ]

    @api.onchange('acc_number')
    def _onchange_acc_number(self):
        """ Warn if the account number already exists. """
        bank_rec = self.env['res.partner.bank'].search([('acc_number', '=', self.acc_number)])
        if bank_rec:
            return {
                'warning': {
                    'title': _('Account Number Duplicate'),
                    'message': _("The account number already exists."
                                 "Please make sure you intend to duplicate it.")
                }
            }

