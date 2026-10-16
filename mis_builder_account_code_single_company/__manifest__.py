# Copyright 2026 Acsone
# Author: Pierre Verkest <pierre.verkest@apycod.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder Account Code Single Company",
    "summary": (
        "Optimize MIS Builder account searches across companies for"
        " single-company accounts"
    ),
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "website": "https://github.com/OCA/mis-builder-contrib",
    "depends": ["account_code_single_company", "mis_builder"],
    "data": [],
    "post_load": "post_load",
}
