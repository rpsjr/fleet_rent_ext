# See LICENSE file for full copyright and licensing details.

import base64
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

# 1x1 transparent GIF
BLANK_GIF = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")


class FleetRentTrackingController(http.Controller):

    @http.route(
        [
            "/fleet_rent/track_proposal/<int:rent_id>/open.gif",
            "/fleet_rent/track_proposal/<int:rent_id>/<string:token>/open.gif",
        ],
        type="http",
        auth="none",
        cors="*",
        csrf=False,
    )
    def track_proposal_open(self, rent_id, token="", **kwargs):
        try:
            rent = request.env["fleet.rent"].sudo().browse(rent_id)
            if rent.exists():
                rent._action_on_proposal_email_opened()
        except Exception as exc:
            _logger.warning("Error tracking proposal open for rent %s: %s", rent_id, exc)

        headers = [
            ("Content-Type", "image/gif"),
            ("Content-Length", str(len(BLANK_GIF))),
            ("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0"),
            ("Pragma", "no-cache"),
            ("Expires", "0"),
        ]
        return Response(BLANK_GIF, headers=headers)

    @http.route(
        [
            "/mail/track/<int:mail_id>/blank.gif",
            "/mail/track/<int:mail_id>/<string:token>/blank.gif",
        ],
        type="http",
        auth="none",
        cors="*",
        csrf=False,
    )
    def track_mail_open(self, mail_id, token="", **kwargs):
        try:
            mail = request.env["mail.mail"].sudo().browse(mail_id)
            if mail.exists() and mail.model == "fleet.rent" and mail.res_id:
                rent = request.env["fleet.rent"].sudo().browse(mail.res_id)
                if rent.exists():
                    rent._action_on_proposal_email_opened()
        except Exception as exc:
            _logger.warning("Error tracking mail open for mail %s: %s", mail_id, exc)

        headers = [
            ("Content-Type", "image/gif"),
            ("Content-Length", str(len(BLANK_GIF))),
            ("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0"),
            ("Pragma", "no-cache"),
            ("Expires", "0"),
        ]
        return Response(BLANK_GIF, headers=headers)
