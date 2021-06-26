# See LICENSE file for full copyright and licensing details.
"""Res Users Models."""

from odoo import fields, models


class ResPartnerExtended(models.Model):
    """Model res partner extended."""

    _inherit = "res.partner"

    d_id = fields.Char(string="ID-Card", size=11)
    is_driver = fields.Boolean(string="Is Driver")
    insurance = fields.Boolean(string="Insurance")
