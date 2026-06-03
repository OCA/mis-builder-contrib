# Copyright 2025 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestMisBuilderBiSqlLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")

    def test_create_line(self):
        line = self.env["mis.builder.bi.sql.line"].create(
            {
                "credit": 100.0,
                "debit": 0.0,
                "company_id": self.company.id,
            }
        )
        self.assertEqual(line.credit, 100.0)
        self.assertEqual(line.company_id, self.company)

    def test_report_filter_without_bi_sql_view(self):
        period = self.env["mis.report.instance.period"]
        self.assertTrue(
            hasattr(period, "_get_additional_move_line_filter"),
            "mis.report.instance.period must expose _get_additional_move_line_filter",
        )
