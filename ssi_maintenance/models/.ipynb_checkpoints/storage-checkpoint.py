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
            if rec.last_invoiced.month < rec.check_out.date().month:
                diff = rec.check_out.date().month - rec.last_invoiced.month
                if diff == 1:
                    rec.subscription_uom = 30
                elif diff == 2:
                    rec.subscription_uom = 33
                elif diff == 3:
                    rec.subscription_uom = 31
                elif diff == 4:
                    rec.subscription_uom = 37
                elif diff == 5:
                    rec.subscription_uom = 38
                elif diff == 6:
                    rec.subscription_uom = 39
                elif diff == 7:
                    rec.subscription_uom = 40
                elif diff == 8:
                    rec.subscription_uom = 41
                elif diff == 9:
                    rec.subscription_uom = 42
                elif diff == 10:
                    rec.subscription_uom = 43
                elif diff == 11:
                    rec.subscription_uom = 44
                elif diff == 12:
                    rec.subscription_uom = 45
