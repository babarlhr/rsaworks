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
#    begin_datetime = fields.Datetime('Begin Date/Time', readonly=True)
#    end_datetime = fields.Datetime('End Date/Time', readonly=True)
    # amount = fields.Float('Amount', default=0, readonly=True)
    # rate = fields.Float('Rate', default=0, readonly=True)
    # rate_code = fields.Char('Rate Code', default="NONE",  readonly=True)
    # cc1 = fields.Float('cc1', default=0, readonly=True)
    # cc2 = fields.Float('cc2', default=0, readonly=True)
    # cc3 = fields.Float('cc3', default=0, readonly=True)
    # cc4 = fields.Float('cc4', default=0, readonly=True)
    # cc5 = fields.Float('cc5', default=0, readonly=True)
    # job_code = fields.Char('Job Code', default="NONE", readonly=True)
    # shift = fields.Char('Shift', default="NONE", readonly=True)
    # wcc = fields.Char('wcc', default="NONE", readonly=True)
    # tcode1 = fields.Char('Tcode1', default="NONE", readonly=True)
    # tcode2 = fields.Char('Tcode2', default="NONE", readonly=True)
    # tcode4 = fields.Char('Tcode4', default="NONE", readonly=True)
    # sequence = fields.Float('Sequence', default=0, readonly=True)
    # check_type = fields.Char('Check Type', default="NONE", readonly=True)
    # check_number = fields.Float('Check Number', default=0, readonly=True)


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
                GREATEST(sum(a.worked_hours)-start_hours, 0) as over_time
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
            WHERE
                o.id = 1
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours
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
                GREATEST(sum(a.worked_hours)-start_hours, 0) as over_time
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
                LEFT JOIN ssi_resource_overtime o ON o.id = c.overtime_rule
            WHERE
                o.id = 2
            GROUP BY
                overtime_group, employee_id, employee_badge, department, shift, begin_date, week_no, start_hours
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
                overtime_group = 'OT' if 'Regular' in att.overtime_group else att.overtime_group

                # Regular Time
                data = [
                    emp_id,
                    'E',
                    'REG',
                    str(hours),
                ]
                csv_row = u'","'.join(data)
                csv += u"\"{}\"\n".format(csv_row)

                # Over Time
                if att.over_time:
                    data = [
                        emp_id,
                        'E',
                        overtime_group,
                        str(overtime),
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
