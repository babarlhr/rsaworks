# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from pytz import utc
from collections import defaultdict
import datetime

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
                
                check_in = datetime.datetime(day_date.year, day_date.month, day_date.day, 8, 0, 0)
                check_out_time = 8 + int(work_hours_count)
                check_out = datetime.datetime(day_date.year, day_date.month, day_date.day, check_out_time, 0, 0)
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

