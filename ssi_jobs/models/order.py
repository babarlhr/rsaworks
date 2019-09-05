# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class SO(models.Model):
    _inherit = 'sale.order'

    ssi_job_id = fields.Many2one(
        'ssi_jobs', string='Job')
    # aa_id = fields.Many2one(
    #     'account.analytic.account', string='Account Analytic')
    
class PO(models.Model):
    _inherit = 'purchase.order'

    ssi_job_id = fields.Many2one(
        'ssi_jobs', string='Job')
