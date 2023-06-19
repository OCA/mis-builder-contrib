# Copyright 2023 - TODAY Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMisBudgetByAccountItem(TransactionCase):
    def setUp(self):
        super(TestMisBudgetByAccountItem, self).setUp()

        self.company = self.env.ref("base.main_company")
        self.date_type = self.env["date.range.type"].create(
            {"name": "Test", "company_id": self.company.id, "allow_overlap": False}
        )
        self.date_range = self.env["date.range"].create(
            {
                "name": "FS2015",
                "date_start": "2023-06-01",
                "date_end": "2023-06-30",
                "type_id": self.date_type.id,
            }
        )
        self.product = self.env.ref("product.product_product_3")
        self.account = self.env["account.account"].create(
            {
                "name": "Account Mis Budget Account Item",
                "code": "TESTBUDGET",
                "user_type_id": self.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        self.budget_account = self.env["mis.budget.by.account"].create(
            {
                "name": "Test",
                "date_range_id": self.date_range.id,
                "date_from": "2023-06-01",
                "date_to": "2023-06-30",
                "state": "confirmed",
                "company_id": self.company.id,
            }
        )
        self.item_id = self.env["mis.budget.by.account.item"].create(
            {
                "name": "Product A",
                "account_id": self.account.id,
                "budget_id": self.budget_account.id,
                "date_range_id": self.date_range.id,
                "date_from": "2023-06-01",
                "date_to": "2023-06-30",
                "debit": 0.00,
                "credit": 500.00,
                "balance": -500.00,
                "product_id": self.product.id,
            }
        )
        self.budget_account_item = self.budget_account.item_ids

    def test_prepare_overlap_domain_with_product(self):

        domain = self.budget_account_item._prepare_overlap_domain()

        expected_domain = [
            "&",
            "&",
            "&",
            "&",
            "&",
            "&",
            ("id", "!=", self.budget_account_item.id),
            ("budget_id", "=", self.budget_account.id),
            ("date_from", "<=", date(2023, 6, 30)),
            ("date_to", ">=", date(2023, 6, 1)),
            ("analytic_account_id", "=", False),
            ("account_id", "=", self.account.id),
            "|",
            ("product_id", "=", False),
            ("product_id", "=", self.product.id),
        ]

        self.assertEqual(expected_domain, domain)

    def test_check_product(self):
        check = self.budget_account_item._check_dates()
        self.assertIsNone(check)
