# Copyright 2026 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestMisTotalCommittedPurchase(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Committed = cls.env["mis.total.committed.purchase"]
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor"})
        cls.expense = cls.company_data["default_account_expense"]
        cls.product = cls.env["product.product"].create(
            {
                "name": "Item",
                "type": "consu",
                "property_account_expense_id": cls.expense.id,
            }
        )
        plan = cls.env["account.analytic.plan"].create({"name": "Plan"})
        other_plan = cls.env["account.analytic.plan"].create({"name": "Other"})
        cls.analytic_1 = cls.env["account.analytic.account"].create(
            {"name": "A1", "plan_id": plan.id}
        )
        cls.analytic_2 = cls.env["account.analytic.account"].create(
            {"name": "A2", "plan_id": plan.id}
        )
        cls.analytic_3 = cls.env["account.analytic.account"].create(
            {"name": "A3", "plan_id": other_plan.id}
        )

    def _order(self, distribution=None, confirm=True):
        line = {"product_id": self.product.id, "product_qty": 4, "price_unit": 25.0}
        if distribution:
            line["analytic_distribution"] = distribution
        order = self.env["purchase.order"].create(
            {"partner_id": self.vendor.id, "order_line": [Command.create(line)]}
        )
        if confirm:
            order.button_confirm()
        self.env.flush_all()
        return order

    def _rows(self, order):
        return self.Committed.search([("purchase_order_id", "=", order.id)])

    def test_01_confirmed_without_analytic(self):
        rows = self._rows(self._order())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.debit, 100.0)
        self.assertEqual(rows.account_id, self.expense)
        self.assertFalse(rows.analytic_account_id)

    def test_02_draft_not_committed(self):
        self.assertFalse(self._rows(self._order(confirm=False)))

    def test_03_analytic_split(self):
        order = self._order(
            {str(self.analytic_1.id): 60.0, str(self.analytic_2.id): 40.0}
        )
        rows = self._rows(order)
        self.assertEqual(len(rows), 2)
        by_account = {r.analytic_account_id: r.debit for r in rows}
        self.assertEqual(by_account[self.analytic_1], 60.0)
        self.assertEqual(by_account[self.analytic_2], 40.0)

    def test_04_combined_analytic_key(self):
        key = f"{self.analytic_1.id},{self.analytic_3.id}"
        order = self._order({key: 100.0})
        rows = self._rows(order)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.debit, 100.0)
        self.assertEqual(rows.analytic_account_id, self.analytic_1)
        self.env.cr.execute(
            "SELECT analytic_account_id"
            " FROM mis_total_committed_purchase_analytic_account_rel"
            " WHERE mis_total_committed_purchase_id = %s",
            (rows.id,),
        )
        self.assertEqual(
            {r[0] for r in self.env.cr.fetchall()},
            {self.analytic_1.id, self.analytic_3.id},
        )
