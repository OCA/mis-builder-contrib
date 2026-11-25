# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder Analytic Filter",
    "summary": """
        Filter box by analytic account, plan and tag on MIS reports
        based on analytic lines""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder-contrib",
    "depends": ["mis_builder_analytic", "account_analytic_tag"],
    "data": [
        "views/mis_account_analytic_line_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
