# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    manufacture = fields.Boolean(string='Manufacture', default=False)
