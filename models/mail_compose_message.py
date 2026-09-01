# See LICENSE file for full copyright and licensing details.

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def action_send_mail(self):
        """Override to update fleet.rent state to proposal_sent upon sending proposal email."""
        res = super(MailComposeMessage, self).action_send_mail()
        for wizard in self:
            if wizard.model == "fleet.rent" and wizard.res_id:
                rent = self.env["fleet.rent"].browse(wizard.res_id)
                if rent.exists() and rent.state in ("draft", "crlv_shared"):
                    rent.action_proposal_sent()
        return res
