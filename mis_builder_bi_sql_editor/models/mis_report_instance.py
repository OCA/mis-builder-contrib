# Copyright 2025 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisReportInstancePeriod(models.Model):
    _inherit = "mis.report.instance.period"

    bi_sql_view = fields.Many2one(
        string="BI SQL View",
        comodel_name="bi.sql.view",
        domain=[("mis_builder_activated", "=", True)],
    )
    bi_sql_view_required = fields.Boolean(
        default=False, compute="_compute_bi_sql_view_required"
    )

    @api.depends("source", "source_aml_model_id")
    def _compute_bi_sql_view_required(self):
        for record in self:
            if record.source == "actuals_alt":
                model_id = (
                    self.env["ir.model"]
                    .search([("model", "=", "mis.builder.bi.sql.line")])
                    .id
                )
                record.bi_sql_view_required = record.source_aml_model_id.id == model_id
            else:
                record.bi_sql_view_required = False

    def _get_additional_move_line_filter(self):
        domain = super()._get_additional_move_line_filter()
        if self.bi_sql_view:
            domain = domain + [("bi_sql_model", "=", self.bi_sql_view.model_id.id)]
        return domain


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    bi_sql_view = fields.Many2one(
        string="BI SQL View",
        comodel_name="bi.sql.view",
        related="report_id.bi_sql_view",
    )
