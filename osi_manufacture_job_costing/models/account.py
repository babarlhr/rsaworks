# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields

class AnalyticAccountLine(models.Model):
    _inherit = 'account.analytic.line'

    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter')

    @api.one
    def _prepare_analytic_line(self):
        result = super(AccountMoveLine, self)._prepare_analytic_line()       
        result[0].update({'workcenter_id': self.workcenter_id.id or False})
        return result


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def action_invoice_open(self):
        result = super(AccountInvoice, self).action_invoice_open()       
        # Generate the Finish Goods to COGS entry for Consumable products
        # Check for SSI/ Redstick workflow here as Repair order vs normal SO
        for inv in self:
            if inv.origin:
                origin_so = self.env['sale.order'].search([('name','=',inv.origin)])
                if origin_so and origin_so.ssi_job_id:
                # if origin_so:
                    inv.action_job_costing_move_create()
        return result

    @api.multi
    def action_job_costing_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            move_line_ids = []
            for line in inv.invoice_line_ids:
                # Check product type and find respective MO to get finish goods costing
                if line.product_id and line.product_id.type == 'consu':
                    # Find the MO related to this product and Job and sum all the rollup cost
                    MO_id = self.env['mrp.production'].search(
                        [('origin','=',inv.origin),
                        ('product_id','=', line.product_id.id)])

                    # Prepare accounts
                    accounts = line.product_id.product_tmpl_id.get_product_accounts()
                    stock_valuation_id = accounts['stock_valuation'].id
                    expense_account_id = accounts['expense'].id
                    if not stock_valuation_id or not expense_account_id:
                        raise UserError(_("Stock valuation or Expense accounts need to be set on the product %s.") % (line.product_id.name,))

                    job_id = MO_id.ssi_job_id or False
                    analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                    total_cost = MO_id.material_cost + MO_id.labor_cost + MO_id.burden_cost
                    # Create Account move line from Finish Goods to COGS account
                    # Finish Goods = Product Valuation Account
                    # COGS Account = Product Expense account
                    # FG
                    move_line_ids.append((0,0,{
                        'name': inv.origin + ' ' + line.name,
                        'product_id': line.product_id.id,
                        'quantity': line.quantity or 1,
                        'account_id': stock_valuation_id,
                        'debit': 0,
                        'credit': total_cost,
                        'partner_id': inv.partner_id.id,
                        'analytic_account_id': line.account_analytic_id.id,
                        'analytic_tag_ids': analytic_tag_ids,
                        'invoice_id': inv.id,
                    }))
                    # COGS
                    move_line_ids.append((0,0,{
                        'name': inv.origin + ' ' + line.name,
                        'product_id': line.product_id.id,
                        'quantity': line.quantity or 1,
                        'account_id': expense_account_id,
                        'credit': 0,
                        'debit': total_cost,
                        'partner_id': inv.partner_id.id,
                        'analytic_account_id': line.account_analytic_id.id,
                        'analytic_tag_ids': analytic_tag_ids,
                        'invoice_id': inv.id,
                    }))
            if move_line_ids:
                # Create Journal entry for job costing
                date = inv.date or inv.date_invoice
                move_vals = {
                    'ref': MO_id.name + ':' + job_id.name +':' + inv.reference,
                    'line_ids': move_line_ids,
                    'journal_id': inv.journal_id.id,
                    'date': date,
                    'narration': inv.comment,
                }
                move = account_move.create(move_vals)
                move.post(invoice = inv)
        return True