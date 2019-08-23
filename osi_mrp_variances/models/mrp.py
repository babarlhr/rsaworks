# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round, float_compare

class MRPWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    overhead_costs_hour = fields.Float('Overhead Cost per Hour')

class MRPRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    time_cycle_std = fields.Float(
        'Standard Duration',
        help="Time in mins for doing one cycle."
    )
    
    @api.multi
    def _get_wo_std_labor_overhead(self):
        for operation in self:

            wc = operation.workcenter_id
            labor_cost = wc.costs_hour
            ovh_cost = wc.overhead_costs_hour

            cycle_number = float_round(1 / wc.capacity, precision_digits=2, rounding_method='UP')
            duration = float_round((wc.time_start + wc.time_stop + cycle_number * operation.time_cycle_std * (100/wc.time_efficiency)) / 60, precision_digits=2)

            # Calculate valuation_amount
            valuation_amount = duration * labor_cost

            # Calculate Overhead Amount
            overhead_valuation_amount = duration * ovh_cost

            operation.update({
                'std_labor': valuation_amount,
                'std_overhead': overhead_valuation_amount,
            })

    @api.multi
    def _get_wo_real_labor_overhead(self):
        for operation in self:

            wc = operation.workcenter_id
            labor_cost = wc.costs_hour
            ovh_cost = wc.overhead_costs_hour

            cycle_number = float_round(1 / wc.capacity, precision_digits=2, rounding_method='UP')
            duration = float_round(operation.time_cycle, precision_digits=2)

            # Calculate valuation_amount
            valuation_amount = duration * labor_cost

            # Calculate Overhead Amount
            overhead_valuation_amount = duration * ovh_cost

            operation.update({
                'real_labor': valuation_amount,
                'real_overhead': overhead_valuation_amount,
            })
            
    std_labor = fields.Float(
        'Std Labor',
        compute='_get_wo_std_labor_overhead'
    )

    std_overhead = fields.Float(
        'Std Overhead',
        compute='_get_wo_std_labor_overhead'
    )

    real_labor = fields.Float(
        'Avg Actual Labor',
        compute='_get_wo_real_labor_overhead'
    )

    real_overhead = fields.Float(
        'Avg Actual Overhead',
        compute='_get_wo_real_labor_overhead'
    )


class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def _compute_wo_costs_overview(self):
        for wo in self:
        
            wc = wo.workcenter_id
            op = wo.operation_id
            
            labor_cost = wc.costs_hour
            ovh_cost = wc.overhead_costs_hour
            
            cycle_number = float_round((wo.qty_production) / wc.capacity, precision_digits=2, rounding_method='UP')
            duration_std = float_round((wc.time_start + wc.time_stop + cycle_number * wo.operation_id.time_cycle_std * (100/wc.time_efficiency)) / 60, precision_digits=2)
            duration_real = wc.time_start + wc.time_stop + (cycle_number * wo.duration) / 60 * (100/wc.time_efficiency)

            # standard costs
            # extra work -- all variance
            if wo.add_consumption:
                std_labor_cost = 0.0
                std_overhead_cost = 0.0
                
            # standard work order
            else:
                std_labor_cost = duration_std * labor_cost
                std_overhead_cost = duration_std * ovh_cost
            
            # real costs
            real_labor_cost = duration_real * labor_cost
            real_overhead_cost = duration_real * ovh_cost
            
            # variance
            variance_labor = real_labor_cost - std_labor_cost
            variance_overhead = real_overhead_cost - std_overhead_cost
            
            wo.update({
                'std_labor': std_labor_cost,
                'std_overhead': std_overhead_cost,
                'real_labor': real_labor_cost,
                'real_overhead': real_overhead_cost,
                'variance_labor': variance_labor,
                'variance_overhead': variance_overhead
            })

    rework_qty = fields.Float(
        string='Rework Quantity',
    )
    
    add_consumption = fields.Boolean(
        string='Extra Work',
        default=False,
        help='Marks WO that are added for Extra labor. '
             'May have additional material used up too.'
    )
    
    std_labor = fields.Float(
        string='Std Labor',
        compute='_compute_wo_costs_overview'
    )
    std_overhead = fields.Float(
        string='Std Overhead',
        compute='_compute_wo_costs_overview'
    )
    real_labor = fields.Float(
        string='Actual Labor',
        compute='_compute_wo_costs_overview'
    )
    real_overhead = fields.Float(
        string='Actual Overhead',
        compute='_compute_wo_costs_overview'
    )
    variance_labor = fields.Float(
        string='Computed Labor Variance',
        compute='_compute_wo_costs_overview'
    )
    variance_overhead = fields.Float(
        string='Computed Overhead Variance',
        compute='_compute_wo_costs_overview'
    )
    
    @api.multi
    def record_production(self):
        if not self:
            return True
        self.ensure_one()
        if self.qty_producing <= 0:
            raise UserError(_('Please set the quantity you are currently producing. It should be different from zero.'))

        if (self.production_id.product_id.tracking != 'none') and not self.final_lot_id and self.move_raw_ids:
            raise UserError(_('You should provide a lot/serial number for the final product'))

        # Update quantities done on each raw material line
        # For each untracked component without any 'temporary' move lines,
        # (the new workorder tablet view allows registering consumed quantities for untracked components)
        # we assume that only the theoretical quantity was used
        for move in self.move_raw_ids:
            rounding = move.product_uom.rounding
            if move.has_tracking == 'none' and (move.state not in ('done', 'cancel')) and move.bom_line_id\
                        and move.unit_factor and not move.move_line_ids.filtered(lambda ml: not ml.done_wo):
                if self.product_id.tracking != 'none':
                    qty_to_add = float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
                    move._generate_consumed_move_line(qty_to_add, self.final_lot_id)
                else:
                    move.quantity_done += float_round(self.qty_producing * move.unit_factor, precision_rounding=rounding)
            elif move.add_consumption:
                if self.product_id.tracking != 'none':
                    qty_to_add = float_round(
                        self.qty_producing * move.unit_factor,
                        precision_rounding=rounding)
                    move._generate_consumed_move_line(
                        qty_to_add, self.final_lot_id)
                else:
                    move.quantity_done += float_round(
                        self.qty_producing * move.unit_factor,
                        precision_rounding=rounding)
            elif len(move._get_move_lines()) < 2:
                move.quantity_done += float_round(
                    self.qty_producing * move.unit_factor,
                    precision_rounding=rounding)
            else:
                move._set_quantity_done(move.quantity_done + float_round(
                    self.qty_producing * move.unit_factor,
                    precision_rounding=rounding))
        # Transfer quantities from temporary to final move lots or make them final
        for move_line in self.active_move_line_ids:
            # Check if move_line already exists
            if move_line.qty_done <= 0:  # rounding...
                move_line.sudo().unlink()
                continue
            if move_line.product_id.tracking != 'none' and not move_line.lot_id:
                raise UserError(_('You should provide a lot/serial number for a component.'))
            # Search other move_line where it could be added:
            lots = self.move_line_ids.filtered(lambda x: (x.lot_id.id == move_line.lot_id.id) and (not x.lot_produced_id) and (not x.done_move) and (x.product_id == move_line.product_id))
            if lots:
                lots[0].qty_done += move_line.qty_done
                lots[0].lot_produced_id = self.final_lot_id.id
                self._link_to_quality_check(move_line, lots[0])
                move_line.sudo().unlink()
            else:
                move_line.lot_produced_id = self.final_lot_id.id
                move_line.done_wo = True

        self.move_line_ids.filtered(
            lambda move_line: not move_line.done_move and not move_line.lot_produced_id and move_line.qty_done > 0
        ).write({
            'lot_produced_id': self.final_lot_id.id,
            'lot_produced_qty': self.qty_producing
        })

        # If last work order, then post lots used
        # TODO: should be same as checking if for every workorder something has been done?
        if not self.next_work_order_id:
            production_moves = self.production_id.move_finished_ids.filtered(lambda x: (x.state not in ('done', 'cancel')))
            for production_move in production_moves:
                if production_move.product_id.id == self.production_id.product_id.id and production_move.has_tracking != 'none':
                    move_line = production_move.move_line_ids.filtered(lambda x: x.lot_id.id == self.final_lot_id.id)
                    if move_line:
                        move_line.product_uom_qty += self.qty_producing
                    else:
                        move_line.create({'move_id': production_move.id,
                                 'product_id': production_move.product_id.id,
                                 'lot_id': self.final_lot_id.id,
                                 'product_uom_qty': self.qty_producing,
                                 'product_uom_id': production_move.product_uom.id,
                                 'qty_done': self.qty_producing,
                                 'workorder_id': self.id,
                                 'location_id': production_move.location_id.id,
                                 'location_dest_id': production_move.location_dest_id.id,
                        })
                elif production_move.unit_factor:
                    rounding = production_move.product_uom.rounding
                    production_move.quantity_done += float_round(self.qty_producing * production_move.unit_factor, precision_rounding=rounding)
                else:
                    if not self.add_consumption:
                        production_move.quantity_done += self.qty_producing

        if not self.next_work_order_id:
            for by_product_move in self.production_id.move_finished_ids.filtered(lambda x: (x.product_id.id != self.production_id.product_id.id) and (x.state not in ('done', 'cancel'))):
                if by_product_move.has_tracking == 'none':
                    by_product_move.quantity_done += self.qty_producing * by_product_move.unit_factor

        # Update workorder quantity produced
        self.qty_produced += self.qty_producing

        if self.final_lot_id:
            self.final_lot_id.use_next_on_work_order_id = self.next_work_order_id
            self.final_lot_id = False

        # One a piece is produced, you can launch the next work order
        self._start_nextworkorder()

        # Set a qty producing
        rounding = self.production_id.product_uom_id.rounding
        if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
            self.qty_producing = 0
        elif self.production_id.product_id.tracking == 'serial':
            self._assign_default_final_lot_id()
            self.qty_producing = 1.0
            self._generate_lot_ids()
        else:
            self.qty_producing = float_round(self.production_id.product_qty - self.qty_produced, precision_rounding=rounding)
            self._generate_lot_ids()

        if self.next_work_order_id and self.next_work_order_id.state not in ['done', 'cancel'] and self.production_id.product_id.tracking != 'none':
            self.next_work_order_id._assign_default_final_lot_id()

        if float_compare(self.qty_produced, self.production_id.product_qty, precision_rounding=rounding) >= 0:
            self.button_finish()
        return True

    @api.multi
    def button_finish(self):
        res = super(MRPWorkorder, self).button_finish()
        for wo in self:
            wo._create_wo_account_move()
            if wo.variance_labor or wo.variance_overhead:
                wo._create_variance_account_move()
        return res

    @api.multi
    def _create_variance_account_move(self):
        move_obj = self.env['account.move']
        for workorder in self:
            # Calculate valuation_amount
            product = workorder.product_id
            qty = workorder.qty_production
            production = workorder.production_id

            # Prepare accounts
            accounts = product.product_tmpl_id.get_product_accounts()
            journal_id = accounts['stock_journal'].id
            debit_account_id = accounts['labor_variance_acc_id'].id
            credit_account_id = accounts['production_account_id'].id

            if not debit_account_id or not credit_account_id:
                raise UserError(_("Manufacturing Account and/or Labor Variance Account needs to be set on the product %s.") % (product.name,))
            # Create data for account move and post them
            name = production.name + '-' + 'Variance::' + workorder.name
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': workorder.variance_labor > 0 and workorder.variance_labor or 0,
                'debit': workorder.variance_labor < 0 and -workorder.variance_labor or 0,
                'account_id': debit_account_id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'debit': workorder.variance_labor > 0 and workorder.variance_labor or 0,
                'credit': workorder.variance_labor < 0 and -workorder.variance_labor or 0,
                'account_id': credit_account_id,
            }
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            # Create an data entry for Overhead
            debit_account_id = accounts['overhead_variance_acc_id'] and accounts['overhead_variance_acc_id'].id or False
            credit_account_id = accounts['production_account_id'] and accounts['production_account_id'].id or False
            if not debit_account_id or not credit_account_id:
                raise UserError(_("It seems Overhead Accounts for product %s is not set. Which means there is probably a configuration error") % (product.name,))
            # Create data for account move and post them
            name = production.name + '-' + 'Variance Overhead::' + workorder.name
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': workorder.variance_overhead > 0 and workorder.variance_overhead  or 0,
                'debit': workorder.variance_overhead  < 0 and -workorder.variance_overhead  or 0,
                'account_id': debit_account_id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'debit': workorder.variance_overhead  > 0 and workorder.variance_overhead  or 0,
                'credit': workorder.variance_overhead  < 0 and -workorder.variance_overhead  or 0,
                'account_id': credit_account_id,
            }
            move_lines.append((0, 0, debit_line_vals))
            move_lines.append((0, 0, credit_line_vals))

            if move_lines:
                new_move = move_obj.create(
                    {'journal_id': journal_id,
                     'line_ids': move_lines,
                     'date': fields.Date.context_today(self),
                     'ref': name or ''})
                new_move.post()
        return True

    @api.multi
    def _create_wo_account_move(self):
        move_obj = self.env['account.move']
        for workorder in self:
        
            # create default entry
            if not workorder.add_consumption:
                workorder._create_wo_start_account_move()
            
            # Calculate valuation_amount
            product = workorder.product_id
            qty = workorder.qty_production
            production = workorder.production_id

            # Prepare accounts
            accounts = product.product_tmpl_id.get_product_accounts()
            journal_id = accounts['stock_journal'].id
            debit_account_id = accounts['labor_variance_acc_id'].id
            credit_account_id = accounts['production_account_id'].id

            if not debit_account_id or not credit_account_id:
                raise UserError(_("Manufacturing Account and/or Labor Variance Account needs to be set on the product %s.") % (product.name,))
            # Create data for account move and post them
            name = production.name + '-' + 'Extra Labor::' + workorder.name
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': workorder.std_labor > 0 and workorder.std_labor or 0,
                'debit': workorder.std_labor < 0 and -workorder.std_labor or 0,
                'account_id': debit_account_id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'debit': workorder.std_labor > 0 and workorder.std_labor or 0,
                'credit': workorder.std_labor < 0 and -workorder.std_labor or 0,
                'account_id': credit_account_id,
            }
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            # Create an data entry for Overhead
            debit_account_id = accounts['overhead_variance_acc_id'] and accounts['overhead_variance_acc_id'].id or False
            credit_account_id = accounts['production_account_id'] and accounts['production_account_id'].id or False
            if not debit_account_id or not credit_account_id:
                raise UserError(_("It seems Overhead Accounts for product %s is not set. Which means there is probably a configuration error") % (product.name,))
            # Create data for account move and post them
            name = production.name + '-' + 'Extra Overhead::' + workorder.name
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': workorder.std_overhead > 0 and workorder.std_overhead  or 0,
                'debit': workorder.std_overhead  < 0 and -workorder.std_overhead  or 0,
                'account_id': debit_account_id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'debit': workorder.std_overhead  > 0 and workorder.std_overhead  or 0,
                'credit': workorder.std_overhead  < 0 and -workorder.std_overhead  or 0,
                'account_id': credit_account_id,
            }
            move_lines.append((0, 0, debit_line_vals))
            move_lines.append((0, 0, credit_line_vals))

            if move_lines:
                new_move = move_obj.create(
                    {'journal_id': journal_id,
                     'line_ids': move_lines,
                     'date': fields.Date.context_today(self),
                     'ref': name or ''})
                new_move.post()
        return True

    def _create_wo_start_account_move(self):

        move_obj = self.env['account.move']
        debit_account_id = False

        # adding extra material and extra step, fetch debit account from move
        if self.production_id.move_raw_ids:
            for ml in self.production_id.move_raw_ids:
                journal_id, acc_src, debit_account_id, acc_valuation = ml._get_accounting_data_for_valuation()

        # fetch debit account from location
        else:
            debit_account_id = self.production_id.routing_id.location_id.valuation_in_account_id.id or False
            if not debit_account_id:
                debit_account_id = self.product.property_stock_production.valuation_in_account_id.id or False

        # Prepare accounts
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        journal_id = accounts['stock_journal'].id
        credit_account_id = accounts['manufacturing_acc_id'].id

        if not debit_account_id or not credit_account_id:
            raise UserError(_("It seems Manufacturing Account or Labor Variance Account for product %s is not set. Which means there is probably a configuration error") % (self.product_id.name,))
            
        # Create data for account move and post them
        name = self.production_id.name + '-' + 'Std Labor::' + self.name
        debit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'debit': self.std_labor > 0 and self.std_labor or 0,
            'credit': self.std_labor < 0 and -self.std_labor or 0,
            'account_id': debit_account_id,
        }
        credit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'credit': self.std_labor > 0 and self.std_labor or 0,
            'debit': self.std_labor < 0 and -self.std_labor or 0,
            'account_id': credit_account_id,
        }
        move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

        credit_account_id = accounts['overhead_absorption_acc_id'] and accounts['overhead_absorption_acc_id'].id or False
        if not debit_account_id or not credit_account_id:
            raise UserError(_("It seems Overhead Absorption Account for product %s is not set. Which means there is probably a configuration error") % (self.product.name,))
            
        # Create data for account move and post them
        name = self.production_id.name + '-' + 'Std Overhead::' + self.name
        debit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'debit': self.std_overhead > 0 and self.std_overhead or 0,
            'credit': self.std_overhead < 0 and -self.std_overhead or 0,
            'account_id': debit_account_id,
        }
        credit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'credit': self.std_overhead > 0 and self.std_overhead or 0,
            'debit': self.std_overhead < 0 and -self.std_overhead or 0,
            'account_id': credit_account_id,
        }
        move_lines.append((0, 0, debit_line_vals))
        move_lines.append((0, 0, credit_line_vals))
        if move_lines:
            new_move = move_obj.create(
                {'journal_id': journal_id,
                 'line_ids': move_lines,
                 'date': fields.Date.context_today(self),
                 'ref': self.production_id.name})
            new_move.post()
        return True


class MRPBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_efficiency = fields.Float(
        string='Manufacturing Efficiency',
        default=1.0,
        help="A factor of 0.9 means a loss of 10% within the production "
             "process."
    )


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _compute_wo_lines_costs_overview(self):
        for production in self:
            std_labor = std_overhead = variance_labor = variance_overhead =0
            std_material = variance_material = 0
            real_labor = real_overhead = real_material = 0
            
            # Compute Std & Variance labor overhead
            for wo in production.workorder_ids:
                std_labor += wo.std_labor
                std_overhead += wo.std_overhead
                real_labor += wo.real_labor
                real_overhead += wo.real_overhead
                variance_labor += wo.variance_labor
                variance_overhead += wo.variance_overhead
                
            # Compute Std material
            for bom_line in production.bom_id.bom_line_ids:
                new_qty = bom_line.product_qty / bom_line.product_efficiency
                std_material += production.company_id.currency_id.round(
                    bom_line.product_id.uom_id._compute_price(
                        bom_line.product_id.standard_price,
                        bom_line.product_uom_id)
                    * new_qty)
            # Compute variance material
            for move in production.move_raw_ids:
                if move.add_consumption:
                    valuation_amount = move.product_id.standard_price \
                                       * move.product_qty
                    variance_material += move.company_id.currency_id.\
                        round(valuation_amount * move.product_qty)
                        
            real_material = std_material * production.product_qty + variance_material
            production.update({
                'std_labor': std_labor,
                'std_overhead': std_overhead,
                'std_material': std_material * production.product_qty,
                'real_labor': real_labor,
                'real_overhead': real_overhead,
                'real_material': real_material,
                'variance_labor': variance_labor,
                'variance_overhead': variance_overhead,
                'variance_material': variance_material
            })

    std_labor = fields.Float(
        string='Std. Labor',
        compute='_compute_wo_lines_costs_overview'
    )
    std_overhead = fields.Float(
        string='Std. Overhead',
        compute='_compute_wo_lines_costs_overview'
    )
    std_material = fields.Float(
        string='Std. Material',
        compute='_compute_wo_lines_costs_overview'
    )
    real_labor = fields.Float(
        string='Actual Labor',
        compute='_compute_wo_lines_costs_overview'
    )
    real_overhead = fields.Float(
        string='Actual Overhead',
        compute='_compute_wo_lines_costs_overview'
    )    
    real_material = fields.Float(
        string='Actual Material',
        compute='_compute_wo_lines_costs_overview'
    )    
    variance_labor = fields.Float(
        string='Labor Variance',
        compute='_compute_wo_lines_costs_overview'
    )
    variance_overhead = fields.Float(
        string='Overhead Variance',
        compute='_compute_wo_lines_costs_overview'
    )
    variance_material = fields.Float(
        string='Material Variance',
        compute='_compute_wo_lines_costs_overview'
    )

    @api.multi
    def _generate_move_link_workorder(self, move):
        for production in self:
            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': move.product_id.id,
                'lot_id': False,
                'product_uom_qty': move.product_uom_qty,
                'product_uom_id': move.product_uom.id,
                'qty_done': 0,
                'workorder_id': self.id,
                'done_wo': False,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
            })
        return True

    @api.multi
    def _generate_additional_raw_move(self, product, quantity):
        move = super(MRPProduction, self)._generate_additional_raw_move(
            product, quantity)
        workorder = self._context.get('selected_workorder_id')
        uom_id = self._context.get('uom_id')
        move.write({'add_consumption': True,
                    'operation_id': workorder and workorder.operation_id.id,
                    'workorder_id': workorder and workorder.id,
                    'product_uom': uom_id})
        # Link moves to Workorder so raw materials can be consume in it
        move._action_confirm()
        return move

    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        production_cost = ovh_cost = labor_cost = mtl_cost = 0.0
        if consumed_moves:
            mtl_cost = super(MRPProduction, self)._cal_price(consumed_moves)
            
        for workorder in self.workorder_ids:
            labor_cost += workorder.real_labor
            ovh_cost += workorder.real_overhead
            
        production_cost = mtl_cost + labor_cost + ovh_cost
        
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            finished_move.value = production_cost
            finished_move.price_unit = production_cost / finished_move.product_uom_qty
        return True
