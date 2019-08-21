# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    status = fields.Selection(string="Status", selection=[(
        'open', 'Open'), ('approved', 'Approved')], default='open', track_visibility='onchange')
    attendance_lines = fields.One2many('hr.attendance.line', 'attendance_id', string='Attendance Lines', copy=True)

    @api.one
    def approve_attendance(self):
        for line in self.attendance_lines:
            data = {
                'workorder_id': line.workorder_id.id,
                'workcenter_id': line.workorder_id.workcenter_id.id,
                'loss_id': 7,
                'user_id': line.employee_id.user_id.id,
                'date_start': line.check_in,
                'date_end': line.check_out,
                # 'x_studio_labor_codes': self.labor_code_id.id
            }
            line.status = 'approved'
            self.env['mrp.workcenter.productivity'].sudo().create(data)
        self.status = 'approved'

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

    @api.depends('check_in', 'check_out')
    def _compute_worked_hours(self):
        for line in self:
            if line.check_out:
                delta = line.check_out - line.check_in
                line.worked_hours = delta.total_seconds() / 3600.0

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

    @api.multi
    def write(self, values):
        """Override default Odoo write function and extend."""
#         raise UserError(_(values))
        # Do your custom logic here
        if self.attendance_id.check_in and self.attendance_id.check_in == self.check_in and 'check_in' in values:
            self.attendance_id.check_in = values['check_in']
        if self.attendance_id.check_out and self.attendance_id.check_out == self.check_out and 'check_out' in values:
            self.attendance_id.check_out = values['check_out']
        # Check for adjustments to other detial lines
#         alo = self.env['hr.attendance.line'].search([('attendance_id', '=', self.attendance_id.id),('check_out', '=', self.check_in)])
#         if alo:
#             alo.check_out = values['check_in']
#         ali = self.env['hr.attendance.line'].search([('attendance_id', '=', self.attendance_id.id),('check_in', '=', self.check_out)])
#         if ali:
#             ali.check_in = values['check_out']
        return super(HrAttendanceLine, self).write(values)