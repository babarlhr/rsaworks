
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Jobs(models.Model):
    _name = 'ssi_jobs'
    _description = 'Jobs'
    _order = "create_date,display_name desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # TOP AND RELATED
    so_ids = fields.One2many(
        'sale.order', 'ssi_job_id', string='SO')
    order_total = fields.Monetary(
        string='Order Total', track_visibility='always', related='so_ids.amount_total')
    po_count = fields.Integer(string='Purchase Order', compute='_get_po_count')
    ai_count = fields.Integer(string='Vendor Bills', compute='_get_ai_count')
    prod_count = fields.Integer(string='Operations', compute='_get_prod_count')
    wo_count = fields.Integer(string='Work Orders', compute='_get_wo_count')
    wc_count = fields.Integer(string='Job Count', compute='_get_wc_count')

    # NECESSARY SUPPORT
    currency_id = fields.Many2one('res.currency', string='Account Currency',
                                  help="Forces all moves for this account to have this account currency.")
    stage_id = fields.Many2one('ssi_jobs_stage', group_expand='_read_group_stage_ids',
                               default=lambda self: self.env['ssi_jobs_stage'].search([('name', '=', 'New Job')]), string='Stage')

    # LEFT
    name = fields.Char(string="Job Name", required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one(
        'res.partner', string='Partner', ondelete='restrict', required=True,
        domain=[('parent_id', '=', False)])
    active = fields.Boolean(default=True)
    # objects = fields.Selection(
    #     [('motor', 'Motor'), ('generator', 'Generator'), ('coil', 'Coil'), ('brake', 'Brake'), ('other', 'Other')], string='Object')
    # size = fields.Integer(string='Size')
    # sizeUM = fields.Selection(
    #     [('hp', 'Horsepower'), ('kw', 'Kilowatts'), ('lb-ft', 'Torque')], string='Size UM')
    # shaft = fields.Selection(
    #     [('horizontal', 'Horizontal'), ('vertical', 'Vertical'), ('other', 'Other')], string='Shaft')
    # dimensions = fields.Float(string='Dimensions')
    equipment_id = fields.Many2one(
        'maintenance.equipment', string='Equipment')

    # RIGHT
    ready_for_pickup = fields.Datetime(string='Ready for Pickup')
    urgency = fields.Selection(
        [('straight', 'Straight time'), ('straight_quote', 'Straight time quote before repair'), ('overtime', 'Overtime'), ('overtime_quote', 'Overtime quote before repair')], string='Urgency')
    po_number = fields.Char(string='PO Number')
    # weight = fields.Float(string='Weight')
    # weightUM = fields.Selection(
    #     [('lbs', 'pounds'), ('tons', 'tons'), ('kgs', 'kilograms')], string='Weight UM')
    notes = fields.Text(string='Notes')
    status = fields.Selection(
        [('ready', 'Ready'), ('process', 'In Process'), ('done', 'Complete'), ('blocked', 'Blocked')], string='Status')

    # NAMEPLATES
    # job_type = fields.Selection(
    #     [('10', '10'), ('12', '12'), ('20', '20'), ('30', '30'), ('40', '40'), ('50', '50'), ('60', '60'), ('00', '00'), ('11', '11')], string='Job Type')

    # OTHER
    color = fields.Integer(string='Color')
    serial = fields.Char(String="Serial #")
    aa_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
#     aa_count = fields.Integer(
#         string='Analytics Count', compute='_get_aa_count')

    _sql_constraints = [(
        'name_unique',
        'unique(name)',
        'This job name already exists in the system!'
    )]

    # ACTIONS AND METHODS
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
        action = self.env.ref(
            'ssi_jobs.sale_order_po_line_action').read()[0]
        action['domain'] = [('ssi_job_id', '=', self.id)]
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

    @api.depends('order_total')
    def _get_po_count(self):
        results = self.env['purchase.order'].read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.po_count = dic.get(
                record.id, 0)

    @api.depends('order_total')
    def _get_ai_count(self):
        results = self.env['account.invoice.line'].read_group(
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
        results = self.env['mrp.workorder'].read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.wo_count = dic.get(
                record.id, 0)

    @api.depends('order_total')
    def _get_wc_count(self):
        results = self.env['mrp.workcenter.productivity'].read_group(
            [('ssi_job_id', 'in', self.ids)], 'ssi_job_id', 'ssi_job_id')
        dic = {}
        for x in results:
            dic[x['ssi_job_id'][0]] = x['ssi_job_id_count']
        for record in self:
            record.wc_count = dic.get(
                record.id, 0)

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
