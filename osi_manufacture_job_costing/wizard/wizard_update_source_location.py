# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class UpdateLocation(models.TransientModel):
    _name = 'update.location'
    _description = 'Update Location'

    move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        default=lambda self: self._context.get('active_id', False)
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
    )

    @api.multi
    def update_stock_move_source_location(self):
        for wizard in self:
            move_ids = self.env.context.get('active_ids', False)
            for move in self.env['stock.move'].browse(move_ids):
                move.location_id = wizard.location_id.id
        return {'type': 'ir.actions.act_window_close'}
