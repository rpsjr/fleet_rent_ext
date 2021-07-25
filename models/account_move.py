import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, RedirectWarning, UserError, ValidationError
from odoo.tools import (
    date_utils,
    email_escape_char,
    email_re,
    email_split,
    float_compare,
    float_is_zero,
    safe_eval,
)
from odoo.tools.misc import format_date, formatLang, get_lang

_logger = logging.getLogger(__name__)


# class my_class(osv.osv):
#    # in the code when needed :
#    _logger.error("my variable : %r", my_var)
#    # Or
#    msg = "This is my error message : " % my_var
#    _logger.error(msg)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _rent_mail_invoice_cron(self):
        """Method to send invoice by e-mail rent."""

        template = self.env.ref(
            "fleet_rent_ext.email_rent_invoice_template", raise_if_not_found=False
        )
        invoices = self.search(
            [
                ("payment_journal_id", "=", 18),
                ("state", "=", "posted"),
                ("invoice_date", "=", fields.Datetime.now().date()),
            ]
        )

        if invoices:
            for posted_invoice in invoices:
                boleto_id = None
                attachment_ids = []
                if posted_invoice.transaction_ids:
                    for payment_transction in posted_invoice.transaction_ids:
                        payment_transction.generate_pdf_boleto()
                        if payment_transction.pdf_boleto_id:
                            boleto_id = (
                                payment_transction.pdf_boleto_id
                                and payment_transction.pdf_boleto_id.id
                                or False
                            )
                            attachment_ids.append(
                                (
                                    4,
                                    boleto_id,
                                )
                            )

                _logger.error("my posted_invoice.name : %r", posted_invoice.name)
                _logger.error("my boleto_idx1 : %r", boleto_id)
                if boleto_id:
                    template.attachment_ids = attachment_ids
                template.send_mail(posted_invoice.id, force_send=True)
                template.attachment_ids = [(5,)]
