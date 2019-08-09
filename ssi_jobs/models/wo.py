# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class WO(models.Model):
    _inherit = 'mrp.workorder'

    # SHOULD BE RELATED TO JOB IN MANUFACTURING ORDER FROM OLD STUDIo production_id.x_studio_job
    # ssi_job_id = fields.Many2one(
    # 'ssi_jobs', string='Job')
    ssi_job_id = fields.Many2one(
        'ssi_jobs', related='production_id.ssi_job_id', string='Job', store=True)
