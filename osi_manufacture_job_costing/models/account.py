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
        # Check for SSI/ Redstick workflow here as Repair order vs normal SO
        for inv in self:
            for line in self.invoice_line_ids:
                if line.ssi_job_id and line.product_id and line.product_id.type == 'consu'\
                    and line.product_id.product_tmpl_id.is_job_type:
                    # Search MO(s) related to given job
                    MO_ids = self.env['mrp.production'].search(
                            [('ssi_job_id', '=', line.ssi_job_id.id),
                            ('wip2cogs_cleared', '=', False)])
                    if MO_ids:
                        # Create WIP TO COGS JE for Labor, Burden and Material
                        MO_ids.create_cogs_entry(job=line.ssi_job_id)
        return result
