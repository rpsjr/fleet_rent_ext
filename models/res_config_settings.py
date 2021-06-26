# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    fleet_rental_deposit_product_id = fields.Many2one(
        "product.product",
        string="Deposit product",
        help="Standard deposit product usend in accounting",
        config_parameter="fleet_rent.fleet_rental_deposit_product_id",
    )
