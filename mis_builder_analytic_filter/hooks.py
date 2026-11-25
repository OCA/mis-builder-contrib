# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Use the new search view on the existing MIS report instances."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    view = env.ref("mis_builder_analytic_filter.mis_account_analytic_line_search")
    instances = (
        env["mis.report.instance"]
        .with_context(active_test=False)
        .search(
            [
                ("report_id.move_lines_source.model", "=", view.model),
                ("widget_search_view_id", "=", False),
            ]
        )
    )
    instances.write({"widget_search_view_id": view.id})
