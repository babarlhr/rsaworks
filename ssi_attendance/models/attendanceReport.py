# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError


class AttendanceReport(models.Model):
    _name = "hr.attendance.report"
    _description = "Attendance Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'employee_id desc, begin_date desc'

    overtime_group = fields.Char('Overtime Rule', readonly=True)
    employee_badge = fields.Char('Employee ID', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    department = fields.Many2one('hr.department', 'Department', readonly=True)
    begin_date = fields.Char('Week Start Date', readonly=True)
    week_no = fields.Integer('Week Number', readonly=True)
    shift = fields.Char('Shift', readonly=True)
    start_hours = fields.Integer('Start Hours', readonly=True)
    hours = fields.Float('Hours Worked', readonly=True)
    straight_time = fields.Float('Straight Time', readonly=True)
    over_time = fields.Float('Over Time', readonly=True)
    days_worked = fields.Float('Days Worked', readonly=True)
    double_time = fields.Float('Double Time', readonly=True)

    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        # with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            SELECT
                MIN(a.id) as id,
                o.name as overtime_group,
                b.barcode as employee_badge,
                a.employee_id as employee_id,
                b.department_id as department,
                c.name as shift,
                DATE_TRUNC('week', a.check_in) as begin_date,
                EXTRACT('week' from a.check_in) as week_no,
                MIN(o.start_hours) as start_hours,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as hours,
                LEAST(sum(a.worked_hours), start_hours) as straight_time,
                CASE 
                    WHEN c.overtime_eligible AND COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) = 7 THEN 
                        GREATEST(sum(a.worked_hours)-start_hours, 0) - 
                        SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2))
                            FILTER (WHERE EXTRACT('dow' from a.check_in) = 0)
                    ELSE GREATEST(sum(a.worked_hours)-start_hours, 0)
                END as over_time,
                COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) as days_worked,
                CASE 
                    WHEN c.overtime_eligible AND COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) = 7 THEN 
                        SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2))
                        FILTER (WHERE EXTRACT('dow' from a.check_in) = 0)
                    ELSE 0
                END as double_time
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
            WHERE
                o.id = 1
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours, c.overtime_eligible
          UNION
            SELECT
                MIN(a.id) as id,
                o.name as overtime_group,
                b.barcode as employee_badge,
                a.employee_id as employee_id,
                b.department_id as department,
                c.name as shift,
                DATE_TRUNC('week', a.check_in) as begin_date,
                EXTRACT('week' from a.check_in) as week_no,
                MIN(o.start_hours) as start_hours,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as hours,
                LEAST(sum(a.worked_hours), start_hours) as straight_time,
                CASE 
                    WHEN c.overtime_eligible AND COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) = 7 THEN 
                        GREATEST(sum(a.worked_hours)-start_hours, 0) - 
                        SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2))
                            FILTER (WHERE EXTRACT('dow' from a.check_in) = 0)
                    ELSE GREATEST(sum(a.worked_hours)-start_hours, 0)
                END as over_time,
                COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) as days_worked,
                CASE 
                    WHEN c.overtime_eligible AND COUNT(DISTINCT(DATE_TRUNC('day', a.check_in))) = 7 THEN 
                        SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2))
                        FILTER (WHERE EXTRACT('dow' from a.check_in) = 0)
                    ELSE 0
                END as double_time
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
            WHERE
                o.id >= 2
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours, c.overtime_eligible
        """

        return select_

    @api.model_cr
    def init(self):
        self._table = 'hr_attendance_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))

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

                # Regular Time
                data = [
                    emp_id,
                    'E',
                    'REG',
                    str(straight),
                ]
                csv_row = u'","'.join(data)
                csv += u"\"{}\"\n".format(csv_row)

                # Over Time
                if overtime_group == 'Regular':
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

        return csv

#         data = {
#             'workorder_id': self.workorder_id.id,
#             'workcenter_id': self.workorder_id.workcenter_id.id,
#             'loss_id': 7,
#             'user_id': self.employee_id.user_id.id,
#             'date_start': self.check_in,
#             'date_end': self.check_out,
#             # 'x_studio_labor_codes': self.labor_code_id.id
#         }
#         self.write({
#             'status': 'approved'
#         })
#         self.env['mrp.workcenter.productivity'].sudo().create(data)
