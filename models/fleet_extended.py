# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import json
import logging
from datetime import date, datetime

import requests
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, Warning
from odoo.tools import misc

# import apifipecons
from . import apifipe as apifipecons

_logger = logging.getLogger(__name__)


class FleetOperations(models.Model):
    """Fleet Operations model."""

    _inherit = "fleet.vehicle"
    _order = "id desc"
    _rec_name = "name"

    @api.depends("fipe_id", "model_year")
    def _compute_result_apifipe(self):
        """Method to retrive vehicle FIPE information using API."""
        for record in self:
            result_apifipe = {}
            if record.model_year and record.fipe_id:
                result_apifipe = apifipecons.apiFIPE().getCodigoMarca(
                    record.model_year, record.fipe_id
                )
                record.result_apifipe = result_apifipe
            if "Valor" in result_apifipe:
                record.resale_value = float(
                    result_apifipe["Valor"][3:].replace(".", "").replace(",", ".")
                )
                record.fipe_model = result_apifipe["Modelo"]
            else:
                record.result_apifipe = record.result_apifipe
                record.resale_value = record.resale_value
                record.fipe_model = record.fipe_model

    @api.depends("result_apifipe")
    def _compute_fipe_model(self):
        """Method to retrive vehicle FIPE model using API."""
        for record in self:
            if record.result_apifipe and "Modelo" in record.result_apifipe:
                record.fipe_model = eval(record.result_apifipe)["Modelo"]
            else:
                record.fipe_model = record.fipe_model

    @api.depends("result_apifipe")
    def _compute_resale_value(self):
        """Method to retrive vehicle FIPE value using API."""
        for record in self:
            if record.result_apifipe and "Valor" in record.result_apifipe:
                record.resale_value = float(
                    eval(record.result_apifipe)["Valor"][3:]
                    .replace(".", "")
                    .replace(",", ".")
                )
            else:
                record.resale_value = record.resale_value

    fuel_type = fields.Selection(
        selection_add=[("flex", "Flex")],
        string="Fuel Type",
        default="flex",
        help="Fuel Used by the vehicle",
    )

    model_year = fields.Selection(
        [
            (str(num), str(num))
            for num in range(
                (int(datetime.now().year) - 10), (int(datetime.now().year) + 1)
            )
        ],
        help="Vehicle year.",
    )
    resale_value = fields.Float(string="Current value")
    vechical_type_id = fields.Many2one("vehicle.type", string="Vehicle Type")
    tax_id = fields.Char(string="Renavam", size=11)
    fipe_id = fields.Char(string="Código Tabela FIPE", size=8)
    fipe_model = fields.Char(
        string="Modelo Tabela FIPE",
        # compute='_compute_fipe_model'
        compute="_compute_result_apifipe",
    )

    result_apifipe = fields.Char(
        string="Resultado consulta FIPE", compute="_compute_result_apifipe"
    )

    state = fields.Selection(
        [
            ("avaliable", "Avaliable"),
            ("inspection", "Inspection"),
            ("in_progress", "In Service"),
            ("contract", "On Contract"),
            ("rent", "On Rent"),
            ("complete", "Completed"),
            ("released", "Released"),
            ("write-off", "Write-Off"),
        ],
        string="Vehicle State",
        default="avaliable",
    )


class ColorHistory(models.Model):
    """Model color history."""

    _name = "color.history"
    _description = "Color History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    previous_color_id = fields.Many2one("color.color", string="Previous Color")
    current_color_id = fields.Many2one("color.color", string="New Color")
    changed_date = fields.Date(string="Change Date")
    note = fields.Text(string="Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", string="Work Order")

    def copy(self, default=None):
        """Method copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(ColorHistory, self).copy(default=default)


class EngineHistory(models.Model):
    """Model Engine History."""

    _name = "engine.history"
    _description = "Engine History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    previous_engine_no = fields.Char(string="Previous Engine No")
    new_engine_no = fields.Char(string="New Engine No")
    changed_date = fields.Date(string="Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", string="Work Order")

    def copy(self, default=None):
        """Method to copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(EngineHistory, self).copy(default=default)


class VinHistory(models.Model):
    """Model Vin History."""

    _name = "vin.history"
    _description = "Vin History"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    previous_vin_no = fields.Char(string="Previous Vin No", translate=True)
    new_vin_no = fields.Char(string="New Vin No", translate=True)
    changed_date = fields.Date(string="Change Date")
    note = fields.Text(string="Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", string="Work Order")

    def copy(self, default=None):
        """Copy Method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(VinHistory, self).copy(default=default)


class TireHistory(models.Model):
    """Model Tire History."""

    _name = "tire.history"
    _description = "Tire History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    previous_tire_size = fields.Char(
        string="Previous Tire Size", size=124, translate=True
    )
    new_tire_size = fields.Char(string="New Tire Size", size=124, translate=True)
    previous_tire_sn = fields.Char(
        string="Previous Tire Serial", size=124, translate=True
    )
    new_tire_sn = fields.Char(string="New Tire Serial", size=124)
    previous_tire_issue_date = fields.Date(string="Previous Tire Issuance Date")
    new_tire_issue_date = fields.Date(string="New Tire Issuance Date")
    changed_date = fields.Date(string="Change Date")
    note = fields.Text(string="Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", string="Work Order")

    def copy(self, default=None):
        """Method to copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(TireHistory, self).copy(default=default)


class BatteryHistory(models.Model):
    """Model Battery History."""

    _name = "battery.history"
    _description = "Battery History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    previous_battery_size = fields.Char(string="Previous Battery Size", size=124)
    new_battery_size = fields.Char(string="New Battery Size", size=124)
    previous_battery_sn = fields.Char(string="Previous Battery Serial", size=124)
    new_battery_sn = fields.Char(string="New Battery Serial", size=124)
    previous_battery_issue_date = fields.Date(string="Previous Battery Issuance Date")
    new_battery_issue_date = fields.Date(string="New Battery Issuance Date")
    changed_date = fields.Date(string="Change Date")
    note = fields.Text(string="Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", string="Work Order")

    def copy(self, default=None):
        """Method to copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(BatteryHistory, self).copy(default=default)


class PendingRepairType(models.Model):
    """Model Pending Repair Type."""

    _name = "pending.repair.type"
    _description = "Pending Repait Type"

    vehicle_rep_type_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    repair_type_id = fields.Many2one("repair.type", string="Repair Type")
    name = fields.Char(string="Work Order #", translate=True)
    categ_id = fields.Many2one("service.category", string="Category")
    issue_date = fields.Date(string="Issue Date")
    state = fields.Selection(
        [("complete", "Complete"), ("in-complete", "Pending")], string="Status"
    )
    user_id = fields.Many2one("res.users", string="By")

    def copy(self, default=None):
        """Copy Method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(PendingRepairType, self).copy(default=default)


class VehicalDivison(models.Model):
    """Model Vehicle Divison."""

    _name = "vehicle.divison"
    _description = "Vehicle Division"

    code = fields.Char(string="Code", size=3, translate=True)
    name = fields.Char(string="Name", required=True, translate=True)

    _sql_constraints = [
        ("vehicle.divison_uniq", "unique(name)", "This divison is already exist!")
    ]

    def copy(self, default=None):
        """Method to copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(VehicalDivison, self).copy(default=default)


class VehicleType(models.Model):
    """Model Vehicle Type."""

    _name = "vehicle.type"
    _description = "Vehicle Type"

    # @api.constrains('name')
    # def _check_unique_insesitive(self):
    #    vehicle_type_ids = self.search([])
    #    lst = [x.name.lower().strip()
    #           for x in vehicle_type_ids if x.name and x.id not in self._ids]
    #    for self_obj in self:
    #        if self_obj.name and self_obj.name.lower().strip() in lst:
    #            return Warning('Vehicle Type is already Exist in system.!')
    #    return True

    @api.constrains("name")
    def _check_unique_insesitive(self):
        """Method to check duplicate value."""
        for rec in self:
            count = self.env["vehicle.type"].search_count(
                [
                    ("name", "in", [rec.name.upper(), rec.name.lower()]),
                    ("id", "!=", rec.id),
                ]
            )
            if count:
                raise ValidationError("This Vehicle Type is already exist")

    code = fields.Char(string="Code", size=10, translate=True)
    name = fields.Char(string="Name", size=64, required=True, translate=True)

    def copy(self, default=None):
        """Method to copy."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(VehicleType, self).copy(default=default)


class VehicleLocation(models.Model):
    """Model Vehicle Location."""

    _name = "vehicle.location"
    _description = "Vehicle Location"

    code = fields.Char(string="Code", size=3, translate=True)
    name = fields.Char(string="Name", size=64, required=True, translate=True)

    def copy(self, default=None):
        """Copy Method can not duplicate record and override."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(VehicleLocation, self).copy(default=default)


class VehicleDepartment(models.Model):
    """Model Vehicle Department."""

    _name = "vehicle.department"
    _description = "Vehicle Department"

    code = fields.Char(string="Code", size=10, translate=True)
    name = fields.Char(string="Name", size=132, required=True, translate=True)

    def copy(self, default=None):
        """Copy method can not duplicate records and override."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(VehicleDepartment, self).copy(default=default)


class ColorColor(models.Model):
    """Model Color."""

    _name = "color.color"
    _description = "Colors"

    code = fields.Char(string="Code", size=12, translate=True)
    name = fields.Char(string="Name", size=32, required=True, translate=True)

    # _sql_constraints = [('color_uniq', 'unique(name)',
    #                      'This color is already exist!')]

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(ColorColor, self).copy(default=default)

    @api.constrains("name")
    def check_color(self):
        """Method to check duplicate value."""
        for rec in self:
            count = self.env["color.color"].search_count(
                [
                    ("name", "in", [rec.name.upper(), rec.name.lower()]),
                    ("id", "!=", rec.id),
                ]
            )
            if count:
                raise ValidationError("This color is already exist")


class IrAttachment(models.Model):
    """Model Ir Attachment."""

    _inherit = "ir.attachment"

    attachment_id = fields.Many2one("fleet.vehicle")
    attachment_id_2 = fields.Many2one("fleet.vehicle")

    def copy(self, default=None):
        """Copy method cannot duplicate record and override method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(IrAttachment, self).copy(default=default)


class FleetWittenOff(models.Model):
    """Model Fleet Witten Off."""

    _name = "fleet.wittenoff"
    _description = "Wittenoff Vehicles"
    _order = "id desc"
    _rec_name = "vehicle_id"

    name = fields.Char(string="Name")
    fleet_id = fields.Integer(
        string="Fleet ID", help="Take this field for data migration"
    )

    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    vehicle_fmp_id = fields.Char(string="Vehicle ID", size=64)
    vin_no = fields.Char(string="Vin No", size=64, translate=True)
    color_id = fields.Many2one("color.color", string="Color")
    vehicle_plate = fields.Char(string="Vechicle Plate No.", translate=True)
    report_date = fields.Date(string="Report Date")
    odometer = fields.Float(string="Odometer")
    cost_esitmation = fields.Float(string="Cost Estimation")
    note_for_cause_damage = fields.Text(string="Cuause of Damage", translate=True)
    note = fields.Text(string="Note", translate=True)
    cancel_note = fields.Text(string="Cancel Note", translate=True)
    multi_images = fields.Many2many(
        "ir.attachment",
        "fleet_written_off_attachment_rel",
        "writeoff_id",
        "attachment_id",
        string="Multi Images",
    )
    damage_type_ids = fields.Many2many(
        "damage.types",
        "fleet_wittenoff_damage_types_rel",
        "write_off_id",
        "damage_id",
        string="Damage Type",
    )
    repair_type_ids = fields.Many2many(
        "repair.type",
        "fleet_wittenoff_repair_types_rel",
        "write_off_id",
        "repair_id",
        string="Repair Type",
    )
    location_id = fields.Many2one("vehicle.location", string="Location")
    driver_id = fields.Many2one("res.partner", string="Driver")
    write_off_type = fields.Selection(
        [
            ("general_accident", "General Accident"),
            ("insurgent_attack", "Insurgent Attack"),
        ],
        string="Write-off Type",
        default="general_accident",
    )
    contact_no = fields.Char(string="Driver Contact Number")
    odometer_unit = fields.Selection(
        [("kilometers", "Kilometers"), ("miles", "Miles")],
        string="Odometer Unit",
        help="Unit of the odometer ",
    )
    province_id = fields.Many2one("res.country.state", "Registration State")
    division_id = fields.Many2one("vehicle.divison", "Division")
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirmed"), ("cancel", "Cancelled")],
        string="State",
        default="draft",
    )
    date_cancel = fields.Date(string="Date Cancelled")
    cancel_by_id = fields.Many2one("res.users", string="Cancelled By")

    def write(self, vals):
        """Override write method and update values."""
        for fleet_witten in self:
            if fleet_witten.vehicle_id:
                vals.update(
                    {
                        "vin_no": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vin_sn
                        or "",
                        "vehicle_fmp_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.name
                        or "",
                        "color_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehical_color_id
                        and fleet_witten.vehicle_id.vehical_color_id.id
                        or False,
                        "vehicle_plate": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.license_plate
                        or "",
                        "province_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehicle_location_id
                        and fleet_witten.vehicle_id.vehicle_location_id.id
                        or False,
                        "division_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehical_division_id
                        and fleet_witten.vehicle_id.vehical_division_id.id
                        or False,
                        "driver_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.driver_id
                        and fleet_witten.vehicle_id.driver_id.id
                        or False,
                        "contact_no": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.driver_id
                        and fleet_witten.vehicle_id.driver_id.mobile
                        or "",
                        "odometer": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.odometer
                        or 0.0,
                        "odometer_unit": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.odometer_unit
                        or False,
                    }
                )
        return super(FleetWittenOff, self).write(vals)

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))
        return super(FleetWittenOff, self).copy(default=default)

    @api.model
    def default_get(self, fields):
        """Default get method update in state changing record."""
        vehicle_obj = self.env["fleet.vehicle"]
        res = super(FleetWittenOff, self).default_get(fields)
        if self._context.get("active_ids", False):
            for vehicle in vehicle_obj.browse(self._context["active_ids"]):
                if vehicle.state == "write-off":
                    raise Warning(_("This vehicle is already in " "write-off state!"))
                elif vehicle.state == "in_progress" or vehicle.state == "complete":
                    raise Warning(
                        _(
                            "You can't write-off this vehicle "
                            "which is in Progress or Complete state!"
                        )
                    )
                elif vehicle.state == "inspection":
                    raise Warning(
                        _("You can't write-off this " "vehicle which is in Inspection")
                    )
                elif vehicle.state == "rent":
                    raise Warning(
                        _("You can't write-off this " "vehicle which is On Rent.")
                    )
                res.update({"contact_no": vehicle.driver_contact_no or ""})
        return res

    @api.onchange("vehicle_id")
    def get_vehicle_info(self):
        """Method to get vehicle information."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.province_id = (
                vehicle.vehicle_location_id and vehicle.vehicle_location_id.id or False
            )
            self.driver_id = vehicle.driver_id and vehicle.driver_id.id or False
            self.contact_no = vehicle.driver_contact_no or ""
            self.vin_no = vehicle.vin_sn or ""
            self.vehicle_fmp_id = vehicle.name or ""
            self.color_id = (
                vehicle.vehical_color_id and vehicle.vehical_color_id.id or False
            )
            self.vehicle_plate = vehicle.license_plate or ""
            self.odometer = vehicle.odometer or 0.0
            self.odometer_unit = vehicle.odometer_unit or False
            self.division_id = (
                vehicle.vehical_division_id and vehicle.vehical_division_id.id or False
            )

    def cancel_writeoff(self):
        """Button method in cancle state in the writeoff."""
        return {
            "name": ("Write Off Cancel Form"),
            "res_model": "writeoff.cancel.reason",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
        }

    def confirm_writeoff(self):
        """Confirm button method in the writeoff state."""
        for wr_off in self:
            if wr_off.vehicle_id:
                wr_off.vehicle_id.write(
                    {
                        "state": "write-off",
                        "last_change_status_date": date.today(),
                    }
                )
            wr_off.write(
                {
                    "state": "confirm",
                    "name": self.env["ir.sequence"].next_by_code(
                        "vehicle.writeoff.sequnce"
                    ),
                }
            )

    def action_set_to_draft(self):
        """Button method to set state in draft."""
        for wr_off in self:
            wr_off.write(
                {
                    "state": "draft",
                }
            )

    def get_usd_currency(self):
        """Method to get usd currency."""
        currency_obj = self.env["res.currency"]
        usd_ids = currency_obj.search([("name", "=", "USD")])
        if not usd_ids:
            raise Warning(_("Please, check USD Currency is not in your list!"))
        usd = usd_ids and usd_ids[0] or False
        return usd


class FleetVehicleModel(models.Model):
    """Model Fleet Vehicle."""

    _inherit = "fleet.vehicle.model"

    _rec_name = "name"

    name = fields.Char(string="Model name", size=32, required=True, translate=True)
    brand_id = fields.Many2one(
        "fleet.vehicle.model.brand",
        string="Make",
        required=True,
        help="Brand of the vehicle",
    )

    _sql_constraints = [
        (
            "model_brand_name_uniq",
            "unique(name,brand_id)",
            "Model with this brand Name and Make is " "already exist!",
        )
    ]

    image_128 = fields.Image(string="Image", readonly=False)


class FleetVehicleModelBrand(models.Model):
    """Model Fleet Vehicle Model Brand."""

    _inherit = "fleet.vehicle.model.brand"

    name = fields.Char(string="Make", size=64, required=True, translate=True)

    _sql_constraints = [
        (
            "brandname_uniq",
            "unique(name)",
            "This brand Name is already exist you " "can't duplicate it!",
        )
    ]

    @api.model
    def create(self, vals):
        """Override create method."""
        if vals.get("name", False):
            vals["name"] = vals["name"].upper()
        return super(FleetVehicleModelBrand, self).create(vals)

    def write(self, vals):
        """Override write method."""
        if vals.get("name", False):
            vals["name"] = vals["name"].upper()
        return super(FleetVehicleModelBrand, self).write(vals)


class FleetVehicleAdvanceSearch(models.TransientModel):
    """Model fleet vehicle advance search."""

    _name = "fleet.vehicle.advance.search"
    _description = "Vehicle Advance Search"
    _rec_name = "fmp_id"

    fmp_id = fields.Many2one("fleet.vehicle", string="Vehicle ID")
    vehicle_location_id = fields.Many2one("res.country.state", string="Province")
    state = fields.Selection(
        [
            ("inspection", "Inspection"),
            ("in_progress", "In Progress"),
            ("complete", "Completed"),
            ("released", "Released"),
            ("write-off", "Write-Off"),
        ],
        string="Status",
    )
    vehical_color_id = fields.Many2one("color.color", string="Color")
    vin_no = fields.Char(string="Vin No", size=64)
    engine_no = fields.Char(string="Engine No", size=64)
    last_service_date = fields.Date(string="Last Service From")
    last_service_date_to = fields.Date(string="Last Service To")
    next_service_date = fields.Date(string="Next Service From")
    next_service_date_to = fields.Date(string="Next Service To")
    acquisition_date = fields.Date(string="Registration From")
    acquisition_date_to = fields.Date(string="Registration To")
    release_date_from = fields.Date(string="Released From")
    release_date_to = fields.Date(string="Released To")
    driver_identification_no = fields.Char(string="Driver ID", size=64)
    vechical_type_id = fields.Many2one("vehicle.type", string="Vechical Type")
    division_id = fields.Many2one("vehicle.divison", string="Division")
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Make")
    model_id = fields.Many2one("fleet.vehicle.model", string="Model")

    @api.constrains("acquisition_date", "acquisition_date_to")
    def check_registration_date(self):
        """Method to check registration date."""
        for vehicle in self:
            if vehicle.acquisition_date_to:
                if vehicle.acquisition_date_to < vehicle.acquisition_date:
                    raise ValidationError(
                        "Registration To Date Should Be "
                        "Greater Than Registration From Date."
                    )

    @api.constrains("last_service_date", "last_service_date_to")
    def check_last_service_date(self):
        """Method to check last service date."""
        for vehicle in self:
            if vehicle.last_service_date_to:
                if vehicle.last_service_date_to < vehicle.last_service_date:
                    raise ValidationError(
                        "Last Service To Date Should Be "
                        "Greater Than Last Service From Date."
                    )

    @api.constrains("next_service_date", "next_service_date_to")
    def check_next_service_date(self):
        """Method to check next service date."""
        for vehicle in self:
            if vehicle.next_service_date_to:
                if vehicle.next_service_date_to < vehicle.next_service_date:
                    raise ValidationError(
                        "Next Service To Date Should Be "
                        "Greater Than Next Service From Date."
                    )

    @api.constrains("release_date_from", "release_date_to")
    def check_released_date(self):
        """Method to check released date."""
        for vehicle in self:
            if vehicle.release_date_to:
                if vehicle.release_date_to < vehicle.release_date_from:
                    raise ValidationError(
                        "Released To Date Should Be " "Greater Than Released From Date."
                    )

    def get_vehicle_detail_by_advance_search(self):
        """Method to get vehicle detail by advance search."""
        domain = []
        vehicle_obj = self.env["fleet.vehicle"]
        vehicle_ids = []
        for vehicle in self:
            if vehicle.make_id:
                vehicle_ids = vehicle_obj.search(
                    [("f_brand_id", "=", vehicle.make_id.id)]
                )
            if vehicle.model_id:
                vehicle_ids = vehicle_obj.search(
                    [("model_id", "=", vehicle.model_id.id)]
                )

            if vehicle.state:
                domain += (("state", "=", vehicle.state),)
            if vehicle.fmp_id:
                domain += (("id", "=", vehicle.fmp_id.id),)
            if vehicle.vehicle_location_id:
                domain += [("vehicle_location_id", "=", vehicle.vehicle_location_id.id)]
            if vehicle.division_id:
                domain += [("vehical_division_id", "=", vehicle.division_id.id)]
            if vehicle.vechical_type_id:
                domain += [("vechical_type_id", "=", vehicle.vechical_type_id.id)]
            if vehicle.vehical_color_id:
                domain += [("vehical_color_id", "=", vehicle.vehical_color_id.id)]
            if vehicle.vin_no:
                domain += [("vin_sn", "=", vehicle.vin_no)]
            if vehicle.engine_no:
                domain += [("engine_no", "=", vehicle.engine_no)]
            if vehicle.driver_identification_no:
                domain += [
                    ("driver_identification_no", "=", vehicle.driver_identification_no)
                ]
            if vehicle.last_service_date and vehicle.last_service_date_to:
                domain += [("last_service_date", ">=", vehicle.last_service_date)]
                domain += [("last_service_date", "<=", vehicle.last_service_date_to)]
            elif vehicle.last_service_date:
                domain += [("last_service_date", "=", vehicle.last_service_date)]
            if vehicle.next_service_date and vehicle.next_service_date_to:
                domain += [("next_service_date", ">=", vehicle.next_service_date)]
                domain += [("next_service_date", "<=", vehicle.next_service_date_to)]
            elif vehicle.next_service_date:
                domain += [("next_service_date", "=", vehicle.next_service_date)]
            if vehicle.acquisition_date and vehicle.acquisition_date_to:
                domain += [("acquisition_date", ">=", vehicle.acquisition_date)]
                domain += [("acquisition_date", "<=", vehicle.acquisition_date_to)]
            elif vehicle.acquisition_date:
                domain += [("acquisition_date", "=", vehicle.acquisition_date)]
            if vehicle.release_date_from and vehicle.release_date_to:
                domain += [("released_date", ">=", vehicle.release_date_from)]
                domain += [("released_date", "<=", vehicle.release_date_to)]
            elif vehicle.release_date_from:
                domain += [("released_date", "=", vehicle.release_date_from)]
            if vehicle.make_id or vehicle.model_id:
                vehicle_ids = sorted(set(vehicle_ids.ids))
                domain += [("id", "in", vehicle_ids)]
            return {
                "name": _("Vehicle Registration"),
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "fleet.vehicle",
                "type": "ir.actions.act_window",
                "nodestroy": True,
                "domain": domain,
                "context": self._context,
                "target": "current",
            }
        return True


class VehicleUniqueSequence(models.Model):
    """Model Vehicle Unique Sequence."""

    _name = "vehicle.unique.sequence"
    _description = "Vehicle Unique Sequence"

    name = fields.Char(string="Name", size=124, translate=True)
    vehicle_location_id = fields.Many2one("res.country.state", string="Location ")
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Make")
    sequence_id = fields.Many2one("ir.sequence", string="Sequence")

    _sql_constraints = [
        (
            "location_make_name_uniq",
            "unique (vehicle_location_id,make_id,sequence_id)",
            "Location, Make and Sequence all should be \
                uniqe for unique sequence!",
        )
    ]

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))


class NextIncrementNumber(models.Model):
    """Model Next Increment NUmber."""

    _name = "next.increment.number"
    _description = "Next Increment Number"

    name = fields.Char(string="Name", size=64, translate=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle Id")
    number = fields.Float(string="Odometer Increment")

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        """Method to check last service date."""
        next_number = self.env["next.increment.number"]
        for increment in self:
            duplicate_hist = next_number.search(
                [
                    ("vehicle_id", "=", increment.vehicle_id.id),
                    ("id", "!=", increment.id),
                ]
            )
            if duplicate_hist:
                raise ValidationError(
                    "You can not add more than one odoometer "
                    "increment configuration for same vehicle.!!!"
                )


class NextServiceDays(models.Model):
    """Model Next Service Days."""

    _name = "next.service.days"
    _description = "Next Service days"

    name = fields.Char(string="Name", translate=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle Id")
    days = fields.Integer(string="Days")

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        """Method to check last service date."""
        next_service = self.env["next.service.days"]
        for service in self:
            duplicate_hist = next_service.search(
                [("vehicle_id", "=", service.vehicle_id.id), ("id", "!=", service.id)]
            )
            if duplicate_hist:
                raise ValidationError(
                    "You can not add more than one next "
                    "service days configuration for same vehicle.!!!"
                )


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = "damage.types"
    _description = "Damage Types"

    name = fields.Char(string="Name", traslate=True)
    code = fields.Char(string="Code")

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))


class VehicleFuelLog(models.Model):
    """Model Vehicle Fuel Log."""

    _inherit = "fleet.vehicle.log.fuel"

    _order = "id desc"

    def _get_odometer(self):
        fleetvehicalodometer = self.env["fleet.vehicle.odometer"]
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search(
                [("vehicle_id", "=", record.vehicle_id.id)], limit=1, order="value desc"
            )
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        fleetvehicalodometer = self.env["fleet.vehicle.odometer"]
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search(
                [("vehicle_id", "=", record.vehicle_id.id)], limit=1, order="value desc"
            )
            if record.odometer < vehicle_odometer.value:
                raise Warning(
                    _("You can't enter odometer less than previous " "odometer %s !")
                    % (vehicle_odometer.value)
                )
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {
                    "value": record.odometer,
                    "date": date,
                    "vehicle_id": record.vehicle_id.id,
                }
                fleetvehicalodometer.create(data)

    @api.onchange("vehicle_id")
    def _onchange_vehicle(self):
        if not self.vehicle_id:
            return {}
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id

    odometer = fields.Float(
        compute="_get_odometer",
        inverse="_set_odometer",
        string="Last Odometer",
        help="Odometer measure of the vehicle at the moment of this log",
    )
    odometer_unit = fields.Selection(
        related="vehicle_id.odometer_unit", help="Unit of the odometer ", store=True
    )
    make = fields.Many2one(related="vehicle_id.f_brand_id", string="Make", store=True)
    model = fields.Many2one(related="vehicle_id.model_id", string="Model", store=True)
    current_fuel = fields.Float(string="Current Fuel", size=64)
    fuel_type = fields.Selection(
        related="vehicle_id.fuel_type", store=True, help="Fuel Used by the vehicle"
    )

    @api.model
    def default_get(self, fields):
        """Vehicle fuel log default get the records."""
        res = super(VehicleFuelLog, self).default_get(fields)
        fleet_obj = self.env["fleet.vehicle"]
        if self._context:
            ctx_keys = self._context.keys()
            if "active_model" in ctx_keys:
                if "active_id" in ctx_keys:
                    vehicle_id = self.env[self._context["active_model"]].browse(
                        self._context["active_id"]
                    )
                    if vehicle_id.state != "write-off":
                        res.update({"vehicle_id": self._context["active_id"]})
                    else:
                        res["vehicle_id"] = False
            if "vehicle_id" in ctx_keys:
                vehicle_id = fleet_obj.browse(self._context["vehicle_id"])
                if vehicle_id.state != "write-off":
                    res.update({"vehicle_id": self._context["vehicle_id"]})
        return res

    def copy(self, default=None):
        """
        Method copy for can not duplicate records.

        In the vehicle fuel log.
        """
        if not default:
            default = {}
        raise Warning(_("You can't duplicate record!"))


class FleetVehicleCost(models.Model):
    """Model Fleet Vehicle Cost."""

    _inherit = "fleet.vehicle.cost"

    @api.model
    def default_get(self, fields):
        """Default get method is set vehilce id."""
        res = super(FleetVehicleCost, self).default_get(fields)
        fleet_obj = self.env["fleet.vehicle"]
        if self._context.get("active_id", False):
            vehicle_id = fleet_obj.browse(self._context["active_id"])
            if vehicle_id.state == "write-off":
                res["vehicle_id"] = False
        return res


class FleetVehicleOdometer(models.Model):
    """Model Fleet Vehicle Odometer."""

    _inherit = "fleet.vehicle.odometer"
    _description = "Odometer log for a vehicle"
    _order = "date desc"

    def _vehicle_log_name_get_fnc(self):
        for record in self:
            name = record.vehicle_id and record.vehicle_id.name or False
            if record.date:
                if not name:
                    name = "New/" + str(record.date)
                name = name + " / " + str(record.date)
            record.name = name

    @api.onchange("vehicle_id")
    def on_change_vehicle(self):
        """Method to onchange vehicle."""
        if self.vehicle_id:
            odometer_unit = self.vehicle_id.odometer_unit
            value = self.vehicle_id.odometer
            self.unit = odometer_unit
            self.value = value

    name = fields.Char(compute="_vehicle_log_name_get_fnc", string="Name", store=True)
    date = fields.Date(string="Date", default=datetime.now().date())
    value = fields.Float(string="Odometer Value", group_operator="max")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", required=True)
    make = fields.Many2one(related="vehicle_id.f_brand_id", string="Make", store=True)
    model = fields.Many2one(related="vehicle_id.model_id", string="Model", store=True)
    unit = fields.Selection(
        related="vehicle_id.odometer_unit", string="Unit", readonly=True
    )

    @api.model
    def default_get(self, fields):
        """Method default get."""
        res = super(FleetVehicleOdometer, self).default_get(fields)
        # cr, uid, context = self.env.args
        context = self.env.context
        # context = dict(context)
        fleet_obj = self.env["fleet.vehicle"]
        if self._context.get("active_id"):
            vehicle_id = fleet_obj.browse(context["active_id"])
            if vehicle_id.state == "write-off":
                res["vehicle_id"] = False
        return res


class ReportHeading(models.Model):
    """Model Report Heading."""

    _name = "report.heading"
    _description = "Report Heading"

    @api.depends("image")
    def _get_image(self):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    def _set_image(self):
        if self.image_small:
            self.image = tools.image_resize_image_small(
                self.image_small, size=(102, 50)
            )
        elif self.image_medium:
            self.image = tools.image_resize_image_small(
                self.image_medium, size=(102, 50)
            )

    name = fields.Char(string="Title", size=128, translate=True)
    revision_no = fields.Char(string="Rev. No.", size=64, translate=True)
    document_no = fields.Char(string="Document No.", size=64, translate=True)
    image = fields.Binary(
        string="Image",
        help="This field holds the image used as image \
                            for the Report , limited to 1024x1024px.",
    )
    image_medium = fields.Binary(
        compute="_get_image",
        inverse="_set_image",
        string="Medium-sized image",
        help="Medium-sized image of the Report. \
                                 It is automatically resized as a 128x128px \
                                image, with aspect ratio preserved, "
        "only when the image exceeds one of those \
                                 sizes. Use this field in form views or \
                                 some kanban views.",
    )
    image_small = fields.Binary(
        compute="_get_image",
        inverse="_set_image",
        string="Report image",
        help="Small-sized image of the Report. \
                                It is automatically "
        "resized as a 64x64px image, \
                                with aspect ratio preserved. "
        "Use this field anywhere a small \
                                image is required.",
    )


class ResCompany(models.Model):
    """Model Res Company."""

    _inherit = "res.company"

    name = fields.Char(
        related="partner_id.name",
        string="Company Name",
        size=128,
        required=True,
        store=True,
        translate=True,
    )


class InsuranceType(models.Model):
    """Model Insurance Type."""

    _name = "insurance.type"
    _description = "Vehicle Insurence Type"

    name = fields.Char(string="Name")
