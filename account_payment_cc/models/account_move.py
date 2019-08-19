# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class AccountMove(models.Model):

    _inherit = 'account.move'
    
    posted = fields.Boolean('Posted')

    @api.multi
    def post(self, invoice=False):
        #set variables
        move_line_pool = self.env['account.move.line']
        for move in self:
            result = []
            #check whether journal has Transfer AP to Credit Card Company
            # = checked or not
            if move.journal_id and move.journal_id.\
            support_creditcard_transactions:
                if not move.journal_id.partner_id.property_account_payable_id:
                    raise Warning(_('Payable Account not configured for %s .')\
                                     % move.journal_id.partner_id.name)
                                     
                # are we posting again?
                if not move.posted:
                    proceed = True
                    for line in move.line_ids:
                        if line.partner_id.id == move.journal_id.partner_id.id:
                            proceed = False
                            break
                else:
                    proceed = False
                
                if proceed:                
                    #browse move lines
                    for move_line in move.line_ids:
                        # Update account as per Partner
                        if move_line.account_id.id == move_line.partner_id.property_account_payable_id.id or\
                           move_line.account_id.id != move.journal_id.default_debit_account_id.id: 
                            account = move.journal_id.partner_id.property_account_payable_id and\
                                     move.journal_id.partner_id.property_account_payable_id.id
                        else:
                            account = move_line.account_id and move_line.account_id.id

                        #prepare move line values
                        result.append({
                            'name': move_line.name,
                            'ref': move_line.ref,
                            'partner_id': move.journal_id.partner_id and\
                             move.journal_id.partner_id.id or\
                             move_line.partner_id and move_line.partner_id.id\
                             or False,
                            'journal_id': move_line.journal_id and\
                             move_line.journal_id.id,
    #                         'account_id': move_line.account_id and\
    #                          move_line.account_id.id,
                            'account_id': account,
                            'debit': move_line.credit,
                            'credit': move_line.debit,
                            'date_maturity': move_line.date_maturity,
                            'move_id': move_line.move_id and move_line.move_id.id,
                            'date': move_line.date,
                        })
                    #check result list
                    if result:
                        move.write({'posted': True})
                        #create new move lines
                        for vals in result:
                            move_line_pool.create(vals)
        return super(AccountMove, self).post(invoice=invoice)
