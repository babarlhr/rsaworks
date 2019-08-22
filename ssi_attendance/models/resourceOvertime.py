from odoo import api, fields, models, _

class ResourceOvertime(models.Model):
    _name = 'ssi_resource.overtime'
    _description = 'Resource Overtime Rules'
    
    name = fields.Char(string='Name')
    start_hours = fields.Integer(string='Overtime Starts at')
    rate = fields.Float(string='Overtime Rate')
                
class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    overtime_rule = fields.Many2one('ssi_resource.overtime', string='Overtime Rules')
    overtime_eligible = fields.Boolean(string='Eligible for Overtime')
