# Copyright 2026 Acsone
# Author: Pierre Verkest <pierre.verkest@apycod.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common, tagged

from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor


@tagged("-at_install", "post_install")
class TestMISBuilderAccountSingleCompany(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create(
            {"name": "Company B", "currency_id": cls.company_a.currency_id.id}
        )
        cls.company_c = cls.env["res.company"].create(
            {"name": "Company C", "currency_id": cls.company_a.currency_id.id}
        )
        cls.companies = cls.company_a | cls.company_b | cls.company_c

        cls.single_company_account_a = cls.env["account.account"].create(
            {
                "name": "Single Company Account A",
                "code": "123456",
                "account_type": "asset_current",
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )
        cls.single_company_account_b = cls.env["account.account"].create(
            {
                "name": "Single Company Account B",
                "code": "123457",
                "account_type": "asset_current",
                "company_ids": [(6, 0, [cls.company_b.id])],
            }
        )
        cls.single_company_account_c = cls.env["account.account"].create(
            {
                "name": "Single Company Account C",
                "code": "123458",
                "account_type": "asset_current",
                "company_ids": [(6, 0, [cls.company_c.id])],
            }
        )

        cls.single_company_income_a = cls.env["account.account"].create(
            {
                "name": "Income Account A",
                "code": "700111",
                "account_type": "income",
                "company_ids": [(6, 0, [cls.company_a.id])],
            }
        )
        cls.single_company_income_b = cls.env["account.account"].create(
            {
                "name": "Income Account B",
                "code": "700222",
                "account_type": "income",
                "company_ids": [(6, 0, [cls.company_b.id])],
            }
        )

        cls.multi_company_account = cls.env["account.account"].create(
            {
                "name": "Multi Company Account",
                "account_type": "asset_current",
                "company_ids": [(6, 0, [cls.company_a.id, cls.company_b.id])],
                "code_mapping_ids": [
                    (0, 0, {"company_id": cls.company_a.id, "code": "654321"}),
                    (0, 0, {"company_id": cls.company_b.id, "code": "654322"}),
                ],
            }
        )

    def setUp(self):
        super().setUp()
        self.env["account.account"].search([("company_ids", "in", self.companies.ids)])

    def test_done_parsing_executes_single_query_per_unique_domain_across_companies(
        self,
    ):
        aep = AccountingExpressionProcessor(self.companies)
        aep.parse_expr("balp[123%]")
        aep.parse_expr("bali[123%]")
        aep.parse_expr("bale[123%]")
        aep.parse_expr("bale[700%]")
        aep.parse_expr("balp[700%]")
        with self.assertQueryCount(2):
            aep.done_parsing()

    def test_done_parsing_finds_single_company_accounts_from_all_targeted_companies(
        self,
    ):
        aep = AccountingExpressionProcessor(self.companies)
        aep.parse_expr("balp[123%]")
        aep.parse_expr("balp[700%]")
        aep.done_parsing()
        expected_123_ids = {
            self.single_company_account_a.id,
            self.single_company_account_b.id,
            self.single_company_account_c.id,
        }
        expected_700_ids = {
            self.single_company_income_a.id,
            self.single_company_income_b.id,
        }
        account_ids_by_domain = {
            domain[0][2]: ids for domain, ids in aep._account_ids_by_acc_domain.items()
        }
        self.assertEqual(account_ids_by_domain["123%"], expected_123_ids)
        self.assertEqual(account_ids_by_domain["700%"], expected_700_ids)

    def test_done_parsing_with_skip_flag_queries_each_company_individually(self):
        companies = self.companies.with_context(
            skip_search_accounts_for_all_company_at_once=True
        )
        aep = AccountingExpressionProcessor(companies)
        aep.parse_expr("balp[123%]")
        aep.parse_expr("bali[123%]")
        aep.parse_expr("bale[123%]")
        aep.parse_expr("bale[700%]")
        aep.parse_expr("balp[700%]")
        with self.assertQueryCount(9):
            aep.done_parsing()

    def test_done_parsing_result_matches_between_single_search_and_individual_search(
        self,
    ):
        aep_fast = AccountingExpressionProcessor(self.companies)
        aep_fast.parse_expr("balp[123%]")
        aep_fast.parse_expr("balp[700%]")
        aep_fast.done_parsing()

        companies_fallback = self.companies.with_context(
            skip_search_accounts_for_all_company_at_once=True
        )
        aep_fallback = AccountingExpressionProcessor(companies_fallback)
        aep_fallback.parse_expr("balp[123%]")
        aep_fallback.parse_expr("balp[700%]")
        aep_fallback.done_parsing()

        self.assertEqual(
            aep_fast._account_ids_by_acc_domain,
            aep_fallback._account_ids_by_acc_domain,
        )
