# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMisAccountAnalyticLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Plan"})
        cls.child_plan = cls.env["account.analytic.plan"].create(
            {"name": "Child Plan", "parent_id": cls.plan.id}
        )
        cls.analytic_a = cls.env["account.analytic.account"].create(
            {"name": "Analytic A", "plan_id": cls.child_plan.id}
        )
        cls.analytic_b = cls.env["account.analytic.account"].create(
            {"name": "Analytic B", "plan_id": cls.plan.id}
        )
        cls.tag = cls.env["account.analytic.tag"].create({"name": "Tag"})
        cls.line_a = cls.env["account.analytic.line"].create(
            {
                "name": "Line A",
                "account_id": cls.analytic_a.id,
                "amount": 100.0,
                "tag_ids": [(6, 0, cls.tag.ids)],
            }
        )
        cls.line_b = cls.env["account.analytic.line"].create(
            {"name": "Line B", "account_id": cls.analytic_b.id, "amount": -50.0}
        )
        cls.MisLine = cls.env["mis.account.analytic.line"]

    def _search(self, domain):
        return self.MisLine.search(
            domain + [("analytic_line_id", "in", (self.line_a + self.line_b).ids)]
        ).mapped("analytic_line_id")

    def test_filter_by_tag(self):
        self.assertEqual(self._search([("tag_ids", "in", self.tag.ids)]), self.line_a)

    def test_filter_by_plan_includes_children(self):
        self.assertEqual(
            self._search([("analytic_account_id.plan_id", "child_of", self.plan.id)]),
            self.line_a + self.line_b,
        )
        self.assertEqual(
            self._search([("plan_id", "=", self.child_plan.id)]), self.line_a
        )

    def test_report_instance_uses_search_view(self):
        view = self.env.ref(
            "mis_builder_analytic_filter.mis_account_analytic_line_search"
        )
        source = self.env["ir.model"]._get("mis.account.analytic.line")
        report = self.env["mis.report"].create(
            {"name": "SIG", "move_lines_source": source.id}
        )
        instance = self.env["mis.report.instance"].create(
            {"name": "SIG", "report_id": report.id}
        )
        self.assertEqual(instance.widget_search_view_id, view)
