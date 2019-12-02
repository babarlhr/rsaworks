# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import clean_action


class ReportGrossMargin(models.AbstractModel):
    _name = "account.report.gross.margin"
    _description = "Gross Margin Report"
    _inherit = 'account.report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_all_entries = False

    def _get_columns_name(self, options):
        return [{'name': _('Internal Ref')},
                {'name': _('Customer')},
                {'name': _('Customer Cat')},
                {'name': _('Project Manager')},
                {'name': _('Account Manager')},
                {'name': _('Job')},
                {'name': _('Revenue'), 'class': 'number'},
                {'name': _('COGS'), 'class': 'number'},
                {'name': _('GM $$'), 'class': 'number'},
                {'name': _('GM %'), 'class': 'number'}]

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=True)._query_get()
#         user_type_id = self.env['account.account.type'].search([('type', '=', 'receivable')])
        if where_clause:
            where_clause = 'AND ' + where_clause
        # When unfolding, only fetch sum for the job we are unfolding and
        # fetch all partners for that country
        if line_id != None:
            where_clause = 'AND \"account_move_line\".analytic_account_id = %s ' + where_clause
            where_params = [line_id] + where_params
#             unfold_query = """
#                 SELECT sum(\"account_move_line\".balance) AS balance, p.name, p.id, c.id AS country_id FROM """+tables+"""
#                     LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
#                     LEFT JOIN res_country c on p.country_id = c.id
#                     WHERE \"account_move_line\".invoice_id IS NOT NULL AND \"account_move_line\".user_type_id = %s """+where_clause+"""
#                     GROUP BY p.name, p.id, c.id ORDER BY p.name
#             """
            unfold_query = """
                SELECT sum(\"account_move_line\".balance)*-1 AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
                    \"account_move_line\".analytic_account_id AS aa_id, pc.profit_center
                    FROM """+tables+"""
                    LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                    LEFT JOIN product_product pp on \"account_move_line\".product_id = pp.id
                    LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                    LEFT JOIN product_category pc on pt.categ_id = pc.id
                    WHERE \"account_move_line\".analytic_account_id IS NOT NULL AND \"account_move_line\".user_type_id IN (14, 16) """+where_clause+"""
                    GROUP BY aa_id, pc.profit_center ORDER BY pc.profit_center
            """


#     def _select(self):
#         select_str = """
# 				SELECT DISTINCT aml.id AS id, aml.name AS name, aml.quantity as quantity, aml.product_uom_id as product_uom_id, aml.product_id AS product_id, 
#                     aml.debit AS debit, aml.credit AS credit, aml.balance AS balance, aml.amount_currency AS amount_currency,
#                     aml.debit_cash_basis AS debit_cash_basis, aml.credit_cash_basis AS credit_cash_basis, aml.balance_cash_basis AS balance_cash_basis,
#                     aml.company_currency_id AS company_currency_id, aml.currency_id AS currency_id, aml.amount_residual AS amount_residual,
#                     aml.amount_residual_currency AS amount_residual_currency, aml.tax_base_amount AS tax_base_amount, aml.account_id AS account_id,
#                     aml.move_id AS move_id, aml.ref as ref, aml.payment_id AS payment_id, aml.reconciled AS reconciled, aml.full_reconcile_id AS full_reconcile_id, 
#                     aml.journal_id AS journal_id, aml.blocked AS blocked, aml.date_maturity AS date_maturity, aml.date AS date, 
#                     aml.tax_line_id AS tax_line_id, aml.analytic_account_id AS analytic_account_id, aml.company_id AS company_id, 
#                     aml.partner_id AS partner_id, aml.user_type_id AS user_type_id, aml.tax_exigible AS tax_exigible, 
#                     pt.categ_id AS categ_id, rp.user_id AS user_id, rp.project_manager_id AS project_manager, aaa.group_id AS aa_group_id
#         """
#         return select_str

#     def _from(self):
#         from_str = """
#                 FROM account_move_line aml
#                 JOIN account_move am on aml.move_id = am.id
#                 LEFT JOIN account_analytic_account aaa on aml.analytic_account_id = aaa.id
#                 LEFT JOIN product_product pp on aml.product_id = pp.id
#                 LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
#                 LEFT JOIN res_partner rp on aml.partner_id = rp.id
#         """
#         return from_str

#     def _group_by(self):
#         group_by_str = """
#                 GROUP BY aml.id, aml.product_id, aml.account_analytic_id, aml.date
#         """
#         return group_by_str

        sql_query = """
            SELECT sum(\"account_move_line\".balance)*-1 AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
                \"account_move_line\".analytic_account_id AS aa_id, 
                p.customer_category, aa.name as job_name,
                pm.name AS project_manager, am.name AS account_manager FROM """+tables+"""
                LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
                LEFT JOIN res_users pu on p.project_manager_id = pu.id
                LEFT JOIN res_partner pm on pu.partner_id = pm.id
                LEFT JOIN res_users au on p.user_id = au.id
                LEFT JOIN res_partner am on au.partner_id = am.id
                LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                WHERE \"account_move_line\".analytic_account_id IS NOT NULL AND \"account_move_line\".user_type_id IN (14, 16) """+where_clause+"""
                GROUP BY aa_id, pm.name, am.name, p.customer_category, job_name ORDER BY job_name
        """
#         sql_query = """
#             SELECT sum(\"account_move_line\".balance) AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
#                 \"account_move_line\".analytic_account_id AS aa_id, 
#                 p.name, p.ref, p.customer_category, aa.name as job_name,
#                 pm.name AS project_manager, am.name AS account_manager FROM """+tables+"""
#                 LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
#                 LEFT JOIN res_partner pm on p.project_manager_id = pm.id
#                 LEFT JOIN res_partner am on p.user_id = am.id
#                 LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
#                 WHERE \"account_move_line\".analytic_account_id IS NOT NULL AND \"account_move_line\".user_type_id IN (14, 16) """+where_clause+"""
#                 GROUP BY aa_id, p.name, p.ref, pm.name, am.name, p.customer_category, job_name ORDER BY job_name
#         """
        params = where_params
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.dictfetchall()

        total_c = 0
        total_d = 0
        total = 0
        count = 0
        for line in results:
            total_c += line.get('credit')
            total_d += line.get('debit')
            total += line.get('balance')
            ++count
#             raise UserError(_(line))
            lines.append({
                    'id': line.get('aa_id'),
                    'name': line.get('ref'),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': line_id == line.get('aa_id') and True or False,
                    'columns': [{'name': line.get('job_name')}, 
                                {'name': line.get('customer_category')}, 
                                {'name': line.get('project_manager')}, 
                                {'name': line.get('account_manager')},
                                {'name': line.get('job_name')},
                                {'name': self.format_value(line.get('credit'))},
                                {'name': self.format_value(line.get('debit'))},
                                {'name': self.format_value(line.get('balance'))},
                                {'name': '{0:.2f}'.format(line.get('balance')/line.get('credit') * 100) }],
                })
        # Adding profit center lines
        if line_id:
            self.env.cr.execute(unfold_query, params)
            results = self.env.cr.dictfetchall()
            for child_line in results:
                lines.append({
                        'id': '%s_%s' % (child_line.get('id'), child_line.get('name')),
                        'name': child_line.get('profit_center'),
                        'level': 4,
                        'caret_options': 'invoice',
                        'parent_id': line_id,
                        'columns': [{'name': v} for v in [
                            '', 
                            '', 
                            '', 
                            '', 
                            '', 
                            self.format_value(child_line.get('credit')), 
                            self.format_value(child_line.get('debit')), 
                            self.format_value(child_line.get('balance')),
                            '{0:.2f}'.format(child_line.get('balance')/child_line.get('credit') * 100)
                        ]],
                    })
            # Sum of all the partner lines
            lines.append({
                    'id': 'total_%s' % (line_id,),
                    'class': 'o_account_reports_domain_total',
                    'name': _('Total '),
                    'parent_id': line_id,
                    'columns': [{'name': v} for v in ['', '', '', '', '', '', '', child_line.get('total')]],
                })

        # Don't display level 0 total line in case we are unfolding
        if total and not line_id:
            lines.append({
                'id': 'total',
                'name': _('Total'),
                'level': 0,
                'class': 'total',
                'columns': [{'name': v} for v in [
                        '', 
                        '',
                        '', 
                        '', 
                        '', 
                        self.format_value(total_c), 
                        self.format_value(total_d), 
                        self.format_value(total),
                        '{0:.2f}'.format(total/total_c * 100),
                    ]],
                })
#             raise UserError(_(lines))
        return lines

    def _get_report_name(self):
        return _('Gross Margin SSI')

    def _get_templates(self):
        templates = super(ReportGrossMargin, self)._get_templates()
        templates['main_template'] = 'ssi_accounting.template_gross_margin_report'
        templates['line_template'] = 'ssi_accounting.line_template_gross_margin_report'
        return templates

    def open_invoices(self, options, params):
        partner_id = int(params.get('id').split('_')[0])
        [action] = self.env.ref('account.action_invoice_tree1').read()
        action['context'] = self.env.context
        action['domain'] = [
            ('partner_id', '=', partner_id), 
            ('date', '<=', options.get('date').get('date_to')), 
            ('date', '>=', options.get('date').get('date_from'))
        ]
        action = clean_action(action)
        return action