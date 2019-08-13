# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round, float_compare


class MRPRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    cycle_nbr = fields.Float(
        string='Std No. of Cycles',
        help="Number of iterations this work center has to do in the "
             "specified operation of the routing."
    )
    hour_nbr = fields.Float(
        string='Std No. of Hours',
        help="Time in hours for this Work Center to achieve the operation "
             "of the specified routing."
    )


class MRPWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    @api.multi
    def _get_wo_std_labor_overhead(self):
        for wc in self:
            # Calculate valuation_amount
            valuation_amount = \
                (wc.time_start + wc.time_stop + wc.time_cycle)*wc.costs_hour \
                + wc.capacity*wc.costs_cycle
            # Calculate Overhead Amount
            overhead_valuation_amount = \
                (wc.time_start + wc.time_stop + wc.time_cycle) \
                * wc.overhead_cost_per_cycle
            wc.update({
                'std_labor': valuation_amount,
                'std_overhead': overhead_valuation_amount,
            })

    costs_cycle = fields.Float(
        'Cost per cycle',
        help="Specify Cost of Work Center per cycle."
    )
    time_cycle = fields.Float(
        'Time for 1 cycle (hour)',
        help="Time in hours for doing one cycle."
    )
    overhead_cost_per_cycle = fields.Float('Overhead Cost per Hour')
    overhead_cost_acc_id = fields.Many2one(
        'account.account',
        string='Overhead Cost Account'
    )
    std_labor = fields.Float(
        'Std. Labor',
        compute='_get_wo_std_labor_overhead'
    )
    std_overhead = fields.Float(
        'Std. Overhead',
        compute='_get_wo_std_labor_overhead'
    )


class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def _compute_wo_costs_overview(self):
        for wo in self:
            # Calculate Std Labor
            cycle_cost = wo.cycle * wo.costs_cycle
            std_hours = \
                (wo.time_start + wo.time_stop + wo.hour * wo.cycle)
            hour_cost = std_hours * wo.costs_hour
            cost = cycle_cost + hour_cost
            # the company currency... so we need to use round() before creating
            # the accounting entries.
            std_labor_cost = \
                wo.production_id and \
                (wo.production_id.company_id.currency_id.
                    round(cost * wo.qty_production)) or 0

            # Calculation Std Overhead
            std_overhead_cost = std_hours * wo.overhead_cost_per_cycle
            std_overhead_cost = \
                wo.production_id and \
                (wo.production_id.company_id.currency_id.
                    round(std_overhead_cost * wo.qty_production)) or 0

            # Calculation Variance Labor and Overhead
            actual_hours = wo.duration
            # difference in hours
            diff = 0
            if not actual_hours:
                diff = actual_hours - std_hours
            variance_labor = diff * wo.costs_hour
            variance_labor = \
                wo.production_id and \
                (wo.production_id.company_id.currency_id.
                    round(variance_labor * wo.qty_production)) or 0
            variance_overhead = std_hours and \
                                (wo.overhead_cost_per_cycle * diff) or 0.0
            variance_overhead = \
                wo.production_id and \
                (wo.production_id.company_id.currency_id.
                    round(variance_overhead * wo.qty_production)) or 0

            wo.update({
                'std_labor': std_labor_cost,
                'std_overhead': std_overhead_cost,
                'variance_labor': variance_labor,
                'variance_overhead': variance_overhead
            })

    add_consumption = fields.Boolean(
        string='Extra Work',
        default=False,
        help='Marks WO that are added for Extra labor. '
             'May have additional material used up too.'
    )
    rework_qty = fields.Float('Rework Qty')
    actual_variance_labor = fields.Float('Actual Labor Variance')
    actual_variance_overhead = fields.Float('Actual Overhead Variance')
    cycle = fields.Float('Number of Cycles')
    costs_cycle = fields.Float('Cost per Cycle')
    time_start = fields.Float('Time for Setup')
    time_stop = fields.Float('Time for Cleanup')
    hour = fields.Float('Number of Hours')
    costs_hour = fields.Float('Cost per Hour')
    overhead_cost_per_cycle = fields.Float('Overhead Cost per Hour')
    std_labor = fields.Float(
        string='Std. Labor',
        compute='_compute_wo_costs_overview'
    )
    std_overhead = fields.Float(
        string='Std. Overhead',
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
    def button_start(self):
        res = super(MRPWorkorder, self).button_start()
        for wo in self:
            if not wo.add_consumption:
            # Make Manufacturing Account to WIP Account Move
                wo._create_wo_start_account_move()
            else:
                wo._create_wo_account_move()
        return res

    @api.multi
    def _create_wo_account_move(self):
        move_obj = self.env['account.move']
        for workorder in self:
            # Calculate valuation_amount
            product = workorder.product_id
            qty = workorder.qty_production
            production = workorder.production_id
            # Calculate valuation_amount for Labor
            cycle_cost = workorder.cycle * workorder.costs_cycle
            hour_cost = (workorder.time_start + workorder.time_stop + workorder.hour * workorder.cycle) * workorder.costs_hour
            valuation_amount = cycle_cost + hour_cost

            valuation_amount = (workorder.rework_qty/qty) * valuation_amount
            # the company currency... so we need to use round() before creating the accounting entries.
            valuation_amount = production and (production.company_id.currency_id.round(valuation_amount * qty)) or 0

            # Prepare accounts
            accounts = product.product_tmpl_id.get_product_accounts()
            journal_id = accounts['stock_journal'].id
            debit_account_id = accounts['labor_variance_acc_id'].id
            credit_account_id = accounts['manufacturing_acc_id'].id

            if not debit_account_id or not credit_account_id:
                raise UserError(_("Manufacturing Account and/or Labor Variance Account needs to be set on the product %s.") % (product.name,))
            # Create data for account move and post them
            name = production.name + '-' + 'Extra Labor::' + workorder.name
            analytic_account = self.env['account.analytic.account'].search(
                [('manufacture','=',True)], limit=1)
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'debit': valuation_amount > 0 and valuation_amount or 0,
                'credit': valuation_amount < 0 and -valuation_amount or 0,
                'account_id': debit_account_id,
                'analytic_account_id': analytic_account.id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': valuation_amount > 0 and valuation_amount or 0,
                'debit': valuation_amount < 0 and -valuation_amount or 0,
                'account_id': credit_account_id,
                'analytic_account_id': analytic_account.id,
            }
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            # Create an data entry for Overhead
            # Calculate Overhead Amount
            overhead_valuation_amount = (workorder.time_start + workorder.time_stop + workorder.hour * workorder.cycle) * workorder.overhead_cost_per_cycle
            overhead_valuation_amount = (workorder.rework_qty/qty) * overhead_valuation_amount

            # the company currency... so we need to use round() before creating the accounting entries.
            overhead_valuation_amount = production and (production.company_id.currency_id.round(overhead_valuation_amount * qty)) or 0
            debit_account_id = accounts['overhead_variance_acc_id'] and accounts['overhead_variance_acc_id'].id or False
            credit_account_id = accounts['overhead_absorption_acc_id'] and accounts['overhead_absorption_acc_id'].id or False
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
                'debit': overhead_valuation_amount > 0 and overhead_valuation_amount or 0,
                'credit': overhead_valuation_amount < 0 and -overhead_valuation_amount or 0,
                'account_id': debit_account_id,
                'analytic_account_id': analytic_account.id,
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': qty,
                'product_uom_id': product.uom_id.id,
                'ref': production.name or False,
                'partner_id': False,
                'credit': overhead_valuation_amount > 0 and overhead_valuation_amount or 0,
                'debit': overhead_valuation_amount < 0 and -overhead_valuation_amount or 0,
                'account_id': credit_account_id,
                'analytic_account_id': analytic_account.id,
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
    def _create_wo_start_account_move(self):

        move_obj = self.env['account.move']
        debit_account_id = False

        # Calculate valuation_amount for Labor
        print ("\n===self.cycle=====", self.cycle, self.costs_cycle)
        cycle_cost = self.cycle * self.costs_cycle
        print ("\n===cycle_cost====", cycle_cost)
        print ("\n===self.time_start + self.time_stop + self.hour * self.cycle======", self.time_start, self.time_stop, self.hour, self.cycle)
        hour_cost = (self.time_start + self.time_stop + self.hour * self.cycle) * self.costs_hour
        print ("\n===hour_cost=", hour_cost)
        valuation_amount = cycle_cost + hour_cost
        print ("\n===valuation_amount======", valuation_amount)

        # the company currency... so we need to use round() before creating the accounting entries.
        valuation_amount = self.production_id and (self.production_id.company_id.currency_id.round(valuation_amount * self.qty_production)) or 0

        # adding extra material and extra step, fetch debit account from move
        if self.production_id.move_raw_ids:
            for ml in self.production_id.move_raw_ids:
                journal_id, acc_src, debit_account_id, acc_valuation = ml._get_accounting_data_for_valuation()

        # fetch debit account from location
        else:
            debit_account_id = self.production_id.routing_id.location_id.valuation_in_account_id.id or False
            if not debit_account_id:
                debit_account_id = self.product_id.property_stock_production.valuation_in_account_id.id or False

        # Prepare accounts
        accounts = self.product_id.product_tmpl_id.get_product_accounts()
        journal_id = accounts['stock_journal'].id
        credit_account_id = accounts['manufacturing_acc_id'].id

        if not debit_account_id or not credit_account_id:
            raise UserError(_("It seems Manufacturing Account or Labor Variance Account for product %s is not set. Which means there is probably a configuration error") % (self.product_id.name,))
        # Create data for account move and post them
        name = self.production_id.name + '-' + 'Std Labor::' + self.name
        analytic_account = self.env['account.analytic.account'].search(
            [('manufacture','=',True)], limit=1)

        debit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'debit': valuation_amount > 0 and valuation_amount or 0,
            'credit': valuation_amount < 0 and -valuation_amount or 0,
            'account_id': debit_account_id,
            'analytic_account_id': analytic_account.id,
        }
        credit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'credit': valuation_amount > 0 and valuation_amount or 0,
            'debit': valuation_amount < 0 and -valuation_amount or 0,
            'account_id': credit_account_id,
            'analytic_account_id': analytic_account.id,
        }
        move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

        # Create an data entry for Overhead
        # Calculate Overhead Amount
        overhead_valuation_amount = (self.time_start + self.time_stop + self.hour * self.cycle) * self.overhead_cost_per_cycle
        # the company currency... so we need to use round() before creating the accounting entries.
        overhead_valuation_amount = self.production_id and (self.production_id.company_id.currency_id.round(overhead_valuation_amount * self.qty_production)) or 0

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
            'debit': overhead_valuation_amount > 0 and overhead_valuation_amount or 0,
            'credit': overhead_valuation_amount < 0 and -overhead_valuation_amount or 0,
            'account_id': debit_account_id,
            'analytic_account_id': analytic_account.id,
        }
        credit_line_vals = {
            'name': name,
            'product_id': self.product_id.id,
            'quantity': self.qty_production,
            'product_uom_id': self.product_id.uom_id.id,
            'ref': self.production_id.name or False,
            'partner_id': False,
            'credit': overhead_valuation_amount > 0 and overhead_valuation_amount or 0,
            'debit': overhead_valuation_amount < 0 and -overhead_valuation_amount or 0,
            'account_id': credit_account_id,
            'analytic_account_id': analytic_account.id,
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
            total_std_labor = total_std_overhead = total_variance_labor = 0
            total_std_material = total_variance_overhead = 0
            # Compute Std & Variance labor overhead
            for wo in production.workorder_ids:
                total_std_labor += wo.std_labor
                total_std_overhead += wo.std_overhead
                total_variance_labor += wo.variance_labor or \
                                        wo.actual_variance_labor
                total_variance_overhead += wo.variance_overhead or \
                                           wo.actual_variance_overhead
            # Compute Std material
            for bom_line in production.bom_id.bom_line_ids:
                new_qty = bom_line.product_qty / bom_line.product_efficiency
                total_std_material += production.company_id.currency_id.round(
                    bom_line.product_id.uom_id._compute_price(
                        bom_line.product_id.standard_price,
                        bom_line.product_uom_id)
                    * new_qty)
            # Compute Std material
            total_variance_material = 0
            for move in production.move_raw_ids:
                if move.add_consumption:
                    valuation_amount = move.product_id.standard_price \
                                       * move.product_qty
                    total_variance_material += move.company_id.currency_id.\
                        round(valuation_amount * move.product_qty)
            production.update({
                'std_labor': total_std_labor,
                'std_overhead': total_std_overhead,
                'std_material': total_std_material * production.product_qty,
                'variance_labor': total_variance_labor,
                'variance_overhead': total_variance_overhead,
                'variance_material': total_variance_material
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
    variance_labor = fields.Float(
        string='Labor Variance',
        compute='_compute_wo_lines_costs_overview'
    )
    variance_overhead = fields.Float(
        string='Overhead Variance',
        compute='_compute_wo_lines_costs_overview'
    )
    variance_material = fields.Float(
        string='Variance Material',
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
