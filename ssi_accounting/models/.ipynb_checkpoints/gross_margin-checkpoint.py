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
    filter_unfold_all = True
    filter_partner = True
    filter_analytic = True

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
                    {'name': _('Invoice')},
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
            if isinstance(line_id, int):
                where_clause = 'AND \"account_move_line\".analytic_account_id = %s ' + where_clause
                where_params = [line_id] + where_params
            else:
                where_clause = 'AND am.ref = %s ' + where_clause
                where_params = [line_id] + where_params

            unfold_query = """
                SELECT sum(\"account_move_line\".balance)*-1 AS balance, sum(\"account_move_line\".debit) AS debit, sum(\"account_move_line\".credit) AS credit,
                    \"account_move_line\".analytic_account_id AS aa_id, MIN(\"account_move_line\".id) AS aml_id, pc.profit_center
                    FROM """+tables+"""
                    LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                    LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                    LEFT JOIN account_move am on \"account_move_line\".move_id = am.id
                    LEFT JOIN product_product pp on \"account_move_line\".product_id = pp.id
                    LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                    LEFT JOIN product_category pc on pt.categ_id = pc.id
                    WHERE ac.group_id IN (2, 3) """+where_clause+"""
                    GROUP BY aa_id, pc.profit_center ORDER BY pc.profit_center
            """


        sql_query = """
            SELECT sum(\"account_move_line\".balance)*-1 AS balance, 
                sum(\"account_move_line\".debit) FILTER (WHERE ac.group_id = 3) AS cogs_debit, 
                sum(\"account_move_line\".credit) FILTER (WHERE ac.group_id = 3) AS cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE ac.group_id = 2) AS rev_debit, 
                sum(\"account_move_line\".credit) FILTER (WHERE ac.group_id = 2) AS rev_credit,
                \"account_move_line\".analytic_account_id AS aa_id, 
                p.customer_category, p.id as partner_id, aa.name as job_name,
                p.ref, am.ref as am_ref FROM """+tables+"""
                LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
                LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                LEFT JOIN account_move am on \"account_move_line\".move_id = am.id
                LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                WHERE am.ref IS NOT NULL AND ac.group_id IN (2, 3) """+where_clause+"""
                GROUP BY aa_id, p.ref, p.id, p.customer_category, job_name, am_ref ORDER BY job_name
        """

        params = where_params
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.dictfetchall()

        total_r = 0
        total_c = 0
        total = 0
        count = 0
        line_r = 0
        line_c = 0
        line_b = 0
        for k, line in enumerate(results):
            if not line.get('rev_credit'):
                line['rev_credit'] = 0 
            if not line.get('rev_debit'):
                line['rev_debit'] = 0 
            if not line.get('cogs_credit'):
                line['cogs_credit'] = 0 
            if not line.get('cogs_debit'):
                line['cogs_debit'] = 0 
            total_r += line.get('rev_credit') - line.get('rev_debit', 0)
            total_c += line.get('cogs_debit', 0) - line.get('cogs_credit', 0)
            total += line.get('balance')
            line_r += line.get('rev_credit', 0) - line.get('rev_debit', 0)
            line_c += line.get('cogs_debit', 0) - line.get('cogs_credit', 0)
            line_b += line.get('balance')
            if k+1 < len(results):
                next_job = results[k+1].get('job_name')
            else:
                next_job = ''
            if line.get('job_name') != next_job or not line.get('job_name'):
#             if True:
                ++count
                margin = 0
                if line_r != 0:
                    margin = (line_b/line_r) * 100
                invoice = self.env['account.invoice.line'].search([('account_analytic_id', '=', line.get('aa_id'))], limit=1).invoice_id
                if line.get('job_name'):
                    id = line.get('aa_id')
                    amref = invoice.move_id.name
                else:
                    id = line.get('am_ref')
                    amref = line.get('am_ref')
                browsed_partner = self.env['res.partner'].browse(line.get('partner_id'))
                partner_name = browsed_partner.parent_id.name and str(browsed_partner.parent_id.name) + ', ' + browsed_partner.name or browsed_partner.name
                lines.append({
                        'id': id,
                        'name': line.get('ref'),
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': line_id == id and True or False,
                        'columns': [{'name': partner_name}, 
                                    {'name': invoice.customer_category}, 
                                    {'name': invoice.project_manager.name}, 
                                    {'name': invoice.user_id.name},
                                    {'name': amref},
                                    {'name': line.get('job_name')},
                                    {'name': self.format_value(line_r)},
                                    {'name': self.format_value(line_c)},
                                    {'name': self.format_value(line_b)},
                                    {'name': '{0:.2f}'.format(margin) }],
                })
                line_r = 0
                line_c = 0
                line_b = 0
        # Adding profit center lines
        if line_id:
            self.env.cr.execute(unfold_query, params)
            results = self.env.cr.dictfetchall()
            for child_line in results:
                margin = 0
                if child_line.get('credit') != 0:
                    margin = child_line.get('balance')/child_line.get('credit') * 100
                lines.append({
                        'id': child_line.get('aml_id'),
                        'name': child_line.get('profit_center'),
                        'level': 4,
                        'caret_options': 'account.invoice.out',
                        'parent_id': line_id,
                        'columns': [{'name': v} for v in [
                            '', 
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
                        '', 
                        self.format_value(total_r), 
                        self.format_value(total_c), 
                        self.format_value(total),
                        '{0:.2f}'.format(total/total_r * 100),
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
                sum(\"account_move_line\".debit) FILTER (WHERE ac.group_id = 3) AS cogs_debit, 
                sum(\"account_move_line\".credit) FILTER (WHERE ac.group_id = 3) AS cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE ac.group_id = 2) AS rev_debit, 
                sum(\"account_move_line\".credit) FILTER (WHERE ac.group_id = 2) AS rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Disassembly') as d_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Disassembly' and ac.group_id = 3) as d_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Disassembly' and ac.group_id = 3) as d_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Disassembly' and ac.group_id = 2) as d_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Disassembly' and ac.group_id = 2) as d_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Machine Shop') as m_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Machine Shop' and ac.group_id = 3) as m_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Machine Shop' and ac.group_id = 3) as m_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Machine Shop' and ac.group_id = 2) as m_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Machine Shop' and ac.group_id = 2) as m_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Winding') as w_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Winding' and ac.group_id = 3) as w_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Winding' and ac.group_id = 3) as w_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Winding' and ac.group_id = 2) as w_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Winding' and ac.group_id = 2) as w_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Assembly') as a_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Assembly' and ac.group_id = 3) as a_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Assembly' and ac.group_id = 3) as a_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Assembly' and ac.group_id = 2) as a_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Assembly' and ac.group_id = 2) as a_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Field Services') as f_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Field Services' and ac.group_id = 3) as f_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Field Services' and ac.group_id = 3) as f_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Field Services' and ac.group_id = 2) as f_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Field Services' and ac.group_id = 2) as f_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'New Product Sales') as n_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'New Product Sales' and ac.group_id = 3) as n_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'New Product Sales' and ac.group_id = 3) as n_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'New Product Sales' and ac.group_id = 2) as n_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'New Product Sales' and ac.group_id = 2) as n_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Storage') as s_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Storage' and ac.group_id = 3) as s_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Storage' and ac.group_id = 3) as s_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Storage' and ac.group_id = 2) as s_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Storage' and ac.group_id = 2) as s_rev_credit,
                sum(\"account_move_line\".balance) FILTER (WHERE pc.profit_center = 'Training') as t_bal,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Training' and ac.group_id = 3) as t_cogs_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Training' and ac.group_id = 3) as t_cogs_credit,
                sum(\"account_move_line\".debit) FILTER (WHERE pc.profit_center = 'Training' and ac.group_id = 2) as t_rev_debit,
                sum(\"account_move_line\".credit) FILTER (WHERE pc.profit_center = 'Training' and ac.group_id = 2) as t_rev_credit,
                \"account_move_line\".analytic_account_id AS aa_id, 
                p.customer_category, p.id as partner_id, p.ref, aa.name as job_name, am.ref as am_ref
                FROM """+tables+"""
                LEFT JOIN res_partner p ON \"account_move_line\".partner_id = p.id
                LEFT JOIN account_account ac on \"account_move_line\".account_id = ac.id
                LEFT JOIN account_move am on \"account_move_line\".move_id = am.id
                LEFT JOIN account_analytic_account aa on \"account_move_line\".analytic_account_id = aa.id
                LEFT JOIN product_product pp on \"account_move_line\".product_id = pp.id
                LEFT JOIN product_template pt on pp.product_tmpl_id = pt.id
                LEFT JOIN product_category pc on pt.categ_id = pc.id
                WHERE am.ref IS NOT NULL AND ac.group_id IN (2, 3) """+where_clause+"""
                GROUP BY aa_id, p.id, p.customer_category, p.ref, job_name, am_ref ORDER BY job_name
        """
        params = where_params
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.dictfetchall()

        total_r = 0
        total_c = 0
        total = 0
        d_line_r = 0
        d_line_c = 0
        d_line_b = 0
        m_line_r = 0
        m_line_c = 0
        m_line_b = 0
        w_line_r = 0
        w_line_c = 0
        w_line_b = 0
        a_line_r = 0
        a_line_c = 0
        a_line_b = 0
        f_line_r = 0
        f_line_c = 0
        f_line_b = 0
        n_line_r = 0
        n_line_c = 0
        n_line_b = 0
        s_line_r = 0
        s_line_c = 0
        s_line_b = 0
        t_line_r = 0
        t_line_c = 0
        t_line_b = 0
        line_r = 0
        line_c = 0
        line_b = 0
        count = 0
        for k, line in enumerate(results):
            for i, v in line.items():
                if not v:
                    line[i] = 0
            total_r += line.get('rev_credit', 0) - line.get('rev_debit', 0)
            total_c += line.get('cogs_debit', 0) - line.get('cogs_credit', 0)
            total += line.get('balance')
            d_line_r += line.get('d_rev_credit', 0) - line.get('d_rev_debit', 0)
            d_line_c += line.get('d_cogs_debit', 0) - line.get('d_cogs_credit', 0)
            d_line_b += line.get('d_bal')
            m_line_r += line.get('m_rev_credit', 0) - line.get('m_rev_debit', 0)
            m_line_c += line.get('m_cogs_debit', 0) - line.get('m_cogs_credit', 0)
            m_line_b += line.get('m_bal')
            w_line_r += line.get('w_rev_credit', 0) - line.get('w_rev_debit', 0)
            w_line_c += line.get('w_cogs_debit', 0) - line.get('w_cogs_credit', 0)
            w_line_b += line.get('w_bal')
            a_line_r += line.get('a_rev_credit', 0) - line.get('a_rev_debit', 0)
            a_line_c += line.get('a_cogs_debit', 0) - line.get('a_cogs_credit', 0)
            a_line_b += line.get('a_bal')
            f_line_r += line.get('f_rev_credit', 0) - line.get('f_rev_debit', 0)
            f_line_c += line.get('f_cogs_debit', 0) - line.get('f_cogs_credit', 0)
            f_line_b += line.get('f_bal')
            n_line_r += line.get('n_rev_credit', 0) - line.get('n_rev_debit', 0)
            n_line_c += line.get('n_cogs_debit', 0) - line.get('n_cogs_credit', 0)
            n_line_b += line.get('n_bal')
            s_line_r += line.get('s_rev_credit', 0) - line.get('s_rev_debit', 0)
            s_line_c += line.get('s_cogs_debit', 0) - line.get('s_cogs_credit', 0)
            s_line_b += line.get('s_bal')
            t_line_r += line.get('t_rev_credit', 0) - line.get('t_rev_debit', 0)
            t_line_c += line.get('t_cogs_debit', 0) - line.get('t_cogs_credit', 0)
            t_line_b += line.get('t_bal')
            line_r += line.get('rev_credit', 0) - line.get('rev_debit', 0)
            line_c += line.get('cogs_debit', 0) - line.get('cogs_credit', 0)
            line_b += line.get('balance')
            if k+1 < len(results):
                next_job = results[k+1].get('job_name')
            else:
                next_job = ''
            if line.get('job_name') != next_job or not line.get('job_name'):
                margin = 0
                if line_c != 0:
                    margin = (line_b/line_c) * 100
                if line.get('job_name'):
                    invoice = self.env['account.invoice.line'].search([('account_analytic_id', '=', line.get('aa_id'))], limit=1).invoice_id
                    id = line.get('aa_id')
                    amref = invoice.move_id.name
                else:
                    id = line.get('am_ref')
                    amref = line.get('am_ref')
                    invoice = self.env['account.invoice'].search([('reference', '=', amref)], limit=1)
                browsed_partner = self.env['res.partner'].browse(line.get('partner_id'))
                partner_name = browsed_partner.parent_id.name and str(browsed_partner.parent_id.name) + ', ' + browsed_partner.name or browsed_partner.name
                lines.append({
                        'id': line.get('aa_id'),
                        'name': line.get('ref'),
                        'level': 2,
                        'unfoldable': True,
                        'unfolded': line_id == line.get('aa_id') and True or False,
                        'columns': [{'name': partner_name}, 
                                    {'name': invoice.customer_category}, 
                                    {'name': invoice.project_manager.name}, 
                                    {'name': invoice.user_id.name},
                                    {'name': line.get('job_name')},
                                    {'name': invoice.origin},
                                    {'name': invoice.move_id.name},
                                    {'name': invoice.date_invoice},
                                    {'name': d_line_r},
                                    {'name': d_line_c},
                                    {'name': d_line_b},
                                    {'name': ''},
                                    {'name': m_line_r},
                                    {'name': m_line_c},
                                    {'name': m_line_b},
                                    {'name': ''},
                                    {'name': w_line_r},
                                    {'name': w_line_c},
                                    {'name': w_line_b},
                                    {'name': ''},
                                    {'name': a_line_r},
                                    {'name': a_line_c},
                                    {'name': a_line_b},
                                    {'name': ''},
                                    {'name': f_line_r},
                                    {'name': f_line_c},
                                    {'name': f_line_b},
                                    {'name': ''},
                                    {'name': n_line_r},
                                    {'name': n_line_c},
                                    {'name': n_line_b},
                                    {'name': ''},
                                    {'name': s_line_r},
                                    {'name': s_line_c},
                                    {'name': s_line_b},
                                    {'name': ''},
                                    {'name': t_line_r},
                                    {'name': t_line_c},
                                    {'name': t_line_b},
                                    {'name': ''},
                                    {'name': line_r},
                                    {'name': line_c},
                                    {'name': line_b},
                                    {'name': '{0:.2f}'.format(margin) }],
                })
                d_line_r = 0
                d_line_c = 0
                d_line_b = 0
                m_line_r = 0
                m_line_c = 0
                m_line_b = 0
                w_line_r = 0
                w_line_c = 0
                w_line_b = 0
                a_line_r = 0
                a_line_c = 0
                a_line_b = 0
                f_line_r = 0
                f_line_c = 0
                f_line_b = 0
                n_line_r = 0
                n_line_c = 0
                n_line_b = 0
                s_line_r = 0
                s_line_c = 0
                s_line_b = 0
                t_line_r = 0
                t_line_c = 0
                t_line_b = 0
                line_r = 0
                line_c = 0
                line_b = 0
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
                        self.format_value(total_r), 
                        self.format_value(total_c), 
                        self.format_value(total),
                        '{0:.2f}'.format(total/total_r * 100),
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

