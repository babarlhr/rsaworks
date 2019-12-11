# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class AttendanceReport(models.Model):
    _name = "hr.attendance.report"
    _description = "Attendance Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'employee_id desc, begin_date desc'

#     a_ids = fields.Char('Attendance Ids')
    overtime_group = fields.Char('Overtime Rule', readonly=True)
    overtime_eligible = fields.Char('Overtime Eligible', readonly=True)
    employee_badge = fields.Char('Employee ID', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    department = fields.Many2one('hr.department', 'Department', readonly=True)
    begin_date = fields.Char('Week Start Date', readonly=True)
    week_no = fields.Integer('Week Number', readonly=True)
    shift = fields.Char('Shift', readonly=True)
    start_hours = fields.Integer('Start Hours', readonly=True)
    total_hours = fields.Float('Total Hours', readonly=True)
    hours = fields.Float('Hours Worked', readonly=True)
    straight_time = fields.Float('Straight Pay', compute='_compute_st', readonly=True)
    over_time = fields.Float('Over Time Pay', compute='_compute_ot', readonly=True)
    days_worked = fields.Float('Days Worked', readonly=True)
    double_time = fields.Float('Double Time Pay', compute='_compute_dt', readonly=True)
    pto_time = fields.Float('PTO Hours', readonly=True)
    time_type = fields.Char('Time Type', readonly=True)
    leave_type = fields.Many2one('hr.leave.type', 'PTO Type', readonly=True)

    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        # with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            SELECT
                MIN(a.id) as id,
                o.name as overtime_group,
                c.overtime_eligible as overtime_eligible,
                b.barcode as employee_badge,
                a.employee_id as employee_id,
                b.department_id as department,
                c.name as shift,
                DATE_TRUNC('week', a.check_in) as begin_date,
                EXTRACT('week' from a.check_in) as week_no,
                MIN(o.start_hours) as start_hours,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as total_hours,
                0 as straight_time,
                CASE 
                    WHEN l.time_type is NULL THEN 
                        LEAST(sum(a.worked_hours), start_hours)
                    ELSE 0
                END as hours,
                0 as over_time,
                COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) as days_worked,
                0 as double_time,
                CASE 
                    WHEN l.time_type = 'leave' THEN 
                        SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2))
                    ELSE 0
                END as pto_time,
                l.name as time_type,
                l.id as leave_type
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
                LEFT JOIN hr_leave_type l ON l.id = a.hour_type
            WHERE
                l.time_type = 'leave' or l.time_type is NULL
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours, c.overtime_eligible, time_type, leave_type, overtime_eligible

          UNION
            SELECT
                MIN(a.id) as id,
                o.name as overtime_group,
                c.overtime_eligible as overtime_eligible,
                b.barcode as employee_badge,
                a.employee_id as employee_id,
                b.department_id as department,
                c.name as shift,
                DATE_TRUNC('week', a.check_in) as begin_date,
                EXTRACT('week' from a.check_in) as week_no,
                MIN(o.start_hours) as start_hours,
                0 as hours,
                0 as total_hours,
                0 as straight_time,
                0 as over_time,
                0 as days_worked,
                0 as double_time,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as pto_time,
                l.name as time_type,
                l.id as leave_type
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
                LEFT JOIN hr_leave_type l ON l.id = a.hour_type
            WHERE
                l.time_type = 'other'
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours, c.overtime_eligible, time_type, leave_type, overtime_eligible
          ORDER BY employee_id, week_no
        """
        return select_

    @api.model_cr
    def init(self):
        self._table = 'hr_attendance_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

    def _compute_st(self):
        for record in self:
            if record.overtime_eligible:
                res = self.env['hr.attendance.report'].search([('employee_badge','=',record.employee_badge), ('week_no','=',record.week_no)])
                ot = 0
                st = 0
                dw = 0
                for r in res:
                    if r.leave_type.time_type == 'leave' or not r.leave_type.time_type:
                        st = st + r.hours + r.pto_time
                        dw = dw + r.days_worked
                if st >= record.start_hours and not record.leave_type.time_type:
                    ot = st - r.start_hours
                    record.straight_time = record.hours - ot if (record.hours - ot) > 0 else 0
                else:
                    record.straight_time = record.hours
                
            else:
                record.straight_time = record.hours
                
    def _compute_ot(self):
        for record in self:
            if record.overtime_eligible:
                res = self.env['hr.attendance.report'].search([('employee_badge','=',record.employee_badge), ('week_no','=',record.week_no)])
                ot = 0
                st = 0
                dw = 0
                for r in res:
                    if r.leave_type.time_type == 'leave' or not r.leave_type.time_type:
                        st = st + r.total_hours
                        dw = dw + r.days_worked
                if st >= record.start_hours and dw < 7 and not record.leave_type.time_type:
                    record.over_time = st - r.start_hours if (st - r.start_hours) > 0 else 0
                else:
                    record.over_time = 0
            else:
                record.over_time = 0
                
    def _compute_dt(self):
        for record in self:
            if record.overtime_eligible:
                res = self.env['hr.attendance.report'].search([('employee_badge','=',record.employee_badge), ('week_no','=',record.week_no)])
                ot = 0
                st = 0
                dw = 0
                for r in res:
                    if r.leave_type.time_type == 'leave' or not r.leave_type.time_type:
                        st = st + r.total_hours
                        dw = dw + r.days_worked
                if st >= record.start_hours and dw == 7 and not record.leave_type.time_type:
                    record.double_time = st - r.start_hours
                else:
                    record.double_time = 0
            else:
                record.double_time = 0
                
    @api.multi
    def payroll_export(self):
        return {
            'type' : 'ir.actions.act_url',
            'url': '/csv/download/payroll/%s/attendance/%s'%(self.week_no, self.id),
            'target': 'blank',
        }

    @api.model
    def _csv_download(self,vals):
        week = vals.get('week')
        attendance_id = vals.get('attendance_id')

        attendance = self.env['hr.attendance.report'].search([('week_no','=',week)])

        columns = ['Employee ID', 'Code', 'Type', 'Hours']
        csv = ','.join(columns)
        csv += "\n"

        if len(attendance) > 0:
            for att in attendance:
                emp_id = att.employee_badge if att.employee_badge else ''
                hours = att.hours if att.hours else 0
                overtime = att.over_time if att.over_time else 0
                straight = att.straight_time if att.straight_time else 0
                doubletime = att.double_time if att.double_time else 0
                overtime_group = att.overtime_group if att.overtime_group else 0
                pto = att.pto_time if att.pto_time else 0
                time_type = att.time_type if att.time_type else ''

                # Regular Time or PTO
                if time_type:
                    data = [
                        emp_id,
                        'E',
                        time_type,
                        str(pto),
                    ]
                    csv_row = u'","'.join(data)
                    csv += u"\"{}\"\n".format(csv_row)
                else:
                    data = [
                        emp_id,
                        'E',
                        'REG',
                        str(straight),
                    ]
                    csv_row = u'","'.join(data)
                    csv += u"\"{}\"\n".format(csv_row)

                # Over Time
                if overtime_group == 'Regular Overtime':
                    if att.over_time:
                        data = [
                            emp_id,
                            'E',
                            'OT',
                            str(overtime),
                        ]
                        csv_row = u'","'.join(data)
                        csv += u"\"{}\"\n".format(csv_row)
                        if doubletime:
                            data = [
                                emp_id,
                                'E',
                                'DT',
                                str(doubletime),
                            ]
                            csv_row = u'","'.join(data)
                            csv += u"\"{}\"\n".format(csv_row)
                else:
                    if att.over_time:
                        data = [
                            emp_id,
                            'E',
                            overtime_group,
                            '4',
                        ]
                        csv_row = u'","'.join(data)
                        csv += u"\"{}\"\n".format(csv_row)
                        data = [
                            emp_id,
                            'E',
                            'OT',
                            str(overtime),
                        ]
                        csv_row = u'","'.join(data)
                        csv += u"\"{}\"\n".format(csv_row)
                        if doubletime:
                            data = [
                                emp_id,
                                'E',
                                'DT',
                                str(doubletime),
                            ]
                            csv_row = u'","'.join(data)
                            csv += u"\"{}\"\n".format(csv_row)
                            
                # Update the History File\
                data = {'org_id': att.id,
                        'overtime_group': att.overtime_group,
                        'overtime_eligible': att.overtime_eligible,
                        'employee_badge': att.employee_badge, 
                        'employee_id': att.employee_id.id, 
                        'department': att.department.id,
                        'begin_date': att.begin_date,
                        'week_no': att.week_no,
                        'shift': att.shift,
                        'start_hours': att.start_hours,
                        'total_hours': att.total_hours,
                        'hours': att.hours,
                        'straight_time': att.straight_time,
                        'over_time': att.over_time,
                        'days_worked': att.days_worked,
                        'pto_time': att.pto_time,
                        'time_type': att.time_type,
                        'leave_type': att.leave_type.id,
                        'double_time': att.double_time}
#                 raise UserError(_(data))
                attendanceHist = self.env['hr.attendance.history'].sudo()
                if not attendanceHist.search([('org_id', '=', att.id)]):
                    attendanceHist.sudo().create(data)



        return csv

class AttendanceHistory(models.Model):
    _name = "hr.attendance.history"
    _description = "Attendance History"
    _rec_name = 'employee_id'
    _order = 'employee_id desc, begin_date desc'

#     a_ids = fields.Many2one('hr.attendance',string='Attendance')
    org_id = fields.Integer('Original ID')
    overtime_group = fields.Char('Overtime Rule')
    overtime_eligible = fields.Char('Overtime Eligible')
    employee_badge = fields.Char('Employee ID')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    department = fields.Many2one('hr.department', 'Department')
    begin_date = fields.Char('Week Start Date')
    week_no = fields.Integer('Week Number')
    shift = fields.Char('Shift')
    start_hours = fields.Integer('Start Hours')
    total_hours = fields.Float('Total Hours')
    hours = fields.Float('Hours Worked')
    straight_time = fields.Float('Straight Time')
    over_time = fields.Float('Over Time')
    days_worked = fields.Float('Days Worked')
    double_time = fields.Float('Double Time')
    pto_time = fields.Float('PTO Hours')
    time_type = fields.Char('Time Type')
    leave_type = fields.Many2one('hr.leave.type', 'PTO Type')


