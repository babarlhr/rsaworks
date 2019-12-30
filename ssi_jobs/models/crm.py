# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_manager = fields.Many2one('res.users', related='partner_id.project_manager_id', string='Project Manager')
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
                if job.stage_id.id < 7:
                    nbr += 1
            lead.job_number = nbr

    @api.depends('ssi_job_ids')
    def _compute_job_id(self):
        for j in self:
            j.ssi_job_id = j.ssi_job_ids[:1].id

#     @api.model
#     def create(self, vals):
#         if vals.get('partner_id'):
#             partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
#             vals['project_manager'] = partner.project_manager.id
#             vals['user_id'] = partner.user_id
#         res = super(AccountInvoice, self).create(vals)

# #       Add Followers
#         followers = []
#         followers.append(partner.user_id)
#         followers.append(partner.project_manager.id)
#         self.message_subscribe(followers)
        
#         return res

