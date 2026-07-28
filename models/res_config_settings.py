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
    fleet_rent_type_id = fields.Many2one(
        "rent.type",
        string="Default Rent Type",
        help="Default rent type for vehicle rentals",
        config_parameter="fleet_rent.fleet_rent_type_id",
    )
    fleet_rental_deposit_formula = fields.Char(
        string="Deposit Amount Formula",
        help="Formula to calculate the default deposit amount (e.g. 'rent_amt * 2'). Available variables: rent, rent_amt, vehicle_id, rent_type_id, rent_product.",
        config_parameter="fleet_rent.fleet_rental_deposit_formula",
    )
    fleet_rental_payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Default Payment Term",
        help="Default payment term used for deposit invoices and rentals",
        config_parameter="fleet_rent.fleet_rental_payment_term_id",
    )



