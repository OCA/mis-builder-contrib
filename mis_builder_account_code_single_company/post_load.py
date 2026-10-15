# Copyright 2026 Acsone
# Author: Pierre Verkest <pierre.verkest@apycod.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.fields import Domain

from odoo.addons.mis_builder.models.aep import AccountingExpressionProcessor

_logger = logging.getLogger(__name__)


def post_load():
    """Patch AccountingExpressionProcessor._done_parsing_search_accounts
    to search accounts for all companies at once when single-company account
    codes are in use.
    """
    _logger.info(
        "Apply AccountingExpressionProcessor._done_parsing_search_accounts monkey patch"
    )

    original_done_parsing_search_accounts = (
        AccountingExpressionProcessor._done_parsing_search_accounts
    )

    def _done_parsing_search_accounts(self, all_unique_domains):
        if self.env.context.get("skip_search_accounts_for_all_company_at_once", False):
            return original_done_parsing_search_accounts(self, all_unique_domains)

        company_domain = [("company_ids", "in", self.companies.ids)]
        for acc_domain in all_unique_domains:
            self._account_ids_by_acc_domain[acc_domain].update(
                self._account_model.search(
                    Domain.AND([acc_domain, company_domain]), order="id"
                ).ids
            )

    AccountingExpressionProcessor._done_parsing_search_accounts = (
        _done_parsing_search_accounts
    )
