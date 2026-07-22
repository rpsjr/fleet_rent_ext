from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fleet_rent_count = fields.Integer(
        compute="_compute_fleet_rent_count", string="Fleet Rents"
    )

    def _compute_fleet_rent_count(self):
        for partner in self:
            partner.fleet_rent_count = self.env["fleet.rent"].search_count(
                [("tenant_id", "=", partner.id)]
            )

    def action_view_fleet_rents(self):
        self.ensure_one()
        return {
            "name": "Aluguéis",
            "type": "ir.actions.act_window",
            "res_model": "fleet.rent",
            "view_mode": "tree,form",
            "domain": [("tenant_id", "=", self.id)],
            "context": {"default_tenant_id": self.id},
        }
