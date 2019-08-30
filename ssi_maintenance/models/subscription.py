# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime
import requests


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'
    
#     equip_id = fields.Char(string='Equip_id')
    storage_id = fields.One2many('storage', 'subscription_id', string='Storage')
    square_foot_total = fields.Float(string='Square Foot Total', compute='_get_sqf_total')

    # ACTIONS AND METHODS
    def recurring_invoice(self):
        self.ssi_update_lines()
        self._recurring_create_invoice()
        current_date = datetime.date.today()
        for strg in self.storage_id:
            strg.last_invoiced = current_date
        
        return self.action_subscription_invoice()

    @api.depends('storage_id')
    def _get_sqf_total(self):
        total = 0
        for record in self:
            for strg in record.storage_id:
                total = total + strg.equip_square_feet
            record.square_foot_total = total


    @api.multi
    def ssi_update_lines(self):
        # Update subsctiption lines
        self.wipe()
        lines = []
        product =  self.env['product.product'].search([('default_code', '=', 'Storage Fee')], limit=1)
        for strg in self.storage_id:
            if not strg.check_out or strg.check_out.date() > strg.last_invoiced:
                line_name = '%s (%s)' % (strg.equipment_id.name, strg.equip_serial_no)
                vals = {
                    "product_id": product.id,
                    "name": line_name,
                    "quantity": strg.equip_square_feet,
                    "price_unit":  strg.subscription_price
                }
                lines.append(vals)
        self.update({"recurring_invoice_line_ids": lines})

