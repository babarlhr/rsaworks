# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class GrossMarginReport(models.Model):
    _name = "gross.margin.report"
    _description = "Gross Margin Report"
    _auto = False
    _rec_name = 'date'

    name = fields.Char(string="Label", readonly=True)
    quantity = fields.Float(digits=dp.get_precision('Product Unit of Measure'),
        help="The optional quantity expressed by this line, eg: number of product sold.", readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    debit = fields.Monetary(default=0.0, currency_field='company_currency_id', readonly=True)
    credit = fields.Monetary(default=0.0, currency_field='company_currency_id', readonly=True)
    balance = fields.Monetary(currency_field='company_currency_id',
        help="Technical field holding the debit - credit in order to open meaningful graph views from reports", readonly=True)
    debit_cash_basis = fields.Monetary(currency_field='company_currency_id', readonly=True)
    credit_cash_basis = fields.Monetary(currency_field='company_currency_id', readonly=True)
    balance_cash_basis = fields.Monetary(currency_field='company_currency_id',
        help="Technical field holding the debit_cash_basis - credit_cash_basis in order to open meaningful graph views from reports", readonly=True)
    amount_currency = fields.Monetary(default=0.0, help="The amount expressed in an optional other currency if it is a multi-currency entry.", readonly=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",
        help='Utility field to express amount currency', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
        help="The optional other currency if it is a multi-currency entry.", readonly=True)
    amount_residual = fields.Monetary(string='Residual Amount', currency_field='company_currency_id',
        help="The residual amount on a journal item expressed in the company currency.", readonly=True)
    amount_residual_currency = fields.Monetary(string='Residual Amount in Currency', readonly=True,
        help="The residual amount on a journal item expressed in its currency (possibly not the company currency).")
    tax_base_amount = fields.Monetary(string="Base Amount", currency_field='company_currency_id', readonly=True)
    account_id = fields.Many2one('account.account', string='Account', readonly=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', help="The move of this entry line.", auto_join=True, readonly=True)
    narration = fields.Text(related='move_id.narration', string='Narration', readonly=True)
    ref = fields.Char(related='move_id.ref', string='Reference', readonly=True)
    payment_id = fields.Many2one('account.payment', string="Originator Payment", help="Payment that created this entry", readonly=True)
#     statement_line_id = fields.Many2one('account.bank.statement.line', index=True, string='Bank statement line reconciled with this entry', readonly=True)
#     statement_id = fields.Many2one('account.bank.statement', related='statement_line_id.statement_id', string='Statement', readonly=True,
#         help="The bank statement used for bank reconciliation", index=True)
    reconciled = fields.Boolean(compute='_amount_residual', readonly=True)
    full_reconcile_id = fields.Many2one('account.full.reconcile', string="Matching Number", readonly=True)
    matched_debit_ids = fields.One2many('account.partial.reconcile', 'credit_move_id', String='Matched Debits',
        help='Debit journal items that are matched with this journal item.', readonly=True)
    matched_credit_ids = fields.One2many('account.partial.reconcile', 'debit_move_id', String='Matched Credits',
        help='Credit journal items that are matched with this journal item.', readonly=True)
    journal_id = fields.Many2one('account.journal', related='move_id.journal_id', string='Journal', index=True, readonly=True)  # related is required
    blocked = fields.Boolean(string='No Follow-up', default=False,
        help="You can check this box to mark this journal item as a litigation with the associated partner", readonly=True)
    date_maturity = fields.Date(string='Due date', readonly=True,
        help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line.")
    date = fields.Date(related='move_id.date', string='Date', index=True, readonly=True)  # related is required
    analytic_line_ids = fields.One2many('account.analytic.line', 'move_id', string='Analytic lines', oldname="analytic_lines", readonly=True)
    tax_ids = fields.Many2many('account.tax', string='Taxes', readonly=True)
    tax_line_id = fields.Many2one('account.tax', string='Originator tax', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True, readonly=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', readonly=True)
    company_id = fields.Many2one('res.company', related='account_id.company_id', string='Company', readonly=True)
#     counterpart = fields.Char("Counterpart", readonly=True, help="Compute the counter part accounts of this journal item for this journal entry. This can be needed in reports.")

    # TODO: put the invoice link and partner_id on the account_move
#     invoice_id = fields.Many2one('account.invoice', oldname="invoice", readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_type_id = fields.Many2one('account.account.type', related='account_id.user_type_id', index=True, store=True, oldname="user_type", readonly=True)
    tax_exigible = fields.Boolean(string='Taxable', readonly=True,
        help="Technical field used to mark a tax line as exigible in the vat report or not (only exigible journal items are displayed). By default all new journal items are directly exigible, but with the feature cash_basis on taxes, some will become exigible only when the payment is recorded.")

    user_id = fields.Many2one('res.users', string='Salesperson', readonly=True)
    project_manager = fields.Many2one('res.users', string='Project Manager', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    profit_center = fields.Char(string='Profit Center', readonly=True)
    customer_cat = fields.Char(string='Customer Category', readonly=True)
    aa_group_id = fields.Many2one('account.analytic.group', string='Analytic Group', readonly=True)

    def _select(self):
        select_str = """
				SELECT DISTINCT aml.id AS id, aml.name AS name, aml.quantity as quantity, aml.product_uom_id as product_uom_id, aml.product_id AS product_id, 
                    aml.debit AS debit, aml.credit AS credit, aml.balance AS balance, aml.amount_currency AS amount_currency,
                    aml.debit_cash_basis AS debit_cash_basis, aml.credit_cash_basis AS credit_cash_basis, aml.balance_cash_basis AS balance_cash_basis,
                    aml.company_currency_id AS company_currency_id, aml.currency_id AS currency_id, aml.amount_residual AS amount_residual,
                    aml.amount_residual_currency AS amount_residual_currency, aml.tax_base_amount AS tax_base_amount, aml.account_id AS account_id,
                    aml.move_id AS move_id, aml.ref as ref, aml.payment_id AS payment_id, aml.reconciled AS reconciled, aml.full_reconcile_id AS full_reconcile_id, 
                    aml.journal_id AS journal_id, aml.blocked AS blocked, aml.date_maturity AS date_maturity, aml.date AS date, 
                    aml.tax_line_id AS tax_line_id, aml.analytic_account_id AS analytic_account_id, aml.company_id AS company_id, 
                    aml.partner_id AS partner_id, aml.user_type_id AS user_type_id, aml.tax_exigible AS tax_exigible, ai.customer_category as customer_cat, 
                    pt.categ_id AS categ_id, pc.profit_center as profit_center, rp.user_id AS user_id, rp.project_manager_id AS project_manager, aaa.group_id AS aa_group_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_move_line aml
                JOIN account_move am on aml.move_id = am.id
                LEFT JOIN account_invoice ai on ai.move_id = am.id
                LEFT JOIN account_analytic_account aaa on aml.analytic_account_id = aaa.id
                LEFT JOIN product_product pp on aml.product_id = pp.id
                LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                LEFT JOIN product_category pc on pt.categ_id = pc.id
                LEFT JOIN res_partner rp on aml.partner_id = rp.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY aml.id, aml.product_id, aml.account_analytic_id, aml.date, profit_center
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s %s WHERE aml.account_id IS NOT NULL AND aml.user_type_id IN (14, 16)
        )""" % (self._table, self._select(), self._from()))

#         self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
#             WITH currency_rate AS (%s)
#             %s
#             FROM (
#                 %s %s WHERE ail.account_id IS NOT NULL %s
#             ) AS sub
#             LEFT JOIN currency_rate cr ON
#                 (cr.currency_id = sub.currency_id AND
#                  cr.company_id = sub.company_id AND
#                  cr.date_start <= COALESCE(sub.date, NOW()) AND
#                  (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
#         )""" % (
#                     self._table, self.env['res.currency']._select_companies_rates(),
#                     self._select(), self._sub_select(), self._from(), self._group_by()))

