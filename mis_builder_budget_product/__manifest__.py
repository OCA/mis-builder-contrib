# Copyright 2022 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder Budget Contributions",
    "summary": """
            Offer more options for budgets for MIS reports""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder-contrib",
    "depends": ["mis_builder_budget"],
    "data": [
        "views/mis_budget_by_account_item.xml",
    ],
    "installable": True,
}
