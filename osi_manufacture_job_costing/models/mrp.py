# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_round, float_compare

class MRPWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    burden_type = fields.Selection(string="Burden Type", selection=[(
        'rate', 'Rate'), ('percent', 'Percentage')], default='rate', copy=True)
        
    burden_costs_hour = fields.Float(
        'Burden Cost per hour'
    )
    burden_costs_percent = fields.Float(
        'Burden Cost Percentage'
    )

class MRPWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    labor_cost = fields.Float(
        'Labor Cost'
    )
    
    burden_cost = fields.Float(
        'Burden'
    )
    
    total_cost = fields.Float(
        'Total Cost'
    )
    
    add_consumption = fields.Boolean(
        string='Extra Work',
        default=False,
        help='Marks WO that are added for Extra labor. '
             'May have additional material used up too.'
    )

    @api.multi
    def button_finish(self):
    
        self.rollup_costs()
        res = super(MRPWorkorder, self).button_finish()
        return res

    def _create_wip2finish_account_move(self):
        move_obj = self.env['account.move']
        workorder = self

        labor_cost = workorder.labor_cost
        burden_cost = workorder.burden_cost
        product = workorder.product_id
        production = workorder.production_id

        # Prepare accounts
        accounts = product.product_tmpl_id.get_product_accounts()
        journal_id = accounts['stock_journal'].id
        stock_valuation_id = accounts['stock_valuation'].id
        labor_wip_acc_id = accounts['labor_wip_acc_id'].id
        overhead_wip_acc_id = accounts['overhead_wip_acc_id'].id
        production_account_id = accounts['production_account_id'].id
        job_id = production.ssi_job_id or False
        partner_id = job_id and job_id.partner_id.id or False
        analytic_account_id = job_id and job_id.aa_id.id or False

        if not stock_valuation_id:
            raise UserError(_("Stock valuation accounts need to be set on the product %s.") % (product.name,))

        if not labor_wip_acc_id or not overhead_wip_acc_id:
            raise UserError(_("Labor and Burden WIP accounts need to be set."))
            
        if not labor_wip_acc_id or not overhead_wip_acc_id or not production_account_id:
            raise UserError(_("WIP account needs to be set on production location"))

        # Create data for account move and post them

        name = job_id and job_id.name + '-' + production.name + '-' + workorder.name or production.name + '-' + workorder.name
        ref = job_id and job_id.name + '-' + production.name + '-' + workorder.name or production.name + '-' + workorder.name

        # WIP to FG account move lines (Labor)
        debit_line_vals = {
            'name': name,
            'product_id': product.id,
            'quantity': workorder.qty_produced or 1,
            'product_uom_id': product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'workcenter_id': self.workcenter_id.id or False,
            'credit': 0.0,
            'debit': labor_cost,
            'account_id': stock_valuation_id,
            'analytic_account_id': analytic_account_id
        }
        credit_line_vals = {
            'name': name,
            'product_id': product.id,
            'quantity': workorder.qty_produced or 1,
            'product_uom_id': product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'workcenter_id': self.workcenter_id.id or False,
            'credit': labor_cost,
            'debit': 0.0,
            'account_id': labor_wip_acc_id or production_account_id,
            'analytic_account_id': analytic_account_id
        }

        move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

        # WIP to FG account move (Labor)
        if move_lines:
            new_move = move_obj.create(
                {'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': fields.Date.context_today(self),
                    'ref': name or ''})
            new_move.post()

        # WIP to FG account move lines (Overhead)
        debit_line_vals = {
            'name': name,
            'product_id': product.id,
            'quantity': workorder.qty_produced or 1,
            'product_uom_id': product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'workcenter_id': self.workcenter_id.id or False,
            'credit': 0.0,
            'debit': burden_cost,
            'account_id': stock_valuation_id,
            'analytic_account_id': analytic_account_id
        }
        credit_line_vals = {
            'name': name,
            'product_id': product.id,
            'quantity': workorder.qty_produced or 1,
            'product_uom_id': product.uom_id.id,
            'ref': ref,
            'partner_id': partner_id,
            'workcenter_id': self.workcenter_id.id or False,
            'credit': burden_cost,
            'debit': 0.0,
            'account_id': overhead_wip_acc_id or production_account_id,
            'analytic_account_id': analytic_account_id
        }

        move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

        # WIP to FG account move (Labor)
        if move_lines:
            new_move = move_obj.create(
                {'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': fields.Date.context_today(self),
                    'ref': name or ''})
            new_move.post()
                                   
        return True

    @api.model
    def run_job_costing_scheduler(self):
        # Get all the in progress workorders and process them one by one
        in_process_wos = self.env['mrp.workorder'].search([('state','=','progress')])
        # rollup costs for all in process wos
        if in_process_wos:
            in_process_wos.rollup_costs()

    
    @api.multi
    def rollup_costs(self):
        for wo in self:

            wc = wo.workcenter_id

            # labor and burden rates
            labor_rate = wc.costs_hour / 60
            
            if wc.burden_type == 'rate':
                burden_rate = wc.burden_costs_hour/60
            elif wc.burden_type == 'percent':
                burden_rate = labor_rate * wc.burden_costs_percent / 100
        
            time_ids = wo.time_ids.filtered(lambda tl: not tl.cost_already_recorded)
            
            cost_dict = {}
            labor = 0.0
            burden = 0.0
            labor_total = 0.0
            burden_total = 0.0
            
            for time_rec in time_ids:
                if time_rec.cost_already_recorded:
                    continue
                    
                labor = time_rec.duration * labor_rate
                burden = time_rec.duration * burden_rate
                
                labor_total += labor
                burden_total += burden
                
                date = time_rec.date_end.date()
                value = cost_dict.get(date, False)
                value_labor = value and value[0]
                value_burden = value and value[1]
                
                if value:
                    cost_dict.update({date:(value_labor + labor, value_burden + burden)})
                    
                else:
                    cost_dict[date] = (labor, burden)
                
                time_rec.update({'cost_already_recorded': True})
                    
            # write journal entry
            for key in cost_dict:
                wo.create_account_move({key:cost_dict[key]})
                
            wo.update({
                'labor_cost': wo.labor_cost + labor_total,
                'burden_cost': wo.burden_cost + burden_total,
                'total_cost': wo.total_cost + labor_total + burden_total,
            })

    @api.multi
    def write(self, values):
    
        set1 = set(values.keys())
        set2 = set(['labor_cost', 'burden_cost', 'total_cost', 'time_ids'])
        
        if not set1.intersection(set2) and any(workorder.state == 'done' for workorder in self):
            raise UserError(_('You can not change the finished work order.'))
        return models.Model.write(self, values)

    def create_account_move(self, cost_day):
    
        move_obj = self.env['account.move']
        workorder = self
        for date in cost_day:
        
            cost = cost_day[date]
            product = workorder.product_id
            production = workorder.production_id

            # Prepare accounts
            accounts = product.product_tmpl_id.get_product_accounts()            
            journal_id = accounts['stock_journal'].id
            labor_absorption_acc_id = accounts['labor_absorption_acc_id'].id
            labor_wip_acc_id = accounts['labor_wip_acc_id'].id
            overhead_absorption_acc_id = accounts['overhead_absorption_acc_id'].id
            overhead_wip_acc_id = accounts['overhead_wip_acc_id'].id
            production_account_id = accounts['production_account_id'].id
            job_id = production.ssi_job_id or False
            partner_id = job_id and job_id.partner_id.id or False
            analytic_account_id = job_id and job_id.aa_id.id or False

            if not labor_absorption_acc_id or not overhead_absorption_acc_id:
                raise UserError(_("Labor absorption and labor burden accounts need to be set on the product %s.") % (product.name,))
                
            if not labor_wip_acc_id or not overhead_wip_acc_id :
                raise UserError(_("Labor and Burden WIP accounts needs to be set."))

            if not labor_wip_acc_id or not overhead_wip_acc_id or not production_account_id:
                raise UserError(_("WIP account needs to be set on production location."))
                
            # Create data for account move and post them
            
            name = job_id and job_id.name + '-' + production.name + '-' +  workorder.name or production.name + '-' +  workorder.name
            name = workorder.add_consumption and ('Extra Work: ' + name) or name
            ref = job_id and job_id.name + '-' + production.name + '-' + 'Labor - ' + date.strftime("%Y-%m-%d") or production.name + '-' + 'Labor - ' + date.strftime("%Y-%m-%d")
            ref1 = job_id and job_id.name + '-' + production.name + '-' + 'Burden - ' + date.strftime("%Y-%m-%d") or production.name + '-' + 'Burden - ' + date.strftime("%Y-%m-%d")
            
            # labor move lines
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': 0.0,
                'debit': cost[0],
                'account_id': labor_wip_acc_id or production_account_id,
                'analytic_account_id': analytic_account_id
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref,
                'partner_id': partner_id,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': cost[0],
                'debit': 0.0,
                'account_id': labor_absorption_acc_id,
                'analytic_account_id': analytic_account_id
            }
            
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]
            
            # labor account move
            if move_lines:
                new_move = move_obj.create(
                    {'journal_id': journal_id,
                     'line_ids': move_lines,
                     'date': fields.Date.context_today(self),
                     'ref': name or ''})
                new_move.post()
                
            # burden move lines
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref1,
                'partner_id': partner_id,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': 0.0,
                'debit': cost[1],
                'account_id': overhead_wip_acc_id or production_account_id,
                'analytic_account_id': analytic_account_id
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref1,
                'partner_id': partner_id,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': cost[1],
                'debit': 0.0,
                'account_id': overhead_absorption_acc_id,
                'analytic_account_id': analytic_account_id
            }
            
            move_lines = [(0, 0, debit_line_vals), (0, 0, credit_line_vals)]

            # burden account move
            if move_lines:
                new_move = move_obj.create(
                    {'journal_id': journal_id,
                     'line_ids': move_lines,
                     'date': fields.Date.context_today(self),
                     'ref': name or ''})
                new_move.post()
                
        return True

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
                        move.product_uom_qty * move.unit_factor,
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

class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _compute_wo_lines_costs_overview(self):
        for production in self:
            material_cost = labor_cost = burden_cost = total_cost = 0
            
            # Compute Std & Variance labor overhead
            for wo in production.workorder_ids:
                labor_cost += wo.labor_cost
                burden_cost += wo.burden_cost
                
            # Compute Std material
            for bom_line in production.bom_id.bom_line_ids:
                new_qty = bom_line.product_qty
                material_cost += production.company_id.currency_id.round(
                    bom_line.product_id.uom_id._compute_price(
                        bom_line.product_id.standard_price,
                        bom_line.product_uom_id)
                    * new_qty)
                    
            # Compute extra material
            for move in production.move_raw_ids:
                if move.add_consumption:
                    valuation_amount = move.product_id.standard_price \
                                       * move.product_qty
                    material_cost += move.company_id.currency_id.\
                        round(valuation_amount)
                    
            production.update({
                'labor_cost': labor_cost,
                'burden_cost': burden_cost,
                'material_cost': material_cost * production.product_qty,
            })

    labor_cost = fields.Float(
        string='Labor Cost',
        compute='_compute_wo_lines_costs_overview'
    )
    burden_cost = fields.Float(
        string='Burden Cost',
        compute='_compute_wo_lines_costs_overview'
    )
    material_cost = fields.Float(
        string='Material Cost',
        compute='_compute_wo_lines_costs_overview'
    )

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
            mtl_cost = sum([-m.value for m in consumed_moves])
            
        production_cost = mtl_cost
        
        finished_move = self.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel') and x.quantity_done > 0)
        if finished_move:
            finished_move.ensure_one()
            finished_move.value = production_cost
            finished_move.price_unit = production_cost / finished_move.product_uom_qty
        return True

    @api.multi
    def post_inventory(self):
        res = super(MRPProduction, self).post_inventory()
        # Create Journal Entry from WIP To Finish Goods
        for mo in self:
            for wo in mo.workorder_ids:
                wo._create_wip2finish_account_move()
        return res