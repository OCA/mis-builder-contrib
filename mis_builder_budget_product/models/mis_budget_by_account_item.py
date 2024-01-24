# Copyright 2022 Camptocamp SA (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class MisBudgetByAccountItem(models.Model):

    _inherit = "mis.budget.by.account.item"
    _order = "budget_id, date_from, account_id, product_id"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    def _prepare_overlap_domain(self):
        # Two budget items are not overlapping if they have different products. However,
        # if they are similar for every other point, and they have the same product, or
        # at least one of the lines has no defined product (which means that it includes
        # the product of the other line), they are overlapping.
        domain = super()._prepare_overlap_domain()
        if self.product_id:
            # If the current line has a product, we have overlapping for another line with
            # the same product or an empty one
            domain = expression.AND(
                [
                    domain,
                    [
                        "|",
                        ("product_id", "=", False),
                        ("product_id", "=", self.product_id.id),
                    ],
                ]
            )
        # If the current line has no product, it includes all of them, so a similar line
        # implies overlapping, no matter the value of product_id
        return domain

    @api.constrains(
        "product_id",
    )
    def _check_product(self):
        """Check dates if product changes."""
        self._check_dates()
        return
