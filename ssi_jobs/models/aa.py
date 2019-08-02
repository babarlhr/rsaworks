# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class AA(models.Model):
    _inherit = 'account.analytic.account'

    ssi_job_id = fields.Many2one(
        'ssi_jobs', string='Job')
    # so_id = fields.Many2one(
    #     'sale.order', string='Job')
