from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form
from odoo.tools.translate import _

class ContractContract(models.Model):
    _name = "contract.contract"
    _inherit = "contract.contract"

    origin_doc_fleet = fields.Many2one(
        string="Contract Proposal", comodel_name="fleet.rent", readonly=True, ondelete="cascade",
    )
