# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Agreement(models.Model):
    _inherit = "agreement"

    rent_id = fields.Many2one(
        "fleet.rent",
        string="Fleet Rental",
        ondelete="set null",
        help="Related Fleet Rental Contract",
    )
