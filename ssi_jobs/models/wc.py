# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class WC(models.Model):
    _inherit = 'mrp.workcenter.productivity'

    # ssi_job_id = fields.Many2one(
    #     'ssi_jobs', related='workorder_id.ssi_job_id', string='Job')
    # ssi_job_id = fields.Many2one(
    #     'ssi_jobs', string='Job')
    ssi_job_id = fields.Many2one(
        related='workorder_id.ssi_job_id', string='Job')
