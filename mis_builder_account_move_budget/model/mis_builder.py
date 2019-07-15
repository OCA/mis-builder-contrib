# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.mis_builder.models.mis_report_instance \
    import SRC_ACTUALS_ALT


class MisReportInstancePeriod(models.Model):

    _inherit = 'mis.report.instance.period'

    account_move_budget_id = fields.Many2one('account.move.budget',
                                             string='Account Move Budget',
                                             required=False, copy=False)

    @api.multi
    def _get_additional_move_line_filter(self):
        aml_domain = super(MisReportInstancePeriod, self).\
            _get_additional_move_line_filter()
        if self.account_move_budget_id and \
                self.source == SRC_ACTUALS_ALT:
            aml_domain.append(
                ('budget_id', '=', self.account_move_budget_id.id))
        return aml_domain
