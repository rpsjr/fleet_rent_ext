# See LICENSE file for full copyright and licensing details.
"""Fleet Rent Model."""

import logging
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF, ustr

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError as err:
    _logger.debug(err)


class FleetRent(models.Model):
    """Fleet Rent Model."""

    _name = "fleet.rent"
    _inherit = "fleet.rent"

    tenant_id = fields.Many2one(
        "res.partner",
        ondelete="set default",
        string="Tenant",
        help="Tenant Name of Rental Vehicle.",
    )

    fleet_tenant_id = fields.Many2one(
        related="tenant_id",
        store=True,
        string="Fleet Tenant",
        help="Tenant Name of Rental Vehicle.",
    )

    rent_product = fields.Many2one(
        "product.product",
        store=True,
        string="Mileage allowance",
        help="Rental mileage allowance.",
    )
    rent_contract = fields.Many2one(
        "contract.contract",
        store=True,
        string="Rental Contract",
        help="Rental contract.",
    )

    deposit_amt_extenso = fields.Text(
        string="Deposit value", compute="_compute_write_deposit_amt"
    )
    rent_amt_extenso = fields.Text(
        string="Deposit value words", compute="_compute_write_rent_amt"
    )
    rent_amt_extenso = fields.Text(
        string="Rent amout value words", compute="_compute_write_rent_amt"
    )
    resale_value_extenso = fields.Text(
        string="Car value words", compute="_compute_write_car_value"
    )
    mileage_allowance_extenso = fields.Text(
        string="Mileage allowance words",
        compute="_compute_write_mileage_allowance_value",
    )

    @api.onchange("tenant_id")
    def sugest_contact_id(self):
        """Method to sugest product contact."""
        for rent in self:
            if rent.tenant_id:
                rent.contact_id = rent.tenant_id

    @api.onchange("tenant_id")
    def _check_tenant(self):
        """Method to check driver marital status and driver id."""
        for rent in self:
            if rent.tenant_id:
                if (
                    rent.tenant_id.d_id is False
                    or rent.tenant_id.marital_status is False
                    or rent.tenant_id.function
                ):
                    Warning(
                        _(
                            f"Please inform {rent.tenant_id.name} driver ID, \n"
                            "function and marital status!"
                        )
                    )

    @api.depends("vehicle_id")
    def _compute_write_car_value(self):
        """Method to write car_value price in words."""
        for rent in self:
            if rent.vehicle_id:
                rent.resale_value_extenso = num2words(
                    rent.vehicle_id.car_value, lang="pt_BR", to="currency"
                )

    @api.depends("deposit_amt")
    def _compute_write_deposit_amt(self):
        """Method to write rent_amt price in words."""
        for rent in self:
            if rent.deposit_amt:
                rent.deposit_amt_extenso = num2words(
                    rent.deposit_amt, lang="pt_BR", to="currency"
                )

    @api.depends("rent_amt")
    def _compute_write_rent_amt(self):
        """Method to write rent_amt_extenso price in words."""
        for rent in self:
            if rent.rent_amt:
                rent.rent_amt_extenso = num2words(
                    rent.rent_amt, lang="pt_BR", to="currency"
                )

    @api.depends("rent_product.mileage_allowance.mileage_allowance_km")
    def _compute_write_mileage_allowance_value(self):
        """Method to write rent_amt_extenso price in words."""
        for rent in self:
            if rent.rent_product.mileage_allowance.mileage_allowance_km:
                rent.mileage_allowance_extenso = num2words(
                    float(rent.rent_product.mileage_allowance.mileage_allowance_km),
                    lang="pt_BR",
                )

    @api.onchange("rent_product")
    def change_rent_amt(self):
        """Method to sugest product price as rent_amt."""
        for rent in self:
            if rent.vehicle_id:
                rent.rent_amt = rent.sudo().rent_product.lst_price

    @api.onchange("vehicle_id")
    def change_rent_product(self):
        """Method to display mileage allowance."""
        # for rent in self:
        #    if rent.rent_product:
        #        rent.rent_product = None
        for rent in self:
            if rent.vehicle_id:
                res = {}
                # res['domain']={'rent_product':[('is_rental_prod', '=', True)]}
                res["domain"] = {
                    "rent_product": [
                        (
                            "vehicle_type_id.id",
                            "=",
                            rent.vehicle_id.sudo().vechical_type_id.id,
                        )
                    ]
                }
                return res

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        for rec in self:
            duplicate_rent = self.env["fleet.rent"].search(
                [
                    ("state", "=", ["draft", "open", "pending"]),
                    ("id", "!=", rec.id),
                    ("vehicle_id", "=", rec.vehicle_id.id),
                ]
            )
            if duplicate_rent:
                raise ValidationError(
                    _(
                        "Vehicle Rent Order is already "
                        "available for this vehicle !! \n Choose other"
                        " vehicle and Prepare new rent order !!"
                    )
                )

    @api.depends("rent_type_id", "date_start")
    def _compute_create_date(self):
        for rent in self:
            if rent.rent_type_id and rent.date_start:
                if rent.rent_type_id.renttype == "Months":
                    rent.date_end = rent.date_start + relativedelta(
                        months=int(rent.rent_type_id.duration) or 1
                    )
                if rent.rent_type_id.renttype == "Years":
                    rent.date_end = rent.date_start + relativedelta(
                        years=int(rent.rent_type_id.duration) or 1
                    )
                if rent.rent_type_id.renttype == "Weeks":
                    rent.date_end = rent.date_start + relativedelta(
                        weeks=int(rent.rent_type_id.duration) or 1
                    )
                if rent.rent_type_id.renttype == "Days":
                    rent.date_end = rent.date_start + relativedelta(
                        days=int(rent.rent_type_id.duration) or 1
                    )
                if rent.rent_type_id.renttype == "Hours":
                    rent.date_end = rent.date_start + relativedelta(
                        hours=int(rent.rent_type_id.duration) or 1
                    )

    def create_rent_schedule(self):
        """Method to create rent schedule Lines."""
        for rent in self:
            for rent_line in rent.rent_schedule_ids:
                if not rent_line.paid and not rent_line.move_check:
                    raise Warning(
                        _(
                            "You can't create new rent "
                            "schedule Please make all related Rent Schedule "
                            "entries paid."
                        )
                    )
            rent_obj = self.env["tenancy.rent.schedule"]
            company = rent.company_id or False
            currency = rent.currency_id or False
            tenent = rent.tenant_id or False
            vehicle = rent.vehicle_id or False
            if rent.date_start and rent.rent_type_id and rent.rent_type_id.renttype:
                interval = int(rent.rent_type_id.duration)
                date_st = rent.date_start
                if not rent.rent_type_id.duration:
                    rent_number = re.findall(r"\d+", rent.name)[0]
                    params = self.env["ir.config_parameter"].sudo()
                    fiscal_postion_id = int(
                        params.get_param("fleet_rent.fiscal_postion_id")
                    )
                    rent.rent_contract = (
                        self.env["contract.contract"]
                        .create(
                            {
                                "code": rent.name or False,
                                "commercial_partner_id": tenent.id or False,
                                "company_id": company.id or rent.company_id.id or False,
                                "contract_type": "sale",
                                "create_date": rent.contract_dt or False,
                                "create_invoice_visibility": True,
                                "currency_id": currency and currency.id or False,
                                "date_end": False,
                                "date_start": rent.contract_dt or False,
                                "display_name": f"Locação {rent.id}",
                                "fiscal_position_id": fiscal_postion_id,
                                "invoice_partner_id": tenent.id or False,
                                # "is_terminated": False,
                                # 'journal_id': 1,
                                # "last_date_invoiced": False,
                                # "line_recurrence": False,
                                # "manual_currency_id": False,
                                "name": f"Locação {rent_number}",
                                "partner_id": tenent and tenent.id or False,
                                "payment_term_id": rent.rent_type_id.payment_term.id,
                                "pricelist_id": 1,
                                # "recurring_interval": 1,
                                # "recurring_invoicing_offset": 0,
                                # "recurring_invoicing_type": "pre-paid",
                                # "recurring_rule_type": "weekly",
                                # "terminate_date": False,
                                "origin_doc_fleet": rent.id,
                            }
                        )
                        .id
                    )
                    self.env["contract.line"].create(
                        {
                            # "active": True,
                            "auto_renew_interval": 1,
                            "auto_renew_rule_type": "yearly",
                            # "automatic_price": False,
                            "company_id": company.id or rent.company_id.id or False,
                            "contract_id": rent.rent_contract.id,
                            "create_invoice_visibility": True,
                            # "date_end": False,
                            # "date_start": "2021-02-05",
                            # "date_start": "2021-02-05",
                            "discount": 0.0,
                            "display_name": f"{rent.rent_product.name} {rent.vehicle_id}",
                            # "is_auto_renew": False,
                            "is_cancel_allowed": True,
                            # "is_canceled": False,
                            # "is_plan_successor_allowed": False,
                            # "is_recurring_note": False,
                            # "is_stop_allowed": True,
                            # "is_stop_plan_successor_allowed": True,
                            # "is_un_cancel_allowed": False,
                            # "last_date_invoiced": False,
                            # "manual_renew_needed": False,
                            "name": rent.rent_product.name,
                            "note_invoicing_mode": "with_previous_line",
                            # "predecessor_contract_line_id": False,
                            "price_unit": rent.rent_amt / 7,
                            "product_id": rent.rent_product.id,  # [18, 'Opel/Agila/PKO9E55']
                            # "qty_type": "fixed",
                            "quantity": 7.0,
                            "recurring_interval": 1,
                            "recurring_invoicing_offset": 0,
                            "recurring_invoicing_type": "pre-paid",
                            "recurring_rule_type": "weekly",
                            # 'specific_price': 54.2857142857,
                            "state": "in-progress",
                            # "successor_contract_line_id": False,
                            # "termination_notice_date": False,
                            "termination_notice_interval": 1,
                            "termination_notice_rule_type": "monthly",
                            "uom_id": 1,  # [21, 'Dia']
                        }
                    )
                elif rent.rent_type_id.renttype == "Months":
                    for _i in range(0, interval):
                        date_st = date_st + relativedelta(months=int(1))
                        rent_obj.create(
                            {
                                "start_date": date_st.strftime(DTF),
                                "amount": rent.rent_amt,
                                "vehicle_id": vehicle and vehicle.id or False,
                                "fleet_rent_id": rent.id,
                                "currency_id": currency and currency.id or False,
                                "rel_tenant_id": tenent and tenent.id or False,
                            }
                        )
                elif rent.rent_type_id.renttype == "Years":
                    for _i in range(0, interval):
                        date_st = date_st + relativedelta(years=int(1))
                        rent_obj.create(
                            {
                                "start_date": date_st.strftime(DTF),
                                "amount": rent.rent_amt,
                                "vehicle_id": vehicle and vehicle.id or False,
                                "fleet_rent_id": rent.id,
                                "currency_id": currency and currency.id or False,
                                "rel_tenant_id": tenent and tenent.id or False,
                            }
                        )
                elif rent.rent_type_id.renttype == "Weeks":
                    for _i in range(0, interval):
                        date_st = date_st + relativedelta(weeks=int(1))
                        rent_obj.create(
                            {
                                "start_date": date_st.strftime(DTF),
                                "amount": rent.rent_amt,
                                "vehicle_id": vehicle and vehicle.id or False,
                                "fleet_rent_id": rent.id,
                                "currency_id": currency and currency.id or False,
                                "rel_tenant_id": tenent and tenent.id or False,
                            }
                        )
                elif rent.rent_type_id.renttype == "Days":
                    rent_obj.create(
                        {
                            "start_date": date_st.strftime(DTF),
                            "amount": rent.rent_amt * interval,
                            "vehicle_id": vehicle and vehicle.id or False,
                            "fleet_rent_id": rent.id,
                            "currency_id": currency and currency.id or False,
                            "rel_tenant_id": tenent and tenent.id or False,
                        }
                    )
                elif rent.rent_type_id.renttype == "Hours":
                    rent_obj.create(
                        {
                            "start_date": date_st.strftime(DTF),
                            "amount": rent.rent_amt * interval,
                            "vehicle_id": vehicle and vehicle.id or False,
                            "fleet_rent_id": rent.id,
                            "currency_id": currency and currency.id or False,
                            "rel_tenant_id": tenent and tenent.id or False,
                        }
                    )
                # cr_rent_btn is used to hide rent schedule button.
                rent.cr_rent_btn = True

    def action_deposite_receive(self):
        """Method to open the related payment form view."""
        for rent in self:

            if rent.deposit_amt < 1:
                raise Warning(
                    _(
                        "Deposit amount should not be zero.\n"
                        "Please Enter Deposit Amount."
                    )
                )

            deposit_inv_ids = self.env["account.move"].search(
                [
                    ("fleet_rent_id", "=", rent.id),
                    ("type", "=", "out_invoice"),
                    ("state", "in", ["draft", "open", "in_payment"]),
                    ("is_deposit_inv", "=", True),
                ]
            )
            if deposit_inv_ids:
                raise Warning(
                    _(
                        "Deposit invoice is already Pending\n"
                        "Please proceed that deposit invoice first"
                    )
                )

            params = self.env["ir.config_parameter"].sudo()
            deposit_product_id = int(params.get_param("fleet_rent.deposit_product_id"))
            int(params.get_param("fleet_rent.fiscal_postion_id"))
            inv_line_values = {
                "product_id": deposit_product_id or False,
                # 'name': 'Deposit Receive' or "",
                # 'origin': rent.name or "",
                "quantity": 1,
                # 'account_id': rent.vehicle_id and rent.vehicle_id.expence_acc_id and
                # rent.vehicle_id.expence_acc_id.id or False,
                "price_unit": rent.deposit_amt or 0.00,
                "fleet_rent_id": rent.id,
            }
            invoice_id = rent.env["account.move"].create(
                {
                    "type": "out_invoice",
                    "ref": rent.name,
                    "partner_id": rent.tenant_id and rent.tenant_id.id or False,
                    "invoice_line_ids": [(0, 0, inv_line_values)],
                    "invoice_date": datetime.now().strftime(DTF) or False,
                    "fleet_rent_id": rent.id,
                    "is_deposit_inv": True,
                    "l10n_br_edoc_policy": "",
                }
            )
            rent.write({"invoice_id": invoice_id.id})
            return True

    def action_deposite_return(self):
        """Method to return deposite."""
        for rent in self:
            deposit_inv_ids = self.env["account.move"].search(
                [
                    ("fleet_rent_id", "=", rent.id),
                    ("type", "=", "out_refund"),
                    ("state", "in", ["draft", "open", "in_payment"]),
                    ("is_deposit_return_inv", "=", True),
                ]
            )
            if deposit_inv_ids:
                raise Warning(
                    _(
                        "Deposit Return invoice is already Pending\n"
                        "Please proceed that Return invoice first"
                    )
                )

            self.ensure_one()
            vehicle = rent.vehicle_id or False
            purch_journal = rent.env["account.journal"].search(
                [("type", "=", "sale")], limit=1
            )
            if vehicle and not vehicle.expence_acc_id:
                raise Warning(
                    _(
                        "Please Configure Expense Account in "
                        "Vehicle Registration form !!"
                    )
                )

            params = self.env["ir.config_parameter"].sudo()
            deposit_product_id = int(params.get_param("fleet_rent.deposit_product_id"))
            int(params.get_param("fleet_rent.fiscal_postion_id"))
            inv_line_values = {
                "product_id": deposit_product_id,
                "name": "Devolução" or "",
                "quantity": 1,
                # 'account_id': vehicle and vehicle.expence_acc_id and
                #              vehicle.expence_acc_id.id or False,
                "price_unit": rent.deposit_amt or 0.00,
                "fleet_rent_id": rent.id,
            }
            invoice_id = rent.env["account.move"].create(
                {
                    "invoice_origin": "Deposit Return For " + rent.name or "",
                    "type": "out_refund",
                    "ref": rent.name,
                    # 'property_id': vehicle and vehicle.id or False,
                    "partner_id": rent.tenant_id and rent.tenant_id.id or False,
                    # 'account_id': rent.tenant_id and
                    # rent.tenant_id.property_account_payable_id.id or False,
                    "invoice_line_ids": [(0, 0, inv_line_values)],
                    "invoice_date": datetime.now().strftime(DTF) or False,
                    "fleet_rent_id": rent.id,
                    "is_deposit_return_inv": True,
                    "journal_id": purch_journal and purch_journal.id or False,
                    "l10n_br_edoc_policy": "",
                }
            )

            rent.write({"invoice_id": invoice_id.id})
        return True

    def action_rent_confirm(self):
        """Method to confirm rent status."""
        for rent in self:
            rent_vals = {"state": "open"}
            if rent.rent_amt < 1:
                raise ValidationError(
                    _(
                        "Rental Vehicle Rent amount should be greater than zero !! "
                        "Please add 'Rental Vehicle Rent' amount !!"
                    )
                )
            if not rent.name or rent.name == "New":
                seq = self.env["ir.sequence"].next_by_code("fleet.rent")
                rent_vals.update({"name": seq})
            rent.write(rent_vals)
            rent.vehicle_id.state = "rent"

    def action_rent_done(self):
        """Method to Change rent state to done."""
        rent_sched_obj = self.env["tenancy.rent.schedule"]
        for rent in self:
            if not rent.rent_schedule_ids:
                raise ValidationError(
                    _(
                        "Without Rent schedule you can not done the rent."
                        "\nplease first create the rent schedule."
                    )
                )
            if rent.rent_schedule_ids:
                rent_schedule = rent_sched_obj.search(
                    [("paid", "=", False), ("id", "in", rent.rent_schedule_ids.ids)]
                )
                if rent_schedule:
                    raise ValidationError(
                        _(
                            "Scheduled Rents is remaining."
                            "\nplease first pay scheduled rents.!!"
                        )
                    )
                rent.state = "done"
                rent.vehicle_id.state = "released"

    def action_set_to_draft(self):
        """Method to Change rent state to close."""
        for rent in self:
            if rent.state == "open" and rent.rent_schedule_ids:
                raise Warning(
                    _(
                        "You can not move rent to draft "
                        "stage because rent schedule is already created !!"
                    )
                )
            rent.state = "draft"
            rent.vehicle_id.state = "rent"


class RentType(models.Model):
    """Rent Type Model."""

    _name = "rent.type"
    _inherit = "rent.type"

    @api.model
    def create(self, vals):
        """Overridden Method."""
        if vals.get("duration") == 0 and vals.get("renttype") == "Hours":
            raise ValidationError(
                _("You Can't Enter Duration Less " "Than One(1)e for Hours rent type.")
            )
        return models.Model.create(self, vals)

    duration = fields.Integer(string="Duration", default=0)
    renttype = fields.Selection(
        [
            ("Hours", "Hours"),
            ("Days", "Days"),
            ("Weeks", "Weeks"),
            ("Months", "Months"),
            ("Years", "Years"),
        ],
        default="Weeks",
        string="Rent Type",
    )
    payment_term = fields.Many2one(
        "account.payment.term",
        store=True,
        string="Payment term",
        help="Rental contract payment term.",
    )

    @api.depends("duration", "renttype")
    def name_get(self):
        """Name get Method."""
        res = []
        for rec in self:
            rec_str = ""
            if rec.duration:
                rec_str += ustr(rec.duration)
            else:
                rec_str += " " + "Auto-renew"
            if rec.renttype:
                rec_str += " " + rec.renttype
            if rec.payment_term:
                rec_str += " " + rec.payment_term.name
            res.append((rec.id, rec_str))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Name Search Method."""
        args = args or []
        args += [
            "|",
            ("duration", operator, name),
            ("renttype", operator, name),
            ("payment_term", operator, name),
        ]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

    @api.onchange("duration", "renttype")
    def onchange_renttype_name(self):
        """Onchange Rent Type Name."""
        full_name = ""
        for rec in self:
            if rec.duration:
                full_name += ustr(rec.duration)
            else:
                full_name += " " + "Auto-renew"
            if rec.renttype:
                full_name += " " + ustr(rec.renttype)
            if rec.payment_term:
                full_name += " " + ustr(rec.payment_term.name)
            rec.name = full_name
