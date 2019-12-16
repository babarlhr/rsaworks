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
    last_invoice_date = fields.Date(string='Last Invoiced Date', compute='_get_last_invoice')
    project_manager = fields.Many2one('res.users', related='partner_id.project_manager_id', string='Project Manager', store=True)

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

    def _get_last_invoice(self):
        Invoice = self.env['account.invoice']
        can_read = Invoice.check_access_rights('read', raise_exception=False)
        for subscription in self:
            current_invoice = Invoice.search([('invoice_line_ids.subscription_id', '=', subscription.id)],order="id desc",limit=1)
            if current_invoice:
                subscription.last_invoice_date = current_invoice.date_invoice
            else:
                subscription.last_invoice_date = 0

    @api.multi
    def ssi_update_lines(self):
        # Update subsctiption lines
        lines = self.recurring_invoice_line_ids
        lines_to_remove = lines.filtered(lambda l: l.product_id.storage_subscription)
#         raise UserError(_(lines_to_remove))
        lines_to_remove.unlink()
        lines = []
        product =  self.env['product.product'].search([('storage_subscription', '=', True)], limit=1)
        for strg in self.storage_id:
            if not strg.last_invoiced:
                last_inv = datetime.date(1, 1, 1)
            else:
                last_inv = strg.last_invoiced
            if not strg.check_out or (strg.check_out.date() > last_inv):
                line_name = '%s (%s)' % (strg.equipment_id.name, strg.equip_serial_no)
                uom =  self.env['uom.uom'].search([('id', '=', strg.subscription_uom.id)], limit=1)
                price = uom.factor_inv * strg.subscription_price
                vals = {
                    "product_id": product.id,
                    "name": line_name,
                    "quantity": strg.equip_square_feet,
                    "price_unit": price
                }
                if strg.subscription_uom:
                    vals.update({"uom_id": strg.subscription_uom})
                lines.append(vals)
        self.update({"recurring_invoice_line_ids": lines})

