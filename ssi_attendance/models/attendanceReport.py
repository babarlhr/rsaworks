# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class AttendanceReport(models.Model):
    _name = "hr.attendance.report"
    _description = "Attendance Report"
    _auto = False
    _rec_name = 'employee_id'
    _order = 'employee_id desc, begin_date desc'

    employee_id = fields.Many2one('hr.employee', 'Id', readonly=True)
    det = fields.Char('Det', default="E", readonly=True)
    det_code = fields.Char('Det Code', default="R1", readonly=True)
    hours = fields.Float('Hours', readonly=True)
    begin_datetime = fields.Datetime('Begin Date/Time', readonly=True)
    end_datetime = fields.Datetime('End Date/Time', readonly=True)
    begin_date = fields.Char('Begin Date', readonly=True)
    end_date = fields.Char('End Date', readonly=True)
    overtime = fields.Float('Over Time', readonly=True)
    work_week = fields.Char('Work Week', readonly=True)
#    begin_date = fields.Date('Begin Date', readonly=True)
#    end_date = fields.Date('End Date', readonly=True)
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
                a.employee_id as employee_id,
                c.name as work_week,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as hours,
                DATE_TRUNC('week', a.check_in) as begin_date,
                DATE_TRUNC('week', a.check_out) as end_date,
                'E' as det,
                'REG' as det_code,
                GREATEST(sum(a.worked_hours)-40, 0) as overtime
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
            WHERE
                b.resource_calendar_id = 1
            GROUP BY
                employee_id, work_week, begin_date, end_date
          UNION
            SELECT
                MIN(a.id) as id,
                a.employee_id as employee_id,
                c.name as work_week,
                SUM(ROUND(CAST(a.worked_hours + 0.00 as Decimal), 2)) as hours,
                DATE_TRUNC('week', a.check_in) as begin_date,
                DATE_TRUNC('week', a.check_out) as end_date,
                'E' as det,
                'REG' as det_code,
                GREATEST(sum(a.worked_hours)-6, 0) as overtime
            FROM
                hr_attendance a
                LEFT JOIN hr_employee b ON b.id = a.employee_id
                LEFT JOIN resource_calendar c ON c.id = b.resource_calendar_id
            WHERE
                b.resource_calendar_id = 3
            GROUP BY
                employee_id, work_week, begin_date, end_date
        """

        return select_

    @api.model_cr
    def init(self):
        self._table = 'hr_attendance_report'
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
