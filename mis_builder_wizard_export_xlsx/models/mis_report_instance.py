# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def open_wizard_custom_export_xls(self):
        return self.env["ir.actions.act_window"]._for_xml_id(
            "mis_builder_wizard_export_xlsx.mis_builder_custom_export_xls_wizard_act_window"
        )

    def _compute_pivot_date(self):
        ret = super()._compute_pivot_date()
        report_id_by_pivot_date = self.env.context.get(
            "mis_builder_xls_report_id_by_pivot_date"
        )
        if report_id_by_pivot_date:
            for rec in self:
                pivot_date = report_id_by_pivot_date.get(str(rec.id))
                if pivot_date:
                    rec.pivot_date = pivot_date

        return ret
