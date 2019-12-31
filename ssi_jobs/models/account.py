# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    project_manager = fields.Many2one('res.users', string='Project Manager')
    customer_category = fields.Selection(
        [('Top Account', 'Top Account'), ('Key Account', 'Key Account'), ('Account', 'Account'), ('New Account', 'New Account')], string='Customer Category')

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            if 'SUB' in vals.get('origin'):
                lines = vals.get('invoice_line_ids')
                sub_id = lines[0][2]['subscription_id']
                ss = self.env['sale.subscription'].search([('id', '=', sub_id)])
                vals['project_manager'] = ss.project_manager.id
                vals['customer_category'] = ss.customer_category
            else:
                so = self.env['sale.order'].search([('name', '=', vals.get('origin'))])
                vals['project_manager'] = so.project_manager.id
                vals['customer_category'] = so.customer_category
        res = super(AccountInvoice, self).create(vals)
        return res

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids.filtered(lambda line: line.account_id):
                raise UserError(_('Please add at least one invoice line.'))
            if inv.move_id:
                continue


            if not inv.date_invoice:
                inv.write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.compute_invoice_totals(company_currency, iml)

            name = inv.name or ''
            if inv.payment_term_id:
                totlines = inv.payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency._convert(t[1], inv.currency_id, inv.company_id, inv._get_currency_rate_date() or fields.Date.today())
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            if inv.partner_shipping_id:
                part = inv.partner_shipping_id
            else:
                part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': inv.journal_id.id,
                'date': date,
                'narration': inv.comment,
            }
            move = account_move.create(move_vals)
            # Pass invoice in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.write(vals)
        return True


class AA(models.Model):
    _inherit = 'account.analytic.account'

    ssi_job_id = fields.Many2one(
        'ssi_jobs', string='Job')

class AI(models.Model):
    _inherit = 'account.invoice.line'

    ssi_job_id = fields.Many2one('ssi_jobs', related='account_analytic_id.ssi_job_id', string='Job', store=True)
    rebate_total = fields.Float(compute='_get_rebate_total', string='Rebate Total', digits=dp.get_precision('Product Price'), store=True)

    @api.depends('sale_line_ids')
    def _get_rebate_total(self):
        for line in self:
            amount = 0
            for sl in line.sale_line_ids:
                amount = sl.rebate_amount * sl.product_uom_qty
            line.rebate_total = amount
#                 raise UserError(_(sl.rebate_amount))
#             amount = self.env['product.pricelist.item'].search([('product_id', '=', line.product_id.id), ('pricelist_id', '=', line.order_id.pricelist_id.id)], limit=1).rebate_amount
#             if not amount:
#                 prod_tmpl_id = self.env['product.product'].search([('id', '=', line.product_id.id)]).product_tmpl_id.id
#                 amount = self.env['product.pricelist.item'].search([('product_tmpl_id', '=', prod_tmpl_id), ('pricelist_id', '=', line.order_id.pricelist_id.id)], limit=1).rebate_amount

