# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime
import requests


class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    remaining_amount = fields.Monetary('Remaining Amount', compute='_compute_remaining',
        help="Amount remaining to spend.")

    @api.multi
    def _compute_remaining(self):
        for line in self:
            line.remaining_amount = float(line.planned_amount - line.practical_amount)

