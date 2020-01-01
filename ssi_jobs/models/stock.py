# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    so_job_id = fields.Many2one('ssi_jobs', related='sale_id.ssi_job_id', string='SO Job')
    po_job_id = fields.Many2one('ssi_jobs', related='purchase_id.ssi_job_id', string='PO Job')
    job_stage = fields.Char(compute='_get_job_stage', string='Job Stage', store=True)

    @api.depends('so_job_id', 'po_job_id')
    def _get_job_stage(self):
        for record in self:
            if record.so_job_id:
                record.job_stage = record.so_job_id.stage_id.name
            if record.po_job_id:
                record.job_stage = record.po_job_id.stage_id.name

class StockRule(models.Model):
    _inherit = 'stock.rule'
    
    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        so = self.env['sale.order'].search([('name', '=', origin)])
        if so:
            values['ssi_job_id'] = so.ssi_job_id.id
        Production = self.env['mrp.production']
        ProductionSudo = Production.sudo().with_context(force_company=values['company_id'].id)
        bom = self._get_matching_bom(product_id, values)
        if not bom:
            msg = _('There is no Bill of Material found for the product %s. Please define a Bill of Material for this product.') % (product_id.display_name,)
            raise UserError(msg)

        # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        production = ProductionSudo.create(self._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom))
        origin_production = values.get('move_dest_ids') and values['move_dest_ids'][0].raw_material_production_id or False
        orderpoint = values.get('orderpoint_id')
        if orderpoint:
            production.message_post_with_view('mail.message_origin_link',
                                              values={'self': production, 'origin': orderpoint},
                                              subtype_id=self.env.ref('mail.mt_note').id)
        if origin_production:
            production.message_post_with_view('mail.message_origin_link',
                                              values={'self': production, 'origin': origin_production},
                                              subtype_id=self.env.ref('mail.mt_note').id)
        return True

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        return {
            'origin': origin,
            'product_id': product_id.id,
            'product_qty': product_qty,
            'product_uom_id': product_uom.id,
            'location_src_id': self.location_src_id.id or self.picking_type_id.default_location_src_id.id or location_id.id,
            'location_dest_id': location_id.id,
            'bom_id': bom.id,
            'date_planned_start': fields.Datetime.to_string(self._get_date_planned(product_id, values)),
            'date_planned_finished': values['date_planned'],
            'procurement_group_id': False,
            'propagate': self.propagate,
            'picking_type_id': self.picking_type_id.id or values['warehouse_id'].manu_type_id.id,
            'company_id': values['company_id'].id,
            'move_dest_ids': values.get('move_dest_ids') and [(4, x.id) for x in values['move_dest_ids']] or False,
            'ssi_job_id': values.get('ssi_job_id') or False,
        }
