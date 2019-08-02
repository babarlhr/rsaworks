# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    status = fields.Selection(string="Status", selection=[(
        'open', 'Open'), ('approved', 'Approved')], default='open', track_visibility='onchange')
    attendance_lines = fields.One2many('hr.attendance.line', 'attendance_id', string='Attendance Lines', copy=True)


    @api.one
    def approve_attendance(self):
        data = {
            'workorder_id': self.workorder_id.id,
            'workcenter_id': self.workorder_id.workcenter_id.id,
            'loss_id': 7,
            'user_id': self.employee_id.user_id.id,
            'date_start': self.check_in,
            'date_end': self.check_out,
            # 'x_studio_labor_codes': self.labor_code_id.id
        }
        self.write({
            'status': 'approved'
        })
        self.env['mrp.workcenter.productivity'].sudo().create(data)

class HrAttendanceLine(models.Model):
    _name = "hr.attendance.line"
    _description = "Attendance  Detail"

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True, ondelete='cascade', index=True)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance ID', required=True, ondelete='cascade', index=True, copy=False)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_hours', store=True, readonly=True)
    status = fields.Selection(string="Status", selection=[(
        'open', 'Open'), ('approved', 'Approved')], default='open', track_visibility='onchange')

    job_id = fields.Many2one(
       'ssi_jobs', ondelete='set null', string="Job", index=True)
    workorder_id = fields.Many2one(
       'mrp.workorder', ondelete='set null', string="Work Order", index=True)
#    labor_code_id = fields.Many2one(
#        'x_labor.codes', ondelete='set null', string="Labor Code", index=True)

