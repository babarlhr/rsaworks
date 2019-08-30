# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizWOAdditionLine(models.TransientModel):
    _name = 'wiz.wo.addition.line'
    _description = 'Wizard WO Addition Line'

    is_select = fields.Boolean('Is Select?', default=False)
    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Workorder'
    )
    new_workorder_name = fields.Char('New Workorder Name')
    rework_qty = fields.Float('Rework Qty')
    addition_wizard_id = fields.Many2one('wiz.wo.addition')


class WizWOAddition(models.TransientModel):
    _name = 'wiz.wo.addition'
    _description = 'Wizard WO Addition'

    wo_addition_lines = fields.One2many(
        'wiz.wo.addition.line',
        'addition_wizard_id',
        string='Select Extra Workorder'
    )

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        res = {}
        wo_addition_lines = []
        for mo in self.env['mrp.production'].browse(context.get('active_ids')):
            for wc_line in mo.workorder_ids:
                wo_addition_lines.append(
                    (0, 0,
                     {'workorder_id':wc_line.id,
                      'new_workorder_name':wc_line.name}))
            # Update wizard values
            res.update({
                'wo_addition_lines':wo_addition_lines
            })
        return res
    
    @api.multi
    def add_workorder(self):
        for wa_line in self.wo_addition_lines:
            if wa_line.is_select:
                # Make a copy with Add flag and Replace new name
                default = {'add_consumption': True,
                           'name': wa_line.new_workorder_name or
                                   wa_line.workorder_id.name,
                           'rework_qty': wa_line.rework_qty,
                           'time_ids': [],
                           'qty_producing': wa_line.workorder_id.
                                            production_id.product_qty,
                           'qty_produced': 0.0, 'state': 'pending'}
                wa_line.workorder_id.copy(default)
        return True
