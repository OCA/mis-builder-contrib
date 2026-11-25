# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MisAccountAnalyticLine(models.Model):
    _inherit = "mis.account.analytic.line"

    plan_id = fields.Many2one(
        related="analytic_account_id.plan_id",
        string="Analytic Plan",
    )
    tag_ids = fields.Many2many(
        related="analytic_line_id.tag_ids",
        string="Analytic Tags",
    )
