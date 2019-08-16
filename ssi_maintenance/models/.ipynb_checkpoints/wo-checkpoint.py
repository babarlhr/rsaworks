from odoo import api, fields, models, tools, _

class WO_maintenance(models.Model):
    _inherit = "mrp.production"
    
    
    
    @api.multi
    def button_maintenance_req(self):
        self.ensure_one()
        return {
            'name': _('New Maintenance Request'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'maintenance.request',
            'type': 'ir.actions.act_window',
            'context': {
                'default_production_id': self.id,
                'default_equipment_id': self.ssi_job_id.equipment_id.id,
                'default_maintenance_team_id': 2,
            },
            'domain': [('production_id', '=', self.id)],
        }

    
