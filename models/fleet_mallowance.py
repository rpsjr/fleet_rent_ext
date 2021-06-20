# See LICENSE file for full copyright and licensing details.
"""Fleet Rent Model."""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF

class MileageAllowance(models.Model):
    """Fleet Rent Mileage Allowance Model."""
    _name = "fleet.mallowance"
    #_inherit = ['mail.thread']
    _description = "Mileage Allowance"

    @api.onchange('mileage_allowance_km', 'uom_id')
    def onchange_mallowance_name(self):
        """Onchange Rent Type Name."""
        full_name = ''
        for rec in self:
            if rec.mileage_allowance_km:
                full_name += ustr(rec.mileage_allowance_km) + 'km/'
            if rec.uom_id:
                full_name += ustr(rec.uom_id.name)
            rec.name = full_name

    name = fields.Char(string="Name")

    mileage_allowance_km = fields.Integer(
                            string='Mileage Allowance Value',
                            help='Odometer measure of the vehicle at \
                            the moment of this log')
    uom_id = fields.Many2one('uom.uom',
                                 string='Unit of measurement',
                                 help="Unit of measurement.")
    extra_km_price = fields.Float(string='Preço quilometro excedente',
                            currency_field='currency_id',
                            help="Preço quilometro excedente ao limite da franquia.",
                            copy=False)
