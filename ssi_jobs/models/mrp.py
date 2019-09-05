# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class WO(models.Model):
    _inherit = 'mrp.workorder'

    # SHOULD BE RELATED TO JOB IN MANUFACTURING ORDER FROM OLD STUDIo production_id.x_studio_job
    # ssi_job_id = fields.Many2one(
    # 'ssi_jobs', string='Job')
    ssi_job_id = fields.Many2one(
        'ssi_jobs', related='production_id.ssi_job_id', string='Job', store=True)

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