# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Mis Builder Wizard Export Xlsx",
    "summary": """
        Wizard to select various options when exporting a mis report as xlsx""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder-contrib",
    "depends": [
        "mis_builder",
    ],
    "data": [
        "security/mis_builder_custom_export_xls_wizard.xml",
        "security/mis_builder_custom_export_xls_wizard_line.xml",
        "wizards/mis_builder_custom_export_xls_wizard.xml",
    ],
    "demo": [],
}
