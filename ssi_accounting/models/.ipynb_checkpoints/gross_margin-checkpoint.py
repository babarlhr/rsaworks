# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import json
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

    def _get_super_columns(self, options):
        if options.get('custom') == 'jeanne':
            columns = [{'string': _('Disassembly')}]
            columns += [{'string': _('Machine Shop')}]
            columns += [{'string': _('Winding')}]
            columns += [{'string': _('Assembly')}]
            columns += [{'string': _('Field Services')}]
            columns += [{'string': _('New Product Sales')}]
            columns += [{'string': _('Training')}]
            columns += [{'string': _('Storage')}]
            columns += [{'string': _('Total')}]

            return {'columns': columns, 'x_offset': 9, 'merge': 4}

    def _get_columns_name(self, options):
        if options.get('custom') != 'jeanne':
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
        else:
            return [{'name': _('Internal Ref')},
                    {'name': _('Customer')},
                    {'name': _('Customer Cat')},
                    {'name': _('Project Manager')},
                    {'name': _('Account Manager')},
                    {'name': _('Job #')},
                    {'name': _('Sales Order #')},
                    {'name': _('Invoice #')},
                    {'name': _('Invoice Date')},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'},
                    {'name': _('Revenue'), 'class': 'number'},
                    {'name': _('COGS'), 'class': 'number'},
                    {'name': _('GM $$'), 'class': 'number'},
                    {'name': _('GM %'), 'class': 'number'}]

    @api.model
    def _get_lines(self, options, line_id=None):
        if options.get('custom') != 'jeanne':
            return self._get_lines_regular(options, line_id)
        else:
            return self._get_lines_custom(options, line_id)

    @api.model
    def _get_lines_regular(self, options, line_id=None):
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

            unfold_query = """
                SELECT sum(\"account_move_line\".balance)*-1 AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
                    \"account_move_line\".analytic_account_id AS aa_id, pc.profit_center
                    FROM """+tables+"""
                    LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                    LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                    LEFT JOIN product_product pp on \"account_move_line\".product_id = pp.id
                    LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                    LEFT JOIN product_category pc on pt.categ_id = pc.id
                    WHERE \"account_move_line\".analytic_account_id IS NOT NULL 
                    AND ac.group_id IN (2, 3) """+where_clause+"""
                    GROUP BY aa_id, pc.profit_center ORDER BY pc.profit_center
            """


        sql_query = """
            SELECT sum(\"account_move_line\".balance)*-1 AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
                \"account_move_line\".analytic_account_id AS aa_id, 
                p.customer_category, p.name as partner, aa.name as job_name, p.ref
                FROM """+tables+"""
                LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
                LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                WHERE \"account_move_line\".analytic_account_id IS NOT NULL AND ac.group_id IN (2, 3) """+where_clause+"""
                GROUP BY aa_id, p.ref, p.name, p.customer_category, job_name ORDER BY job_name
        """

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
            margin = 0
            if line.get('credit') != 0:
                margin = line.get('balance')/line.get('credit') * 100
            invoice = self.env['account.invoice.line'].search([('account_analytic_id', '=', line.get('aa_id'))], limit=1).invoice_id
            lines.append({
                    'id': line.get('aa_id'),
                    'name': line.get('ref'),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': line_id == line.get('aa_id') and True or False,
                    'columns': [{'name': line.get('partner')}, 
                                {'name': invoice.customer_category}, 
                                {'name': invoice.project_manager.name}, 
                                {'name': invoice.user_id.name},
                                {'name': line.get('job_name')},
                                {'name': self.format_value(line.get('credit'))},
                                {'name': self.format_value(line.get('debit'))},
                                {'name': self.format_value(line.get('balance'))},
                                {'name': '{0:.2f}'.format(margin) }],
                })
        # Adding profit center lines
        if line_id:
            self.env.cr.execute(unfold_query, params)
            results = self.env.cr.dictfetchall()
            for child_line in results:
                margin = 0
                if child_line.get('credit') != 0:
                    margin = child_line.get('balance')/child_line.get('credit') * 100
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
                            '{0:.2f}'.format(margin)
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

    @api.model
    def _get_lines_custom(self, options, line_id=None):
        lines = []
        tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=True)._query_get()
        if where_clause:
            where_clause = 'AND ' + where_clause

        sql_query = """
            SELECT sum(\"account_move_line\".balance)*-1 AS balance, 
                sum(\"account_move_line\".debit) AS debit, 
                sum(\"account_move_line\".credit) AS credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Disassembly') as d_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Disassembly') as d_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Disassembly') as d_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Machine Shop') as m_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Machine Shop') as m_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Machine Shop') as m_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Winding') as w_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Winding') as w_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Winding') as w_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Assembly') as a_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Assembly') as a_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Assembly') as a_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Field Services') as f_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Field Services') as f_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Field Services') as f_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'New Product Sales') as n_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'New Product Sales') as n_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'New Product Sales') as n_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Storage') as s_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Storage') as s_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Storage') as s_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Training') as t_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Training') as t_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Training') as t_credit,
                \"account_move_line\".analytic_account_id AS aa_id, 
                p.customer_category, p.name as partner, p.ref, aa.name as job_name
                FROM """+tables+"""
                LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
                LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                LEFT JOIN product_product pp on \"account_move_line\".product_id = pp.id
                LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                LEFT JOIN product_category pc on pt.categ_id = pc.id
                WHERE \"account_move_line\".analytic_account_id IS NOT NULL AND ac.group_id IN (2, 3) """+where_clause+"""
                GROUP BY aa_id, p.name, p.customer_category, p.ref, job_name ORDER BY job_name
        """
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
            margin = 0
            if line.get('credit') != 0:
                margin = line.get('balance')/line.get('credit') * 100
            invoice = self.env['account.invoice.line'].search([('account_analytic_id', '=', line.get('aa_id'))], limit=1).invoice_id
#             raise UserError(_(invoice.date_invoice))
            lines.append({
                    'id': line.get('aa_id'),
                    'name': line.get('ref'),
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': line_id == line.get('aa_id') and True or False,
                    'columns': [{'name': line.get('partner')}, 
                                {'name': invoice.customer_category}, 
                                {'name': invoice.project_manager.name}, 
                                {'name': invoice.user_id.name},
                                {'name': line.get('job_name')},
                                {'name': invoice.origin},
                                {'name': invoice.move_id.name},
                                {'name': invoice.date_invoice},
                                {'name': (line.get('d_credit')*-1)},
                                {'name': line.get('d_debit')},
                                {'name': line.get('d_bal')},
                                {'name': ''},
                                {'name': line.get('m_credit')},
                                {'name': line.get('m_debit')},
                                {'name': line.get('m_bal')},
                                {'name': ''},
                                {'name': line.get('w_credit')},
                                {'name': line.get('w_debit')},
                                {'name': line.get('w_bal')},
                                {'name': ''},
                                {'name': line.get('a_credit')},
                                {'name': line.get('a_debit')},
                                {'name': line.get('a_bal')},
                                {'name': ''},
                                {'name': line.get('f_credit')},
                                {'name': line.get('f_debit')},
                                {'name': line.get('f_bal')},
                                {'name': ''},
                                {'name': line.get('n_credit')},
                                {'name': line.get('n_debit')},
                                {'name': line.get('n_bal')},
                                {'name': ''},
                                {'name': line.get('s_credit')},
                                {'name': line.get('s_debit')},
                                {'name': line.get('s_bal')},
                                {'name': ''},
                                {'name': line.get('t_credit')},
                                {'name': line.get('t_debit')},
                                {'name': line.get('t_bal')},
                                {'name': ''},
                                {'name': line.get('credit')},
                                {'name': line.get('debit')},
                                {'name': line.get('balance')},
                                {'name': '{0:.2f}'.format(margin) }],
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

    def export_xlsx(self, options):
        options['custom'] ='jeanne'
        return {
                'type': 'ir_actions_account_report_download',
                'data': {'model': self.env.context.get('model'),
                         'options': json.dumps(options),
                         'output_format': 'xlsx',
                         'financial_id': self.env.context.get('id'),
                         }
        }
    
    def _get_reports_buttons(self):
        return [{'name': _('Print Preview'), 'action': 'print_pdf'}, 
                {'name': _('Export (XLSX)'), 'action': 'print_xlsx'}, 
                {'name': _('Jeanne\'s Export'), 'action': 'export_xlsx'}]

