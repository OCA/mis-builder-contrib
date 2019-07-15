# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'MIS Builder with Account Move Budget',
    'version': '11.0.1.0.0',
    'category': 'Reporting',
    "author": "Eficent, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    'website': 'https://github.com/OCA/mis-builder-contrib',
    'depends': ['mis_builder', 'account_move_budget'],
    'data': [
        'view/mis_builder.xml',
    ],
    'installable': True,
}
