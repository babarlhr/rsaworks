# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import werkzeug
import json


class attendance(http.Controller):

    @http.route('/update/attendance',
                type='json',
                auth="public",
                methods=['POST'],
                website=True,
                multilang=False,
                csrf=False)
    def updateAttendance(self,  **args):
        input_data = request.httprequest.data
        check_out = json.loads(input_data.decode("utf-8"))['check_out']
        attendanceId = json.loads(input_data.decode("utf-8"))['attendance']
        if attendanceId:
            try:
                attendance = request.env['hr.attendance'].sudo().search(
                    [('id', '=', attendanceId)], limit=1)
                if attendance.check_in[:16] == attendance.check_out[:16]:
                    attendance.sudo().write({'check_out': None})
                data = {'message': check_out, 'attendance': attendance}
            except:
                data = {'message': 'Error'}
            return data
        return {'message': 'No Attendance'}

        # input_data = request.httprequest.data
        # attendanceId = json.loads(input_data.decode("utf-8"))['attendance']
        # job = json.loads(input_data.decode("utf-8"))['job']
        # wo = json.loads(input_data.decode("utf-8"))['wo']
        # lc = json.loads(input_data.decode("utf-8"))['lc']
        # try:
        #     attendance = request.env['hr.attendance'].sudo().search(
        #         [('id', '=', attendanceId)], limit=1)
        #     if attendance:
        #         attendance.sudo().write({'job_id': job})
        #         attendance.sudo().write({'labor_code_id': lc})

        #         wojs = request.env['mrp.workorder'].search_read(
        #             [('ssi_job_id.id', '=', job)])

        #         if wo != '':
        #             attendance.sudo().write({'workorder_id': wo})
        #         else:
        #             attendance.sudo().write({'workorder_id': wojs[0]['id']})

        #     data = {'message': 'success', 'job': job,
        #             'wo': wo, 'lc': lc, 'attendance': attendance, 'wojs': wojs}
        # except:
        #     data = {'message': 'Error'}
        # return data
