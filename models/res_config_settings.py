# -*- coding: utf-8 -*-
#See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    deposit_product = fields.Many2one('product.product',
                                  string='Deposit product',
                                  help="Standard deposit product usend in accounting",
                                  config_parameter='fleet_rent.deposit_product')
