# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ["res.config.settings"]

    deposit_product_id = fields.Many2one(
        "product.product",
        string="Deposit product",
        help="Standard deposit product usend in accounting",
        config_parameter="fleet_rent.deposit_product_id",
    )
    fleet_rent_fiscal_postion_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        help="Standard fiscal position to rent contract",
        config_parameter="fleet_rent.fiscal_postion_id",
    )
