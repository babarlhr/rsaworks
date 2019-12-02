# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class Sales(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def add_nontstock_product(self):
        action = self.env.ref('ssi_nonstock.add_nonstock_product_view').read()[0]
#         action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

