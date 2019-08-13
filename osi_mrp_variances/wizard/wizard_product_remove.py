# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizProductRemoveLine(models.TransientModel):
    _name = 'wiz.product.remove.line'
    _description = 'Wizard Product Remove Line'

    is_select = fields.Boolean("Is Select?", default=False)
    move_id = fields.Many2one("stock.move",string="Stock Move")
    product_id = fields.Many2one("product.product",string="Product")
    product_qty = fields.Float("Product Qty")
    remove_wizard_id = fields.Many2one("wiz.product.remove")


class WizProductRemove(models.TransientModel):
    _name = 'wiz.product.remove'
    _description = 'Wizard Product Remove'

    product_remove_lines = fields.One2many(
        'wiz.product.remove.line',
        'remove_wizard_id',
        string='Remove Extra Material'
    )

    @api.model
    def default_get(self, fields):
        res = super(WizProductRemove, self).default_get(fields)
        context = dict(self._context or {})
        product_remove_lines = []
        for mo in self.env['mrp.production'].browse(context.get('active_ids')):
            for ml in mo.move_raw_ids:
                product_remove_lines.append(
                    (0, 0,
                     {'move_id':ml.id,
                      'product_id':ml.product_id.id,
                      'product_qty':ml.product_qty}))
            # Update wizard values
            res.update({
                'product_remove_lines':product_remove_lines
            })
        return res

    @api.multi
    def return_move(self):
        for wiz in self:
            for wa_line in wiz.product_remove_lines:
                if wa_line.is_select:
                    move = wa_line.move_id
                    if wa_line.product_qty <= 0.0:
                        raise ValidationError(_('Please add positive quantity '
                                                'to remove material'))
                    if move.product_qty < wa_line.product_qty:
                        raise ValidationError(_(
                            'Remove material quantity (%s) should not be '
                            'greater than intial quantity (%s).' % (
                                wa_line.product_qty, move.product_qty)))
                    move._do_unreserve()
                    move.write({'state': 'draft'})
                    move.unlink()
        return True
