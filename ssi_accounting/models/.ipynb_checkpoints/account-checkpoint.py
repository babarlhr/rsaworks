# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class Account(models.Model):
    _inherit = 'account.invoice'
