# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import requests


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
#     equip_id = fields.Char(string='Equip_id')
    description = fields.Char(string='Description')
    rating = fields.Float(string='Rating')
    rating_unit = fields.Selection(
        [('HP', 'HP'), ('KW', 'KW'), ('FT-lbs', 'FT-lbs'), ('MW', 'MW')], string='Rating Unit')
    poles = fields.Selection([('2', '2'), ('4', '4'), ('6', '6'), ('8', '8'), ('10', '10'), ('12', '12'), ('14', '14'), ('16', '16'), ('18', '18'), ('20', '20'), ('22', '22'), ('24', '24'), (
        '26', '26'), ('28', '28'), ('30', '30'), ('32', '32'), ('34', '34'), ('36', '36'), ('38', '38'), ('40', '40'), ('42', '42'), ('44', '44'), ('46', '46'), ('48', '48'), ('50', '50')], string='Poles')
    voltage = fields.Selection([('115', '115'), ('230', '230'), ('460', '460'), ('230/460', '230/460'), ('575', '575'), ('660', '660'), ('690', '690'), ('2300', '2300'),
                                ('4160', '4160'), ('2300/4160', '2300/4160'), ('13200', '13200'), ('13800', '13800'), ('4000', '4000'), ('2300/4000', '2300/4000')], string='Voltage')
    enclosure = fields.Selection([('ODP', 'ODP'), ('WPI', 'WPI'), ('WPII', 'WPII'), ('TEFC', 'TEFC'), (
        'TEWAC', 'TEWAC'), ('TEAAC', 'TEAAC'), ('TENV', 'TENV'), ('TEXP', 'TEXP'), ('TEBC', 'TEBC')], string='Enclosure')
    mounting = fields.Selection([('Solid shaft vertical', 'Solid shaft vertical'), ('Horizontal', 'Horizontal'), (
        'C-Flange', 'C-Flange'), ('D-Flange', 'D-Flange'), ('Hollow shaft vertical', 'Hollow shaft vertical')], string='Mounting')
    manufacture = fields.Char(string='Manufacture')
    customer_stock_number = fields.Char(string='Customer Stock#')
    customer_id_number = fields.Char(string='Customer ID#')
    amps = fields.Float(string='Amps')
    rpm_nameplate = fields.Float(string='RPM Nameplate')
    phase = fields.Selection(
        [('Single', 'Single'), ('Three', 'Three'), ('DC', 'DC')], string='Phase')
    frame = fields.Char(string='Frame')
    winding_type = fields.Selection(
        [('Form', 'Form'), ('Random', 'Random')], string='Winding Type')
    bearing_type = fields.Selection([('Anti Friction', 'Anit Friction'), (
        'Sleeve', 'Sleeve'), ('Kingsbury Thrust', 'Kingsbury Thrust'), ('No Bearing', 'No Bearing'), ('Single Bearing', 'Single Bearing')], string='Bearing Type')
    de_bearing = fields.Char(string='DE Bearing')
    ode_bearing = fields.Char(string='ODE Bearing')
    lube_type = fields.Selection([('Grease', 'Grease'), ('Oil Mist', 'Oil Mist'), ('Force Lube', 'Force Lube'), (
        'Wet Sump', 'Wet Sump'), ('Wet sump top/grease bottom', 'Wet sump top/grease bottom')], string='Lube Type')
    weight_in_lbs = fields.Float(string='Weight in LBS')
    duty = fields.Char(string='Duty')
    service_factor = fields.Float(string='Service Factor')
    ul_rating = fields.Char(string='UL Rating')
    nema_design = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], string='Nema Design')
    temp_rise = fields.Char(string='Temp Rise')
    hz = fields.Selection([('60', '60'), ('50', '50')], string='HZ')
    code = fields.Char(string='Code')
    insulation_class = fields.Selection(
        [('A', 'A'), ('B', 'B'), ('F', 'F'), ('H', 'H')], string='Insulation Class')
    direction_of_rotation = fields.Selection([('CW from NDE', 'CW from NDE'), ('CCW from NDE', 'CCW from NDE'), (
        'Bi Directional', 'Bi Directional'), ('Unknown', 'Unknown')], string='Direction of rotation')
    jbox_location = fields.Selection(
        [('F1', 'F1'), ('F2', 'F2'), ('F3', 'F3')], string='J-Box location')
    r_voltage = fields.Float(string='R Voltage ')
    r_amps = fields.Float(string='R Amps')
    excit_type = fields.Char(string='Excit Type')
    field_volts = fields.Float(string='Field Volts')
    field_amps = fields.Float(string='Field Amps')
    f_ohm = fields.Float(string='F Ohm @25C')
    armature_winding_type = fields.Selection(
        [('Form ', 'Form '), ('Random', 'Random')], string='Armature winding type')
    coupling_installed = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Coupling installed')

    length = fields.Float(string='Length')
    additional_length = fields.Float(string='Additional Length')
    width = fields.Float(string='Width')
    additional_width = fields.Float(string='Additional Width')
    square_feet = fields.Float(string='Square Feet')
    weight = fields.Float(string='Weight')
    height = fields.Float(string='Height')
    stock_number = fields.Char(string='Stock Number')

    storage_ids = fields.One2many(
        'storage', 'equipment_id', string='Storages')

    customer_id = fields.Many2one(
        'res.partner', string='Customer', domain="[('customer', '=', 1)]")

    ssi_jobs_count = fields.Integer(
        string='Jobs', compute='_get_ssi_jobs_count')

    customer_id_number_general = fields.Char(string='Customer ID# General')
    customer_id_number_motor_specific = fields.Char(
        string='Customer ID# General Motor Specific')
    ui_rated = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='UI Rated')
    ui_rating = fields.Char(string='UI Rating')

    @api.depends('description')
    def _get_ssi_jobs_count(self):
        results = self.env['ssi_jobs'].read_group(
            [('equipment_id', 'in', self.ids)], 'equipment_id', 'equipment_id')
        dic = {}
        for x in results:
            dic[x['equipment_id'][0]] = x['equipment_id_count']
        for record in self:
            record.ssi_jobs_count = dic.get(
                record.id, 0)

    @api.multi
    def action_ssi_jobs_count_button(self):
        action = self.env.ref(
            'ssi_maintenance.sale_order_equipment_id_line_action').read()[0]

        jobs = self.env['ssi_jobs'].search(
            [('equipment_id', 'in', self.ids)])

        # raise UserError(_(jobs))
        if len(jobs) == 0:
            raise UserError(
                _('There are no jobs assiociated with with this record'))
        elif len(jobs) > 1:
            action['domain'] = [('equipment_id', '=', self.id)]
        else:
            action['views'] = [(self.env.ref('ssi_jobs.jobs_form').id, 'form')]
            action['res_id'] = jobs[0].id

        return action

    @api.multi
    def ssi_equ_qm_button(self):
        # BASIC API REQUEST PYTHON
        # https://realpython.com/python-requests/
        # import requests
        login_response = requests.post(
            'http://api.springpt.com:38136/api/v1/login',
            headers={'Content-Type': 'application/json'},
            json={"user_name": "RS_API_USER", "password": "b+PHhK2M", "company_id": "RedStick"},
        )
        json_login_response = login_response.json()
        token = json_login_response['data']['token']
        nameplate_response = requests.get(
            'http://api.springpt.com:38136/api/v1/RSReturnNamePlate/EM-1000',
            headers={'x-access-token': token}
        )
        nameplate_response_json = nameplate_response.json()
        nameplate_data = nameplate_response_json['data']
#         raise UserError(_(nameplate_data[0]['Equip ID']))
# 
        self.write({
#             'equip_id': nameplate_data[0]['Equip ID'],
            'description': nameplate_data[0]['Description'],
            'manufacture': nameplate_data[0]['Manufacturer'],
            'model': nameplate_data[0]['Model'],
            'serial_no': nameplate_data[0]['Serial Number'],
            'rating': nameplate_data[0]['Rating'],
#             'poles': nameplate_data[0]['Poles'],  #return wront value
#             'enclosure': nameplate_data[0]['Enclosure'],    #return wront value
            'customer_stock_number': nameplate_data[0]['Customer Stock'],
            'mounting': nameplate_data[0]['Mounting'],
#             'id_name': nameplate_data['Customer ID'],
            'amps': nameplate_data[0]['Amps'],
            'rpm_nameplate': nameplate_data[0]['RPM Nameplate'],
            'phase': nameplate_data[0]['Phase'],
            'frame': nameplate_data[0]['Frame'],
            'winding_type': nameplate_data[0]['Winding Type'],
            'bearing_type': nameplate_data[0]['Bearing Type'],
            'de_bearing': nameplate_data[0]['DE Bearing'],
            'ode_bearing': nameplate_data[0]['ODE Bearing'],
            'lube_type': nameplate_data[0]['Lube Type'],
            'weight_in_lbs': nameplate_data[0]['Weight in LBS'],
            'duty': nameplate_data[0]['Duty'],
            'service_factor': nameplate_data[0]['Service Factor'],
            'ul_rating': nameplate_data[0]['UL Rating'],
            'nema_design': nameplate_data[0]['Nema Design'],
            'temp_rise': nameplate_data[0]['Temp Rise'],
            'hz': nameplate_data[0]['HZ'],
#             'insulation_class': nameplate_data[0]['Insulation Class'],    #return wront value
            'direction_of_rotation': nameplate_data[0]['Direction of rotation'],
            'jbox_location': nameplate_data[0]['JBox Location'],
            'r_voltage': nameplate_data[0]['R Voltage'],
            'r_amps': nameplate_data[0]['R Amps'],
            'excit_type': nameplate_data[0]['Excit Type'],
            'field_volts': nameplate_data[0]['Field Volts'],
            'field_amps': nameplate_data[0]['Field Amps'],
            'f_ohm': nameplate_data[0]['F Ohm 25C'],
            'armature_winding_type': nameplate_data[0]['Armature winding type'],
            'coupling_installed': nameplate_data[0]['Couple installed']
        })        
        



class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

#     megger_test_motor = fields.Selection(
#         [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], string='Megger test motor')
    megger_test_motor = fields.Char(string='Megger test motor')
    rotate_the_shaft = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Rotate the shaft')
    check_add_oil = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Check/Add oil')
    verify_location = fields.Selection(
        [('Yes', 'Yes'), ('No', 'No')], string='Verify Location')
    note_problem = fields.Char(string='Note any problems')
