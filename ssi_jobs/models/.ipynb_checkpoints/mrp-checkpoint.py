# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from datetime import datetime


class WO(models.Model):
    _inherit = 'mrp.workorder'

    # SHOULD BE RELATED TO JOB IN MANUFACTURING ORDER FROM OLD STUDIo production_id.x_studio_job
    # ssi_job_id = fields.Many2one(
    # 'ssi_jobs', string='Job')
    ssi_job_id = fields.Many2one(
        'ssi_jobs', related='production_id.ssi_job_id', string='Job', store=True)
    duration_expected_hours = fields.Float(
        'Expected Hours',
        compute='_compute_expected_hours',
        readonly=True, store=True,
        help="Expected duration (in hours)")
    duration_hours = fields.Float(
        'Real Hours', compute='_compute_duration_hours',
        readonly=True, store=True)
    job_urgency = fields.Selection(related='ssi_job_id.urgency', string="Urgency", store=True, readonly=True)
    job_deadline = fields.Datetime(related='ssi_job_id.deadline_date', string="Deadline", store=True, readonly=True)
    hide_in_kiosk = fields.Boolean(related='operation_id.hide_in_kiosk', string="Hide in Kiosk", store=True, readonly=True)


    @api.depends('duration_expected')
    def _compute_expected_hours(self):
        for record in self:
            record.duration_expected_hours = record.duration_expected / 60

    @api.depends('duration')
    def _compute_duration_hours(self):
        for record in self:
            record.duration_hours = record.duration / 60

    @api.multi
    def name_get(self):
        return [(wo.id, "%s(%s) %s" % (wo.ssi_job_id.name, wo.production_id.name, wo.name)) for wo in self]
#         return [(wo.id, "%s - %s - %s" % (wo.production_id.name, wo.product_id.name, wo.name)) for wo in self]

    @api.multi
    def button_start(self):
        self.ensure_one()
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True

        # Need a loss in case of the real time exceeding the expected
#         timeline = self.env['mrp.workcenter.productivity']
#         if self.duration < self.duration_expected:
#             loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','productive')], limit=1)
#             if not len(loss_id):
#                 raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
#         else:
#             loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','performance')], limit=1)
#             if not len(loss_id):
#                 raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
#             timeline.create({
#                 'workorder_id': workorder.id,
#                 'workcenter_id': workorder.workcenter_id.id,
#                 'description': _('Time Tracking: ')+self.env.user.name,
#                 'loss_id': loss_id[0].id,
#                 'date_start': datetime.now(),
#                 'user_id': self.env.user.id
#             })
        return self.write({'state': 'progress',
                    'date_start': datetime.now(),
        })
        
    
class WC(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    ssi_job_id = fields.Many2one('ssi_jobs', related='workorder_id.ssi_job_id', string='Job', store=True)
#    ssi_job_id = fields.Many2one(
#        'workorder_id.ssi_job_id', string='Job')
    # ssi_job_id = fields.Many2one(
    #     related='workorder_id.ssi_job_id', relation="ssi_jobs.ssi_jobs", string='Job', domain=[])
    
class Prod(models.Model):
    _inherit = 'mrp.production'

    ssi_job_id = fields.Many2one(
        'ssi_jobs', string='Job')
    
class Prod(models.Model):
    _inherit = 'mrp.routing.workcenter'

    time_cycle_hours = fields.Float(
        'Hour Duration', compute='_compute_cycle_hours',
        help="Time in hours.")
    time_cycle_manual_hours = fields.Float(
        'Manual Hour Duration', compute='_compute_cycle_manual_hours',
        help="Time in hours.")
    hide_in_kiosk = fields.Boolean(default=False, string="Hide in Kiosk")

    @api.depends('time_cycle')
    def _compute_cycle_hours(self):
        for record in self:
            record.time_cycle_hours = record.time_cycle / 60

    @api.depends('time_cycle_manual')
    def _compute_cycle_manual_hours(self):
        for record in self:
            record.time_cycle_manual_hours = record.time_cycle_manual / 60

