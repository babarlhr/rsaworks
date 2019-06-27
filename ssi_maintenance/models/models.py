# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

# Good start. Couple of things. Make the fields side by side, so 18 or so on the right, the rest  on the left.

# Bearing Type should be Anti, not Anit. DONE

# And work on the required next. I went ahead and created Equipment categories, equivalent of Equip Type. I did the description in required in Studio. Look at the XML it produced to model the rest of them like that.
# I just mocked it up. It shouldn't screw anything up. All you have to do is delete that studio view. I can do it if you aren't sure how,

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
    manufacture = fields.Char(string='Manufacure')
    model_number = fields.Char(string='Model#')
    serial_number = fields.Char(string='Serial#')
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
        'Sleeve', 'Sleeve'), ('Kingsbury Thrust', 'Kingsbury Thrust')], string='Bearing Type')
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