# -*- coding: utf-8 -*-

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from collections import defaultdict
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY

class HrLeaves(models.Model):
    _inherit = 'hr.leave'

    @api.multi
    def _validate_leave_request(self):
        """ Timesheet will be generated on leave validation only if a timesheet_project_id and a
            timesheet_task_id are set on the corresponding leave type. The generated timesheet will
            be attached to this project/task.
        """
        # create the timesheet on the vacation project
        for holiday in self.filtered(
                lambda request: request.holiday_type == 'employee'):

            work_hours_data = holiday.employee_id.list_work_time_per_day(
                fields.Datetime.from_string(holiday.date_from),
                fields.Datetime.from_string(holiday.date_to),
            )
#             raise UserError(_(work_hours_data))
            for index, (day_date, work_hours_count) in enumerate(work_hours_data):
                
                check_in = datetime(day_date.year, day_date.month, day_date.day, 8, 0, 0)
                check_out_time = 8 + int(work_hours_count)
                check_out = datetime(day_date.year, day_date.month, day_date.day, check_out_time, 0, 0)
#                 raise UserError(check_out)
                
                self.env['hr.attendance'].create({
                    'check_in': check_in,
                    'check_out': check_out,
                    'worked_hours': work_hours_count,
                    'employee_id': holiday.employee_id.id,
                    'hour_type': holiday.holiday_status_id.id,
                    'status': 'open',
                })

        return super(HrLeaves, self)._validate_leave_request()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if self.holiday_status_id.name == 'PTO Sell':
                cal = self.env['resource.calendar'].search([('id', '=', 11)], limit=1)
                return employee.get_work_days_data(date_from, date_to, calendar=cal)['days']
            else:
                return employee.get_work_days_data(date_from, date_to)['days']

        today_hours = self.env.user.company_id.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        return self.env.user.company_id.resource_calendar_id.get_work_hours_count(date_from, date_to) / (today_hours or HOURS_PER_DAY)
