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
    def rollup_costs(self):
        for wo in self:

            wc = wo.workcenter_id

            # labor and burden rates            
            labor_rate = wc.costs_hour
            
            if wc.burden_type == 'rate':
                burden_rate = wc.burden_costs_hour
            elif wc.burden_type == 'percent':
                burden_rate = labor_rate * wc.burden_costs_percent
        
            time_ids = wo.time_ids.filtered(lambda tl: not tl.cost_already_recorded)
            
            cost_dict = {}
            labor = 0.0
            burden = 0.0
            labor_total = 0.0
            burden_total = 0.0
            
            for time_rec in time_ids:
                if time_rec.cost_already_recorded:
                    continue
                    
                labor = amount * labor_rate
                if wc_burden_type == 'rate':
                    burden = amount * burden_rate
                else:
                    burden = labor * burden_rate
                
                labor_total += labor
                burden_total += burden
                
                date = time_rec.date_end
                value = cost_dict.get(date, False)
                value_labor = value and value[0]
                value_burden = value and value[1]
                
                if existing_value:
                    cost_dict[date].update((value_labor + labor, value_burden + burden))
                    
                else:
                    cost_dict[date] = (labor, burden)
                
                time_rec.update({'cost_already_recorded': True})
                    
            # write journal entry
            for item in cost_dict:
                self.create_account_move(item)
                
            wo.update({
                'labor_cost': wo.labor + labor_total,
                'burden_cost': wo.burden + burden_total,
                'total_cost': wo.total + labor_total + burden_total,
            })

    def create_account_move(self, cost_day):
    
        move_obj = self.env['account.move']
        
        for date, cost in cost_day.iteritems():
            # Calculate valuation_amount
            product = workorder.product_id
            production = workorder.production_id

            # Prepare accounts
            accounts = product.product_tmpl_id.get_product_accounts()
            journal_id = accounts['stock_journal'].id
            labor_absorption_acc_id = accounts['labor_absorption_acc_id'].id
            overhead_absorption_acc_id = accounts['overhead_absorption_acc_id'].id
            production_account_id = accounts['production_account_id'].id

            if not labor_absorption_acc_id or not overhead_absorption_acc_id:
                raise UserError(_("Labor absorption and labor burden accounts need to be set on the product %s.") % (product.name,))
                
            if not production_account_id:
                raise UserError(_("WIP account needs to be set on production location"))
                
            # Create data for account move and post them
            
            name = production.name + '-' +  workorder.name
            name = workorder.add_consumption and ('Extra Work: ' + name) or name
            ref = 'Labor - ' + date
            ref1 = 'Burden - ' + date
            
            # labor move lines
            debit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref,
                'partner_id': production.analytic_account_id and production.analytic_account_id.partner_id or False,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': 0.0,
                'debit': cost[0],
                'account_id': production_account_id,
                'analytic_account_id': production.analytic_account_id.id or False
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref,
                'partner_id': production.analytic_account_id and production.analytic_account_id.partner_id or False,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': cost[0],
                'debit': 0.0,
                'account_id': production_account_id,
                'analytic_account_id': production.analytic_account_id.id or False
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
                'partner_id': production.analytic_account_id and production.analytic_account_id.partner_id or False,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': 0.0,
                'debit': cost[1],
                'account_id': production_account_id,
                'analytic_account_id': production.analytic_account_id.id or False
            }
            credit_line_vals = {
                'name': name,
                'product_id': product.id,
                'quantity': 1,
                'product_uom_id': product.uom_id.id,
                'ref': ref1,
                'partner_id': production.analytic_account_id and production.analytic_account_id.partner_id or False,
                'workcenter_id': self.workcenter_id.id or False,
                'credit': cost[1],
                'debit': 0.0,
                'account_id': production_account_id,
                'analytic_account_id': production.analytic_account_id.id or False
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

'''
    def _cal_price(self, consumed_moves):
        """Set a price unit on the finished move according to `consumed_moves`.
        """
        production_cost = ovh_cost = labor_cost = mtl_cost = 0.0
        if consumed_moves:
            mtl_cost = sum([-m.value for m in consumed_moves])
            
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
'''