# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceJobValidate(models.TransientModel):
    _name = 'account.invoice.job.validate'
    _description = 'Wizard Invoice Job Validate'

    is_valid = fields.Boolean(default=True)
    warning_note = fields.Text()

    @api.model
    def default_get(self, fields):
        context = dict(self._context or {})
        res = super(AccountInvoiceJobValidate, self).default_get(fields)
        mrp_pool = self.env['mrp.production']
        warning_description = ''
        valid = True
        for invoice in self.env['account.invoice'].browse(context.get('active_ids')):
            for line in invoice.invoice_line_ids:
                if line.ssi_job_id and \
                        line.product_id and \
                        line.product_id.type == 'consu' and \
                        line.product_id.product_tmpl_id.is_job_type:
                    # Search unique MO with product_id and ssi_job_id
                    mo_id = mrp_pool.search(
                        [('ssi_job_id', '=', line.ssi_job_id.id),
                         ('product_id', '=', line.product_id.id),
                         ('state', '!=', 'done')], limit=1)
                    if mo_id:
                        message = "<br/><li>Manufacture Order <b>{0}</b> - " \
                                  "corresponding to <b>{1}</b></li>".format(
                            mo_id.name, line.product_id.name)
                        warning_description += message
                        valid = False
        if not valid:
            # Update wizard values
            res.update({
                'is_valid': valid,
                'warning_note': warning_description,
            })
        return res
    
    @api.multi
    def invoice_validate(self):
        context = dict(self._context or {})
        for invoice in self.env['account.invoice'].browse(
                context.get('active_ids')):
            invoice.action_invoice_open()
        return True
