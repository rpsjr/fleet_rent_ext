# See LICENSE file for full copyright and licensing details.
"""Fleet Rent Model."""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF

class ProductTemplate(models.Model):
    """product template model."""

    _inherit = 'product.template'

    is_rental_prod = fields.Boolean('Locação de Veículo')
    vehicle_type_id = fields.Many2one('vehicle.type',
                                      string='Vehicle Type')
    mileage_control = fields.Boolean('Controle de quilometragem')
    mileage_allowance = fields.Many2one('fleet.mallowance',
                                 string='Mileage Allowance category',
                                 help="Mileage Allowance.")
