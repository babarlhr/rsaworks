# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizProductionProductLine(models.TransientModel):
    _inherit = 'wiz.production.product.line'

    workorder_id = fields.Many2one(
        'mrp.workorder',
        string='Workorder'
    )
    uom_id = fields.Many2one(
        'uom.uom',
        string='UoM',
        help='Help to store UoM to avoid re-search of UoM'
    )
    product_uom_id  = fields.Many2one(
        'uom.uom',
        string='UoM',
        readonly='1',
        help='User will see it and not store value',
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            uom_id = self.product_id.uom_id.id
            if self.production_id and self.production_id.bom_id:
                # Search product exists on bom lines
                domain = [('product_id', '=', self.product_id.id),
                          ('bom_id', '=', self.production_id.bom_id.id)]
                bom_line = self.env['mrp.bom.line'].search(domain, limit=1)
                if bom_line:
                    uom_id = bom_line.product_uom_id.id
            self.uom_id = uom_id
            self.product_uom_id = uom_id

    @api.multi
    def add_product(self):
        if self.product_qty <= 0:
            raise ValidationError(_(
                'Please provide a positive quantity to add'))
        required_workorder = False
        workorder_id = False
        if self.production_id.routing_id:
            required_workorder = True
        if required_workorder:
            workorder_ids = self.env['mrp.workorder'].search(
                [('production_id', '=', self.production_id.id),
                 ('state', 'in', ('pending', 'ready', 'progress'))])
            if self.workorder_id:
                workorder_id = self.workorder_id
            elif workorder_ids:
                raise ValidationError(_(
                    'Please select existing workorders'))
            elif not self.workorder_id:
                # Create new workorder
                default = {'add_consumption': True,
                           'name': 'Workorder from Raw materials',
                           'time_ids': [],
                           'qty_producing': self.production_id.product_qty,
                           'qty_produced': 0.0, 'state': 'pending'}
                if not self.production_id.workorder_ids:
                    raise ValidationError(_(
                        "Please create workorder using 'Plan' button!"))
                workorder_id = self.production_id.workorder_ids[0].copy(
                    default)
        self.production_id.with_context(
            selected_workorder_id=workorder_id,
            uom_id=self.uom_id.id)._generate_additional_raw_move(
                self.product_id, self.product_qty)
        # Check for all draft moves whether they are mto or not
        self.production_id._adjust_procure_method()
        self.production_id.move_raw_ids._action_confirm()
        return True
