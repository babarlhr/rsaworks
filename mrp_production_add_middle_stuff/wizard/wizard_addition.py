from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class WizProductionProductLine(models.TransientModel):
    _name = 'wiz.production.product.line'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_qty = fields.Float(
        'Product Quantity', digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    production_id = fields.Many2one(
        'mrp.production', 'Production Order', 
        default=lambda self: self.env.context.get('active_id', False))

    @api.multi
    def add_product(self):
        move_obj = self.env['stock.move']
        if self.product_qty <= 0:
            raise ValidationError(_('Please provide a positive '
                                    'quantity to add'))
        self.production_id._generate_additional_raw_move(
            self.product_id,
            self.product_qty
        )
        # Check for all draft moves whether they are mto or not
        self.production_id._adjust_procure_method()
        self.production_id.move_raw_ids._action_confirm()
        return True