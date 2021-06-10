# See LICENSE file for full copyright and licensing details.
"""Fleet Rent Model."""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import ustr,date_utils, DEFAULT_SERVER_DATE_FORMAT as DF, \
    DEFAULT_SERVER_DATETIME_FORMAT as DTF

import re
try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)

class FleetRent(models.Model):
    """Fleet Rent Model."""
    _name = "fleet.rent"
    _inherit = "fleet.rent"

    tenant_id = fields.Many2one('res.partner', ondelete='set default',
                                string='Tenant',
                                help="Tenant Name of Rental Vehicle.")

    fleet_tenant_id = fields.Many2one(related="tenant_id",
                                      store=True,
                                      string='Fleet Tenant',
                                      help="Tenant Name of Rental Vehicle.")

    rent_product = fields.Many2one('product.product',
                                      store=True,
                                      string='Mileage allowance',
                                      help="Rental mileage allowance.")
    rent_contract = fields.Many2one('contract.contract',
                                      store=True,
                                      string='Rental Contract',
                                      help="Rental contract.")

    deposit_amt_extenso = fields.Text(string="Deposit value",
                                    compute='_write_deposit_amt')
    rent_amt_extenso = fields.Text(string="Deposit value words",
                                   compute='_write_rent_amt')
    rent_amt_extenso = fields.Text(string="Rent amout value words",
                                   compute='_write_rent_amt')
    resale_value_extenso = fields.Text(string="Car value words",
                                   compute='_write_car_value')
    mileage_allowance_extenso = fields.Text(string="Mileage allowance words",
                                    compute='_write_mileage_allowance_value')

    @api.onchange('tenant_id')
    def sugest_contact_id(self):
        """Method to sugest product contact."""
        for rent in self:
            if rent.tenant_id:
                rent.contact_id = rent.tenant_id

    @api.onchange('tenant_id')
    def _check_tenant(self):
        """Method to check driver marriage status and driver id."""
        for rent in self:
            if rent.tenant_id:
                if rent.tenant_id.d_id == False or rent.tenant_id.marriage == False:
                    Warning(_(f'Please inform {rent.tenant_id.name} driver ID and marriage status'))

    @api.depends('vehicle_id')
    def _write_car_value(self):
        """Method to write car_value price in words."""
        for rent in self:
            if rent.vehicle_id:
                rent.resale_value_extenso = num2words(rent.vehicle_id.car_value, lang='pt_BR', to='currency')

    @api.depends('deposit_amt')
    def _write_deposit_amt(self):
        """Method to write rent_amt price in words."""
        for rent in self:
            if rent.deposit_amt:
                rent.deposit_amt_extenso = num2words(rent.deposit_amt, lang='pt_BR', to='currency')

    @api.depends('rent_amt')
    def _write_rent_amt(self):
        """Method to write rent_amt_extenso price in words."""
        for rent in self:
            if rent.rent_amt:
                rent.rent_amt_extenso = num2words(rent.rent_amt, lang='pt_BR', to='currency')

    @api.depends('rent_product.mileage_allowance.mileage_allowance_km')
    def _write_mileage_allowance_value(self):
        """Method to write rent_amt_extenso price in words."""
        for rent in self:
            if rent.rent_product.mileage_allowance.mileage_allowance_km:
                rent.mileage_allowance_extenso = num2words(float(rent.rent_product.mileage_allowance.mileage_allowance_km), lang='pt_BR')

    @api.onchange('rent_product')
    def change_rent_amt(self):
        """Method to sugest product price as rent_amt."""
        for rent in self:
            if rent.vehicle_id:
                rent.rent_amt = rent.sudo().rent_product.lst_price

    @api.onchange('vehicle_id')
    def change_rent_product(self):
        """Method to display mileage allowance."""
        #for rent in self:
        #    if rent.rent_product:
        #        rent.rent_product = None
        for rent in self:
            if rent.vehicle_id:
                res = {}
                #res['domain']={'rent_product':[('is_rental_prod', '=', True)]}
                res['domain']={'rent_product':[('vehicle_type_id.id', '=', rent.vehicle_id.sudo().vechical_type_id.id)]}
                #res['domain']={'rent_product':[('vehicle_type_id', '=', rent.vehicle_id.sudo().vechical_type_id.id), ('is_rental_prod', '=', True)]}
                return res

    def create_rent_schedule(self):
        """Method to create rent schedule Lines."""
        for rent in self:
            for rent_line in rent.rent_schedule_ids:
                if not rent_line.paid and not rent_line.move_check:
                    raise Warning(_('You can\'t create new rent '
                                    'schedule Please make all related Rent Schedule '
                                    'entries paid.'))
            rent_obj = self.env['tenancy.rent.schedule']
            company =  rent.company_id or False
            currency = rent.currency_id or False
            tenent = rent.tenant_id or False
            vehicle = rent.vehicle_id or False
            if rent.date_start and rent.rent_type_id and \
                    rent.rent_type_id.renttype:
                interval = int(rent.rent_type_id.duration)
                date_st = rent.date_start
                if not rent.rent_type_id.duration:
                    rent_number = re.findall("\d+", rent.name)[0]
                    rent.rent_contract = self.env['contract.contract'].create({
                         'code': rent.name or false,
                         'commercial_partner_id': tenent.id or False,
                         'company_id': company.id or rent.company_id.id or false,
                         'contract_type': 'sale',
                         'create_date': rent.contract_dt or False,
                         'create_invoice_visibility': True,
                         'currency_id': currency and currency.id or False,
                         'date_end': False,
                         'date_start': rent.contract_dt or False,
                         'display_name': f'Locação {rent.id}',
                         'fiscal_position_id': False,
                         'invoice_partner_id': tenent.id or False,
                         'is_terminated': False,
                         #'journal_id': 1,
                         'last_date_invoiced': False,
                         'line_recurrence': False,
                         'manual_currency_id': False,
                         'name': f'Locação {rent_number}',
                         'partner_id': tenent and tenent.id or False,
                         'payment_term_id': rent.rent_type_id.payment_term.id,
                         'pricelist_id': 1,
                         'recurring_interval': 1,
                         'recurring_invoicing_offset': 0,
                         'recurring_invoicing_type': 'pre-paid',
                         'recurring_rule_type': 'weekly',
                         'terminate_date': False,
                         'origin_doc_fleet': rent.id,
                    }).id
                    line = self.env['contract.line'].create({
                         'active': True,
                         'auto_renew_interval': 1,
                         'auto_renew_rule_type': 'yearly',
                         'automatic_price': False,
                         'company_id': company.id or rent.company_id.id or false,
                         'contract_id': rent.rent_contract.id,
                         'create_invoice_visibility': True,
                         'date_end': False,
                         'date_start': '2021-02-05',
                         'discount': 0.0,
                         'display_name': f'{rent.rent_product.name} {rent.vehicle_id}',
                         'is_auto_renew': False,
                         'is_cancel_allowed': True,
                         'is_canceled': False,
                         'is_plan_successor_allowed': False,
                         'is_recurring_note': False,
                         'is_stop_allowed': True,
                         'is_stop_plan_successor_allowed': True,
                         'is_un_cancel_allowed': False,
                         'last_date_invoiced': False,
                         'manual_renew_needed': False,
                         'name':rent.rent_product.name,
                         'note_invoicing_mode': 'with_previous_line',
                         'predecessor_contract_line_id': False,
                         'price_unit': rent.rent_amt/7,
                         'product_id': rent.rent_product.id, #[18, 'Opel/Agila/PKO9E55']
                         'qty_type': 'fixed',
                         'quantity': 7.0,
                         'recurring_interval': 1,
                         'recurring_invoicing_offset': 0,
                         'recurring_invoicing_type': 'pre-paid',
                         'recurring_rule_type': 'weekly',
                         #'specific_price': 54.2857142857,
                         'state': 'in-progress',
                         'successor_contract_line_id': False,
                         'termination_notice_date': False,
                         'termination_notice_interval': 1,
                         'termination_notice_rule_type': 'monthly',
                         'uom_id': 1, #[21, 'Dia']
                    })
                elif rent.rent_type_id.renttype == 'Months':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(months=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                elif rent.rent_type_id.renttype == 'Years':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(years=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                elif rent.rent_type_id.renttype == 'Weeks':
                    for i in range(0, interval):
                        date_st = date_st + relativedelta(weeks=int(1))
                        rent_obj.create({
                            'start_date': date_st.strftime(DTF),
                            'amount': rent.rent_amt,
                            'vehicle_id': vehicle and vehicle.id or False,
                            'fleet_rent_id': rent.id,
                            'currency_id': currency and currency.id or False,
                            'rel_tenant_id': tenent and tenent.id or False
                        })
                elif rent.rent_type_id.renttype == 'Days':
                    rent_obj.create({
                        'start_date': date_st.strftime(DTF),
                        'amount': rent.rent_amt * interval,
                        'vehicle_id': vehicle and vehicle.id or False,
                        'fleet_rent_id': rent.id,
                        'currency_id': currency and currency.id or False,
                        'rel_tenant_id': tenent and tenent.id or False
                    })
                elif rent.rent_type_id.renttype == 'Hours':
                    rent_obj.create({
                        'start_date': date_st.strftime(DTF),
                        'amount': rent.rent_amt * interval,
                        'vehicle_id': vehicle and vehicle.id or False,
                        'fleet_rent_id': rent.id,
                        'currency_id': currency and currency.id or False,
                        'rel_tenant_id': tenent and tenent.id or False
                    })
                # cr_rent_btn is used to hide rent schedule button.
                rent.cr_rent_btn = True

class RentType(models.Model):
    """Rent Type Model."""

    _name = "rent.type"
    _inherit = "rent.type"

    @api.model
    def create(self, vals):
        """Overridden Method."""
        if vals.get('duration') == 0 and vals.get('renttype') == 'Hours':
            raise ValidationError("You Can't Enter Duration Less "
                                          "Than One(1)e for Hours rent type.")
        return models.Model.create(self, vals)

    duration = fields.Integer(string="Duration", default=0)
    renttype = fields.Selection(
        [('Hours', 'Hours'),
         ('Days', 'Days'),
         ('Weeks', 'Weeks'),
         ('Months', 'Months'),
         ('Years', 'Years')],
        default='Weeks',
        string='Rent Type')
    payment_term = fields.Many2one('account.payment.term',
                                  store=True,
                                  string='Payment term',
                                  help="Rental contract payment term.")
