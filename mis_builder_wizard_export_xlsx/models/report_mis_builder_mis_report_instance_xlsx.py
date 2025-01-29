# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MisBuilderXlsx(models.AbstractModel):

    _inherit = "report.mis_builder.mis_report_instance_xlsx"

    def generate_xlsx_report(self, workbook, data, objects):
        company_ids = self.env.context.get("mis_builder_xls_custom_company_ids")
        if company_ids:
            if self.env.context.get("mis_builder_xls_company_by_company"):
                for company_id in company_ids:
                    res = super().generate_xlsx_report(
                        workbook,
                        data,
                        objects.with_context(**{"allowed_company_ids": [company_id]}),
                    )
            else:
                res = super().generate_xlsx_report(
                    workbook,
                    data,
                    objects.with_context(**{"allowed_company_ids": company_ids}),
                )
        else:
            res = super().generate_xlsx_report(workbook, data, objects)

        return res
