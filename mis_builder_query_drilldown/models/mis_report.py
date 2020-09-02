# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.mis_builder.models.expression_evaluator import ExpressionEvaluator


class MisReportKpi(models.Model):
    _inherit = "mis.report.kpi"

    query_id = fields.Many2one("mis.report.query", string="Linked Query")


class MisQueryExpressionEvaluator(ExpressionEvaluator):
    def eval_expressions(self, expressions, locals_dict):
        vals, drilldown_args, name_error = super(
            MisQueryExpressionEvaluator, self
        ).eval_expressions(expressions, locals_dict)
        for expression in expressions:
            if expression.kpi_id.query_id:
                domain = (
                    expression.kpi_id.query_id.domain
                    and safe_eval(expression.kpi_id.query_id.domain)
                    or []
                )
                if locals_dict.get(expression.kpi_id.query_id, False):
                    domain = locals_dict[expression.kpi_id.query_id]["domain"]
                drilldown_args = [
                    {
                        "domain": domain,
                        "model": expression.kpi_id.query_id.model_id.model,
                        "date_field": expression.kpi_id.query_id.date_field.name,
                    }
                ]
        return vals, drilldown_args, name_error


class MisReportInstance(models.Model):
    _inherit = "mis.report.instance"

    def _add_column_move_lines(self, aep, kpi_matrix, period, label, description):
        super(MisReportInstance, self)._add_column_move_lines(
            aep, kpi_matrix, period, label, description
        )
        expression_evaluator = MisQueryExpressionEvaluator(
            aep,
            period.date_from,
            period.date_to,
            None,  # target_move now part of additional_move_line_filter
            period._get_additional_move_line_filter(),
            period._get_aml_model_name(),
        )
        self.report_id._declare_and_compute_period(
            expression_evaluator,
            kpi_matrix,
            period.id,
            label,
            description,
            period.subkpi_ids,
            period._get_additional_query_filter,
            no_auto_expand_accounts=self.no_auto_expand_accounts,
        )

    def drilldown(self, arg):
        self.ensure_one()
        period_id = arg.get("period_id")
        domain = arg.get("domain", False)
        model = arg.get("model", False)
        date_field = arg.get("date_field", False)
        if period_id and date_field and model and isinstance(domain, list):
            period = self.env["mis.report.instance.period"].browse(period_id)
            domain.extend(
                (
                    (date_field, "<=", period.date_to),
                    (date_field, ">=", period.date_from),
                )
            )
            return {
                "name": u"{} - {}".format(model, period.name),
                "domain": domain,
                "type": "ir.actions.act_window",
                "res_model": model,
                "views": [[False, "list"], [False, "form"]],
                "view_type": "list",
                "view_mode": "list",
                "target": "current",
            }
        return super(MisReportInstance, self).drilldown(arg)
