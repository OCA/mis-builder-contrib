# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MisBuilderCustomExportXlsWizardLine(models.TransientModel):
    _name = "mis.builder.custom.export.xls.wizard.line"
    _description = "Mis Builder Custom Export Xls Wizard Line"

    report_id = fields.Many2one(
        comodel_name="mis.report.instance",
        string="Report",
        readonly=False,
    )

    date = fields.Date(
        compute="_compute_date",
        store=True,
        readonly=False,
    )

    wizard_id = fields.Many2one(
        comodel_name="mis.builder.custom.export.xls.wizard",
    )

    @api.depends("report_id")
    def _compute_date(self):
        for rec in self:
            rec.date = rec.report_id.pivot_date
