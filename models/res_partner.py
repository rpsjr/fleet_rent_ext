import re

from odoo import api, fields, models
from odoo.osv import expression


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

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = list(args or [])
        if name:
            clean_name = name.strip()
            digits = re.sub(r"\D", "", clean_name)
            search_domains = [
                [("name", operator, clean_name)],
                [("display_name", operator, clean_name)],
                [("email", operator, clean_name)],
                [("ref", "=", clean_name)],
                [("phone", operator, clean_name)],
                [("mobile", operator, clean_name)],
                [("vat", operator, clean_name)],
            ]
            if "l10n_br_cnpj_cpf" in self._fields:
                search_domains.append([("l10n_br_cnpj_cpf", operator, clean_name)])

            # If search query contains digits (e.g. searching CPF/phone unformatted or formatted)
            if digits and len(digits) >= 2:
                search_domains.append([("phone", "ilike", digits)])
                search_domains.append([("mobile", "ilike", digits)])
                search_domains.append([("vat", "ilike", digits)])
                if "l10n_br_cnpj_cpf" in self._fields:
                    search_domains.append([("l10n_br_cnpj_cpf", "ilike", digits)])

            partner_domain = expression.OR(search_domains)
            domain = expression.AND([partner_domain, args])
            partner_ids = self._search(
                domain, limit=limit, access_rights_uid=name_get_uid
            )
            records = self.browse(partner_ids).with_user(name_get_uid)
            if hasattr(models, "lazy_name_get"):
                return models.lazy_name_get(records)
            return records.name_get()

        return super()._name_search(
            name,
            args=args,
            operator=operator,
            limit=limit,
            name_get_uid=name_get_uid,
        )
