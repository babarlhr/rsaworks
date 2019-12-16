# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp


class Storage(models.Model):
    _name = "storage"
    _description = "Equipment Storage Records"

    name = fields.Char(required=True, default='Storage')
    location_id = fields.Char(string='Location')
    equipment_id = fields.Many2one(
        'maintenance.equipment', string='Equipment')
    subscription_id = fields.Many2one('sale.subscription', string='Subscription')
    check_in = fields.Datetime(string='Check in')
    check_out = fields.Datetime(string='Check out')
    equip_square_feet = fields.Float(string='Square Feet', related='equipment_id.square_feet')
    equip_serial_no = fields.Char(string='Serial Number', related='equipment_id.serial_no')
    subscription_price = fields.Float(string='Subscription Price', digits=dp.get_precision('Product Price'))
    subscription_uom = fields.Many2one('uom.uom', 'Unit of Measure')
    last_invoiced = fields.Date(string='Last Invoiced', related='subscription_id.last_invoice_date', readonly=True)
    customer_id = fields.Many2one('res.partner', string='Customer', related='equipment_id.customer_id', store=True)
    equip_square_feet = fields.Float(string='Square Feet', related='equipment_id.square_feet', readonly=True)
    status = fields.Boolean(string='Status')

    def name_get(self):
        res = []
#         name = '%s - %s' % (self.equipment_id.name, self.equip_serial_no)
#         res.append([name])
        name = '%s (%s)' % (self.equipment_id.name, self.equip_serial_no) if self.equip_serial_no else self.equipment_id.name
        res.append((self.id, name))
        return res

    @api.onchange('check_out')
    def _on_check_out_change(self):
        for rec in self:
            if rec.last_invoiced:
                if rec.check_out:
                    if rec.last_invoiced.month < rec.check_out.date().month:
                        diff = rec.check_out.date().month - rec.last_invoiced.month
                        if diff == 1:
                            rec.subscription_uom = 20
                        elif diff == 2:
                            rec.subscription_uom = 25
                        elif diff == 3:
                            rec.subscription_uom = 21
                        elif diff == 4:
                            rec.subscription_uom = 28
                        elif diff == 5:
                            rec.subscription_uom = 29
                        elif diff == 6:
                            rec.subscription_uom = 30
                        elif diff == 7:
                            rec.subscription_uom = 31
                        elif diff == 8:
                            rec.subscription_uom = 32
                        elif diff == 9:
                            rec.subscription_uom = 33
                        elif diff == 10:
                            rec.subscription_uom = 34
                        elif diff == 11:
                            rec.subscription_uom = 35
                        elif diff == 12:
                            rec.subscription_uom = 36
