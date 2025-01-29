# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class MisBuilderCustomExportXlsWizard(models.TransientModel):
    _name = "mis.builder.custom.export.xls.wizard"
    _description = "Mis Builder Custom Export Xls Wizard"

    company_ids = fields.Many2many(
        comodel_name="res.company",
        string="Company",
        domain="[('id', 'in', allowed_company_ids)]",
        default=lambda self: self.env.company,
    )

    wizard_line_ids = fields.One2many(
        comodel_name="mis.builder.custom.export.xls.wizard.line",
        inverse_name="wizard_id",
    )

    compute_report_company_by_company = fields.Boolean(
        help="Compute report company by company (one sheet by company and report) instead of"
        " computing computing report one every company at once (one sheet by report)."
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        report_ids = self.env.context.get("active_ids")
        if self.env.context.get("active_model") == "mis.report.instance" and (
            report_ids
        ):
            res["wizard_line_ids"] = [
                Command.create(
                    {
                        "report_id": report_id,
                    }
                )
                for report_id in report_ids
            ]

        return res

    def export(self):
        custom_context = {
            "mis_builder_xls_custom_company_ids": self.company_ids.ids,
            "mis_builder_xls_report_id_by_pivot_date": {
                rec.report_id.id: rec.date for rec in self.wizard_line_ids
            },
            "mis_builder_xls_company_by_company": self.compute_report_company_by_company,
        }

        # map date by instance
        return self.wizard_line_ids.report_id.with_context(
            **custom_context
        ).export_xls()
