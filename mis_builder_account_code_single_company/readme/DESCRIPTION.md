This module is a bridge between **mis_builder** and **account_code_single_company**.

In standard Odoo 19, account codes (`code_store`) are company-dependent. For this reason, `mis_builder`'s `AccountingExpressionProcessor` (`AEP._done_parsing_search_accounts`) searches matching accounts by iterating over every company individually (`with_company(company)`). In multi-company environments, this generates `N_companies * N_unique_domains` search queries.

With `account_code_single_company` installed, accounts linked to a single company store their code in `code_store_single_company`. Searching accounts by code operates across companies without being restricted to the active context company.

This module patches `AccountingExpressionProcessor._done_parsing_search_accounts` to execute a single search query per unique account domain across all targeted companies (`company_ids in self.companies.ids`). This eliminates the loop over companies and reduces the query count to `N_unique_domains`, significantly speeding up MIS report parsing in multi-company setups.

### Fallback

If you need the original per-company search behavior (for example, when evaluating shared multi-company accounts whose codes differ across companies), you can set the context key `skip_search_accounts_for_all_company_at_once=True` on the environment or company recordset.

