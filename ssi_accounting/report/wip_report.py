# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class GrossMarginReport(models.Model):
    _name = "wip.report"
    _description = "WIP Report"
    _auto = False
    _rec_name = 'name'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    general_account_id = fields.Many2one('account.account', string='Financial Account', ondelete='restrict', readonly=True)
    move_id = fields.Many2one('account.move.line', string='Journal Item', ondelete='cascade', index=True)
    code = fields.Char(size=8, readonly=True)
    ref = fields.Char(string='Ref.', readonly=True)
    name = fields.Char('Description', readonly=True)
    date = fields.Date('Date', index=True, readonly=True)
    amount = fields.Monetary('Amount', readonly=True)
    unit_amount = fields.Float('Quantity', readonly=True)
    account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_id = fields.Many2one('res.users', string='User', readonly=True)
    tag_ids = fields.Many2many('account.analytic.tag', 'account_analytic_line_tag_rel', 'line_id', 'tag_id', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    group_id = fields.Many2one('account.analytic.group', related='account_id.group_id', readonly=True)
    so_line = fields.Many2one('sale.order.line', string='Sale Order Item', readonly=True)
    workcenter_id = fields.Many2one('mrp.workcenter', string='Workcenter', readonly=True)

    project_manager = fields.Many2one('res.users', string='Project Manager', readonly=True)
    categ_id = fields.Many2one('product.category', string='Product Category', readonly=True)
    profit_center = fields.Char(string='Profit Center', readonly=True)
    customer_cat = fields.Char(string='Customer Category', readonly=True)

    def _select(self):
        select_str = """
				SELECT aal.id AS id, aal.product_uom_id as product_uom_id, aal.product_id AS product_id, aal.general_account_id AS general_account_id, 
                    aal.amount AS amount, aal.unit_amount AS unit_amount, aal.code AS code, aal.workcenter_id AS workcenter_id,
                    aal.currency_id AS currency_id, aal.company_id AS company_id, aal.account_id AS account_id,
                    aal.move_id AS move_id, aal.ref as ref, aal.date AS date, aal.partner_id AS partner_id, aal.user_id AS user_id, 
                    pt.categ_id AS categ_id, pc.profit_center as profit_center, rp.project_manager_id AS project_manager, aal.group_id AS group_id
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_analytic_line aal
                LEFT JOIN product_product pp on aal.product_id = pp.id
                LEFT JOIN product_template pt on pp.product_tmpl_id = pp.id
                LEFT JOIN product_category pc on pt.categ_id = pc.id
                LEFT JOIN res_partner rp on aal.partner_id = rp.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY aml.id, aml.product_id, aml.account_analytic_id, aml.date
        """
        return group_by_str

    @api.model_cr
    def init(self):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
            %s %s WHERE aal.general_account_id  IS NOT NULL
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

