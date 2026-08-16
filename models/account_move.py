import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _rent_mail_invoice_cron(self):
        """Method to send invoice by e-mail rent."""

        template = self.env.ref(
            "fleet_rent_ext.email_rent_invoice_template", raise_if_not_found=False
        )
        if not template:
            _logger.error(
                "Mail template 'fleet_rent_ext.email_rent_invoice_template' not found."
            )
            return

        # Ensure shared template has no lingering attachments
        if template.attachment_ids:
            template.attachment_ids = [(5,)]

        invoices = self.search(
            [
                ("payment_journal_id", "=", 18),
                ("state", "=", "posted"),
                ("invoice_sent", "!=", True),
            ]
        )

        for posted_invoice in invoices:
            try:
                if posted_invoice.state != "posted" or posted_invoice.invoice_sent:
                    continue

                attachment_ids = []
                valid_transactions = posted_invoice.transaction_ids.filtered(
                    lambda t: t.state not in ("cancel", "error")
                )
                for payment_transction in valid_transactions:
                    if (
                        not payment_transction.pdf_boleto_id
                        and payment_transction.acquirer_reference
                    ):
                        try:
                            payment_transction.generate_pdf_boleto()
                        except Exception as tx_err:
                            _logger.warning(
                                "Could not generate PDF boleto for transaction %s "
                                "(Invoice %s): %s",
                                payment_transction.id,
                                posted_invoice.name,
                                tx_err,
                            )
                    if payment_transction.pdf_boleto_id:
                        attachment_ids.append(payment_transction.pdf_boleto_id.id)

                email_values = {}
                if attachment_ids:
                    email_values["attachment_ids"] = [
                        (4, aid) for aid in sorted(set(attachment_ids))
                    ]

                _logger.info(
                    "Sending invoice email: %s (ID: %s, Boleto Attachments: %r)",
                    posted_invoice.name,
                    posted_invoice.id,
                    attachment_ids,
                )

                mail_id = template.send_mail(
                    posted_invoice.id,
                    force_send=True,
                    raise_exception=True,
                    email_values=email_values or None,
                )
                mail = self.env["mail.mail"].browse(mail_id)
                if mail and mail.state == "sent":
                    posted_invoice.write({"invoice_sent": True})
                    self._cr.commit()
                    _logger.info(
                        "Successfully processed invoice email for %s (ID: %s)",
                        posted_invoice.name,
                        posted_invoice.id,
                    )
                else:
                    failure_reason = mail.failure_reason if mail else "No mail record"
                    _logger.warning(
                        "Email for invoice %s (ID: %s) was not sent (status: %s, reason: %s)",
                        posted_invoice.name,
                        posted_invoice.id,
                        mail.state if mail else "None",
                        failure_reason,
                    )
                    self._cr.rollback()
            except Exception as exc:
                self._cr.rollback()
                _logger.exception(
                    "Failed to process invoice email for %s (ID: %s): %s",
                    posted_invoice.name,
                    posted_invoice.id,
                    exc,
                )
