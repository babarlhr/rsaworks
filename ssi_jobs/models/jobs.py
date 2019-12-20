
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import requests


class Jobs(models.Model):
    _name = 'ssi_jobs'
    _description = 'Jobs'
    _order = "create_date,display_name desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    so_ids = fields.One2many(
        'sale.order', 'ssi_job_id', string='SO')
    order_total = fields.Monetary(
        string='Order Total', track_visibility='always', related='so_ids.amount_total')
#     po_count = fields.Integer(string='Purchase Order', compute='_get_po_count')
    po_count = fields.Integer(string='Purchase Order', default=0)
    ai_count = fields.Integer(string='Vendor Bills', compute='_get_ai_count')
    prod_count = fields.Integer(string='Operations', compute='_get_prod_count')
    wo_count = fields.Integer(string='Work Orders', compute='_get_wo_count')
    wc_count = fields.Integer(string='Job Count', compute='_get_wc_count')
    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                  help="Forces all moves for this account to have this account currency.")
    stage_id = fields.Many2one('ssi_jobs_stage', group_expand='_read_group_stage_ids',
                               default=lambda self: self.env['ssi_jobs_stage'].search([('name', '=', 'New Job')]), string='Stage',
                               track_visibility='onchange')
#     name = fields.Char(string="Job Name", required=True, copy=False, readonly=True,
#                        index=True, default=lambda self: _('New'))
    name = fields.Char(string="Job Name", required=True, copy=False, index=True)
    partner_id = fields.Many2one(
        'res.partner', string='Customer', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)])
    user_id = fields.Many2one('res.users', related='partner_id.user_id', string='Salesperson')
    project_manager = fields.Many2one('res.users', related='partner_id.project_manager_id', string='Project Manager', store=True)
    active = fields.Boolean(default=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
#     deadline_date = fields.Datetime(string='Customer Deadline', required=True, default=datetime.today())
    deadline_date = fields.Datetime(string='Customer Deadline')
#     ready_for_pickup = fields.Datetime(string='Ready for Pickup')
    type = fields.Selection(
        [('Shop', 'Shop'), ('Field Service', 'Field Service')], string='Job Type', default='Shop')
    urgency = fields.Selection(
        [('straight', 'Straight time'), ('straight_quote', 'Straight time quote before repair'), ('overtime', 'Overtime'), ('overtime_quote', 'Overtime quote before repair')], string='Urgency')
    po_number = fields.Char(string='PO Number')
    notes = fields.Text(string='Notes')
#     status = fields.Selection(
#         [('ready', 'Ready'), ('process', 'In Process'), ('done', 'Complete'), ('blocked', 'Blocked')], string='Status')
    color = fields.Integer(string='Color')
    serial = fields.Char(String="Serial #")
    aa_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    warranty_claim = fields.Boolean(default=False, string="Warranty Claim")
    warranty_status = fields.Selection(
        [('warranty', 'Warranty'), ('concession', 'Customer Concession'), ('not warrantied', 'Not Warrantied')], 
        string='Warranty Status', track_visibility='onchange')
    hide_in_kiosk = fields.Boolean(default=False, string="Hide in Kiosk")
    completed_on = fields.Datetime(string='Completed On')
    
    _sql_constraints = [(
        'name_unique',
        'unique(name)',
        'This job name already exists in the system!'
    )]

    # ACTIONS AND METHODS
    def _track_subtype(self, init_values):
        # init_values contains the modified fields' values before the changes
        #
        # the applied values can be accessed on the record as they are already
        # in cache
        self.ensure_one()
#         if 'warranty_status' in init_values and self.warranty_status == 'not warrantied':
        if 'warranty_status' in init_values:
            if self.warranty_status != '':
                employees = self.env['hr.employee'].search(
                    [('department_id', '=', 21)])
                followers = []
                for emp in employees:
                    if emp.user_id:
                        followers.append(emp.user_id.partner_id.id)
                # Add Ann Kendrick also
                followers.append(57)
                self.message_subscribe(followers)
            return 'ssi_jobs.job_warranty_change'  # Full external id
        return super(Jobs, self)._track_subtype(init_values)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ssi_job_sequence') or _('New')
        res = super(Jobs, self).create(vals)
        name = res.name
        group = self.env['account.analytic.group'].search(
            [('name', '=', 'Jobs')], limit=1).id
        partner = res.partner_id.id
        aa = self.env['account.analytic.account'].sudo().create(
            {'name': name, 'ssi_job_id': res.id, 'group_id': group, 'partner_id': partner})
        res.write({'aa_id': aa.id})
        
        login_response = requests.post(
            'http://api.springpt.com:38136/api/v1/login',
            headers={'Content-Type': 'application/json'},
            json={"user_name": "RS_API_USER", "password": "b+PHhK2M", "company_id": "RedStick"},
        )
        json_login_response = login_response.json()
        token = json_login_response['data']['token']

        create_qm_job = requests.post(
            'http://api.springpt.com:38136/api/v1/RSImportJob',
            headers={'Content-Type': 'application/json', 'x-access-token': token},
            json= [{
                "JobID" : res.name,
                "CustomerID" : res.partner_id.id,
                "CustomerName" : res.partner_id.name,
                "Notes" : "",
                "Make" : "",
                "Model" : "",
                "SerialNumber" : "",
                "RatingUnit" : res.equipment_id.rating_unit,
                "Poles" : "",
                "RPM" : "",
                "Frame" : "",
                "Enclosure" : "",
                "Voltage" : "",
                "Amps" : "",
                "ODEBearing" : "",
                "DEBearing" : "",
                "CustomerStock" : "",
                "CustomerIDMotor" : "",
                "Phase" : "",
                "Mounting" : "",
                "Duty" : "",
                "NEMADesign" : "",
                "ServiceFactor" : "",
                "Weight" : "",
                "BearingType" : "",
                "StatorWindingType" : "",
                "LubeType": ""
            }]
        )      
        return res
        # raise UserError(_(res.id))

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['ssi_jobs_stage'].search([])
        return stage_ids

    @api.multi  # DONE
    def action_view_estimates(self):
        action = self.env.ref(
            'ssi_jobs.sale_order_estimate_line_action').read()[0]
#        raise UserError(_(action))
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

    @api.multi
    def action_view_po_count(self):
        po_lines = self.env['purchase.order.line'].search([('account_analytic_id', '=', self.aa_id.id)])
        po_ids = []
        for line in po_lines:
            po_ids.append(line.order_id.id)
        action = self.env.ref(
            'ssi_jobs.purchase_order_line_action').read()[0]
        action['domain'] = [('id', 'in', po_ids)]
        return action

    @api.multi
    def action_view_ai_count(self):
        action = self.env.ref(
            'ssi_jobs.sale_order_ai_line_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

    @api.multi
    def action_view_prod_count(self):
        action = self.env.ref(
            'ssi_jobs.sale_order_prod_line_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

    @api.multi
    def action_view_wo_count(self):
        action = self.env.ref(
            'ssi_jobs.sale_order_wo_line_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

    @api.multi
    def action_view_wc_count(self):
        action = self.env.ref(
            'ssi_jobs.sale_order_wc_line_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

#     @api.multi
#     def action_view_aa_count(self):
#         action = self.env.ref(
#             'ssi_jobs.sale_order_aa_line_action').read()[0]
#         action['domain'] = [('ssi_job_id', '=', self.id)]
#         return action

    @api.multi
    def ssi_jobs_new_so_button(self):
        action = self.env.ref(
            'ssi_jobs.ssi_jobs_new_so_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
#         action['domain'] = [('ssi_job_id', '=', self.id),
#                             ('analytic_account_id', '=', self.aa_id)]
        # action['context'] = [('ssi_job_id', '=', self.id), ('aa_id', '=', self.aa_id)]
        return action

    @api.multi
    def ssi_jobs_new_mrp_prod_button(self):
        # raise UserError(_('TEST 1 '))
        action = self.env.ref(
            'ssi_jobs.ssi_jobs_new_prod_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

    @api.multi
    def ssi_jobs_new_po_button(self):
        action = self.env.ref(
            'ssi_jobs.ssi_jobs_new_po_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
        return action

#     @api.depends('order_total')
#     def _get_po_count(self):
#         results = self.env['purchase.order.line'].read_group(
#             domain=[('account_analytic_id', '=', self.aa_id.id)],
#             fields=['account_analytic_id'], groupby=['account_analytic_id']
#         )
#         for res in results:
#             for job in self:
#                 job.po_count = res['account_analytic_id_count']
#         self.po_count = 0

    @api.depends('order_total')
    def _get_ai_count(self):
        results = self.env['account.invoice.line'].sudo().read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.ai_count = dic.get(
                record.id, 0)

    @api.depends('order_total')
    def _get_prod_count(self):
        results = self.env['mrp.production'].sudo().read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.prod_count = dic.get(
                record.id, 0)

    @api.depends('order_total')
    def _get_wo_count(self):
        results = self.env['mrp.workorder'].sudo().read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.wo_count = dic.get(
                record.id, 0)

    @api.depends('order_total')
    def _get_wc_count(self):
        results = self.env['mrp.workcenter.productivity'].sudo().read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.wc_count = dic.get(
                record.id, 0)

    @api.multi
    def write(self, vals):
        # stage change: update date_last_stage_update
        if 'stage_id' in vals: 
            if vals['stage_id'] >= 7 and not self.completed_on:
                vals['completed_on'] = fields.Datetime.now()
            elif vals['stage_id'] < 7: 
                vals['completed_on'] = False
        return super(Jobs, self).write(vals)

#     @api.onchange('stage_id')
#     def _change_complete(self):
#         if self.stage_id.id == 15:
#             self.completed_on = fields.Datetime.now()
#         else:
#             self.completed_on = ''
        
    @api.model
    def run_job_kiosk_scheduler(self):
        # Flip hid flag on kiosk for jobs completed 24 hours ago
        jobs = self.env['ssi_jobs'].search([('stage_id', '>=', 7)])
        for job in jobs:
            delta = fields.Datetime.now()-job.completed_on
            if delta > timedelta(minutes=5):
                job.hide_in_kiosk = True

#     @api.depends('order_total')
#     def _get_aa_count(self):
#         results = self.env['account.analytic.account'].read_group(
#             [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
#         dic = {}
#         for x in results:
#             dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
#         for record in self:
#             record.wc_count = dic.get(
#                 record.id, 0)

    def _get_name(self):
        """ Utility method to allow name_get to be overrided without re-browse the partner """
        partner = self.partner_id
        name = partner.name or ''

#         raise UserError(partner.parent_id)
        if partner.company_name or partner.parent_id:
            if not name and partner.type in ['invoice', 'delivery', 'other']:
                name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
            if not partner.is_company:
#                 raise UserError(partner.parent_id)
                name = "%s, %s" % (partner.commercial_company_name or partner.parent_id.name, name)
        if self._context.get('show_address_only'):
            name = partner._display_address(without_company=True)
        if self._context.get('show_address'):
            name = name + "\n" + partner._display_address(without_company=True)
        name = name.replace('\n\n', '\n')
        name = name.replace('\n\n', '\n')
        if self._context.get('address_inline'):
            name = name.replace('\n', ', ')
        if self._context.get('show_email') and partner.email:
            name = "%s <%s>" % (name, partner.email)
        if self._context.get('html_format'):
            name = name.replace('\n', '<br/>')
        if self._context.get('show_vat') and partner.vat:
            name = "%s ‒ %s" % (name, partner.vat)
        name = "%s ‒ %s" % (self.name, name)
        return name

    @api.multi
    def name_get(self):
        res = []
        for partner in self:
            name = partner._get_name()
            res.append((partner.id, name))
        return res

