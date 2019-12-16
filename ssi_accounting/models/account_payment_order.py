# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    @api.multi
    def action_send_email(self):
        for line in self.bank_line_ids:
            partner = line.partner_id
            email = partner.ach_email
            email_alt = partner.ach_email_alt
            if email and email.strip():
                mail_template = self.env.ref('ssi_accounting.ssi_mail_template_payment_notify')
                mail_values = mail_template.generate_email(line.id)
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()
                # mail message's subject
                msg = "Email sent to:" + email
                self.message_post(body=msg)
            else:
                raise UserError(_('Could not send mail to partner because it does not have any email address defined'))
        return True


