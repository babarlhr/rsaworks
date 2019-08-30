# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
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
    last_invoiced = fields.Date(string='Last Invoiced')
    status = fields.Boolean(string='Status')

    def name_get(self):
        res = []
#         name = '%s - %s' % (self.equipment_id.name, self.equip_serial_no)
#         res.append([name])
        name = '%s (%s)' % (self.equipment_id.name, self.equip_serial_no) if self.equip_serial_no else self.equipment_id.name
        res.append((self.id, name))
        return res

