# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class Jobs(models.Model):
    _inherit = "ssi_jobs"

    eq_rating = fields.Float(string='Rating', related='equipment_id.rating')
    eq_rating_unit = fields.Selection(string='Rating Unit', related='equipment_id.rating_unit')

