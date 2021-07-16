from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools.translate import _


class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = "contract.contract"

    origin_doc_fleet = fields.Many2one(
        string="Contract Proposal",
        comodel_name="fleet.rent",
        readonly=True,
        ondelete="cascade",
    )

    def _prepare_invoice(self, date_invoice, journal=None):
        """Prepare in a Form the values for the generated invoice record.

        :return: A tuple with the vals dictionary and the Form with the
          preloaded values for being used in lines.
        """
        invoice_vals, move_form = super()._prepare_invoice(date_invoice)
        if self.payment_mode_id.id == 1:  # se é boleto banto inter
            payment_journal_id = 18
        else:
            payment_journal_id = None
        invoice_vals.update(
            {
                "auto_post": True,
                "l10n_br_edoc_policy": None,
                "payment_journal_id": payment_journal_id,
            }
        )
        return invoice_vals, move_form
