# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    project_manager = fields.Many2one('res.users', related='partner_id.project_manager_id', string='Project Manager')

