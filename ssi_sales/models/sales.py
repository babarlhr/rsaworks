# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class Sales(models.Model):
    _inherit = 'sale.order'
