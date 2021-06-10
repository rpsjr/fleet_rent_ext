# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Fleet Rental Vehicle l10n_br',
    'category': 'Fleet Rent',
    'sequence': 1,
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """Rental Vehicle Management System
        This module provides fleet rent features.""",
    'description': """
        Rental Vehicle Management System
        This module extend fleet rent features..
     """,
    # Website
    'author': 'RPSJR',
    'website': 'http://www..com',

    # Dependencies
    'depends': ['analytic', 'fleet_rent', 'contract','uom','contract_variable_quantity', 'partner_contact_marital_status' ],

    # Data
    'data': [
            'security/ir.model.access.csv',
            'views/extended_views.xml',
            'views/fleet_extended_view.xml',
            'report/rent_proposal_pdf.xml'
    ],
    # Technical
    'auto_install': False,
    'installable': True,
    'application': True,
    "external_dependencies": {"python": ["num2words"]},
}
