# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = 'crm.lead'

    ssi_job_id = fields.Many2one('ssi_jobs', string='Job', compute='_compute_job_id')
    ssi_job_ids = fields.One2many('ssi_jobs', 'opportunity_id', string='Jobs')
    job_deadline = fields.Datetime(related='ssi_job_id.deadline_date', string="Deadline", store=True, readonly=True)
    job_stage = fields.Many2one('ssi_jobs_stage', related='ssi_job_id.stage_id', string="Job Stage", store=True, readonly=True)
    job_number = fields.Integer(compute='_compute_job_total', string="Number of Jobs")
    
    @api.depends('ssi_job_ids')
    def _compute_job_total(self):
        for lead in self:
            nbr = 0
            for job in lead.ssi_job_ids:
                nbr += 1
            lead.job_number = nbr

    @api.depends('ssi_job_ids')
    def _compute_job_id(self):
        for j in self:
            j.ssi_job_id = j.ssi_job_ids[:1].id

#     @api.model
#     def create(self, vals):
#         # set up context used to find the lead's Sales Team which is needed
#         # to correctly set the default stage_id
#         context = dict(self._context or {})
#         if vals.get('type') and not self._context.get('default_type'):
#             context['default_type'] = vals.get('type')
#         if vals.get('team_id') and not self._context.get('default_team_id'):
#             context['default_team_id'] = vals.get('team_id')

#         if vals.get('user_id') and 'date_open' not in vals:
#             vals['date_open'] = fields.Datetime.now()

#         partner_id = vals.get('partner_id') or context.get('default_partner_id')
#         onchange_values = self._onchange_partner_id_values(partner_id)
#         onchange_values.update(vals)  # we don't want to overwrite any existing key
#         vals = onchange_values

#         # context: no_log, because subtype already handle this
#         return super(Lead, self.with_context(context, mail_create_nolog=True)).create(vals)

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
            vals['project_manager'] = partner.project_manager_id.id
            vals['user_id'] = partner.user_id.id
            vals['customer_category'] = partner.customer_category
        res = super(Lead, self).create(vals)

#       Add Followers
        if vals.get('partner_id'):
            followers = []
            followers.append(partner.project_manager_id.partner_id.id)
            followers.append(partner.user_id.partner_id.id)
            res.message_subscribe(followers)
        
        return res

