from odoo import api, fields, models


# flake8: noqa: E501
class MisContractLine(models.Model):
    _name = "mis.contract.line"
    _auto = False
    _description = "MIS Contract Line"

    account_id = fields.Many2one("account.account", string="Account")
    company_id = fields.Many2one("res.company", string="Company")
    contract_line_id = fields.Many2one("contract.line", string="Contract Line")
    credit = fields.Float()
    date = fields.Date()
    debit = fields.Float()
    quantity = fields.Integer()
    repetitions = fields.Integer()
    specific_price = fields.Float()
    product_id = fields.Many2one("product.product", string="Product")

    @property
    def _table_query(self):
        return "".join(
            [
                self._select(),
                self._from(),
                self._left_join(),
                self._subquery_repetitions(),
                self._join_generate_series_and_where(),
            ]
        )

    @api.model
    def _select(self):
        return """
    SELECT
        (cl.id * 1000 + gs.n) AS id,
        cl.id AS contract_line_id,
        cl.date_start + CASE cl.recurring_rule_type
            WHEN 'daily' THEN (gs.n || ' days')::interval
            WHEN 'weekly' THEN (gs.n * cl.recurring_interval || ' weeks')::interval
            WHEN 'monthly' THEN (gs.n * cl.recurring_interval || ' months')::interval
            WHEN 'monthlylastday' THEN (gs.n * cl.recurring_interval || ' months')::interval
            WHEN 'quarterly' THEN (gs.n * 3 * cl.recurring_interval || ' months')::interval
            WHEN 'semesterly' THEN (gs.n * 6 * cl.recurring_interval || ' months')::interval
            WHEN 'yearly' THEN (gs.n * cl.recurring_interval || ' years')::interval
            ELSE '0 days'::interval
        END AS date,
        cl.quantity AS quantity,
        cl.specific_price AS specific_price,
        cl.company_id AS company_id,
        COALESCE(rep.repetitions, 24) AS repetitions,
        CASE
            WHEN c.contract_type = 'purchase' THEN COALESCE(
                NULLIF(SPLIT_PART(ipex.value_reference, ',', 2), '')::int,
                NULLIF(SPLIT_PART(ipex_cat.value_reference, ',', 2), '')::int,
                NULLIF(SPLIT_PART(ipd.value_reference, ',', 2), '')::int
            )
            WHEN c.contract_type = 'sale' THEN COALESCE(
                NULLIF(SPLIT_PART(ipin.value_reference, ',', 2), '')::int,
                NULLIF(SPLIT_PART(ipin_cat.value_reference, ',', 2), '')::int,
                NULLIF(SPLIT_PART(ipd_income.value_reference, ',', 2), '')::int
            )
            ELSE NULL
        END AS account_id,
        CASE
            WHEN (
                CASE
                    WHEN c.contract_type = 'purchase' THEN
                        -(cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                    ELSE
                        (cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                END
            ) < 0 THEN (
                (CASE
                    WHEN c.contract_type = 'purchase' THEN
                        -(cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                    ELSE
                        (cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                END) / NULLIF(COALESCE(rep.repetitions, 24), 0)
            ) * -1
            ELSE 0.0
        END AS credit,
        CASE
            WHEN (
                CASE
                    WHEN c.contract_type = 'purchase' THEN
                        -(cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                    ELSE
                        (cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                END
            ) >= 0 THEN (
                (CASE
                    WHEN c.contract_type = 'purchase' THEN
                        -(cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                    ELSE
                        (cl.specific_price * COALESCE(rep.repetitions, 24) * cl.quantity)
                END) / NULLIF(COALESCE(rep.repetitions, 24), 0)
            )
            ELSE 0.0
        END AS debit
    """

    @api.model
    def _from(self):
        return """
    FROM contract_line cl
    JOIN contract_contract c ON cl.contract_id = c.id
    JOIN res_partner p ON c.partner_id = p.id
    JOIN product_product pp ON cl.product_id = pp.id
    JOIN product_template pt ON pp.product_tmpl_id = pt.id
    JOIN product_category pc ON pt.categ_id = pc.id
    """

    @api.model
    def _left_join(self):
        return """
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_expense_id'
        AND type = 'many2one'
        AND res_id = 'product.template,' || pt.id
        LIMIT 1
    ) ipex ON TRUE
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_income_id'
        AND type = 'many2one'
        AND res_id = 'product.template,' || pt.id
        LIMIT 1
    ) ipin ON TRUE
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_expense_categ_id'
        AND type = 'many2one'
        AND res_id = 'product.category,' || pc.id
        LIMIT 1
    ) ipex_cat ON TRUE
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_income_categ_id'
        AND type = 'many2one'
        AND res_id = 'product.category,' || pc.id
        LIMIT 1
    ) ipin_cat ON TRUE
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_expense_categ_id'
        AND type = 'many2one'
        AND (res_id IS NULL OR res_id = '')
        LIMIT 1
    ) ipd ON TRUE
    LEFT JOIN LATERAL (
        SELECT * FROM ir_property
        WHERE name = 'property_account_income_categ_id'
        AND type = 'many2one'
        AND (res_id IS NULL OR res_id = '')
        LIMIT 1
    ) ipd_income ON TRUE
    """

    @api.model
    def _subquery_repetitions(self):
        return """
    LEFT JOIN (
        SELECT
            cl_inner.id AS contract_line_id,
            COUNT(gs_inner.n) AS repetitions
        FROM contract_line cl_inner
        JOIN generate_series(0, 1000) AS gs_inner(n)
            ON cl_inner.date_start +
                CASE cl_inner.recurring_rule_type
                    WHEN 'daily' THEN (gs_inner.n * cl_inner.recurring_interval || ' days')::interval
                    WHEN 'weekly' THEN (gs_inner.n * cl_inner.recurring_interval || ' weeks')::interval
                    WHEN 'monthly' THEN (gs_inner.n * cl_inner.recurring_interval || ' months')::interval
                    WHEN 'monthlylastday' THEN (gs_inner.n * cl_inner.recurring_interval || ' months')::interval
                    WHEN 'quarterly' THEN (gs_inner.n * 3 * cl_inner.recurring_interval || ' months')::interval
                    WHEN 'semesterly' THEN (gs_inner.n * 6 * cl_inner.recurring_interval || ' months')::interval
                    WHEN 'yearly' THEN (gs_inner.n * cl_inner.recurring_interval || ' years')::interval
                    ELSE '0 days'::interval
                END <= cl_inner.date_end
        WHERE cl_inner.date_start IS NOT NULL
        AND cl_inner.recurring_interval > 0
        GROUP BY cl_inner.id
    ) rep ON rep.contract_line_id = cl.id
    """

    @api.model
    def _join_generate_series_and_where(self):
        return """
    JOIN generate_series(0, 1000) AS gs(n)
        ON gs.n < COALESCE(rep.repetitions, 24)
    WHERE (
        (
            ipex.value_reference IS NOT NULL OR
            ipex_cat.value_reference IS NOT NULL OR
            ipd.value_reference IS NOT NULL
        )
        OR
        (
            ipin.value_reference IS NOT NULL OR
            ipin_cat.value_reference IS NOT NULL OR
            ipd_income.value_reference IS NOT NULL
        )
    )
    """
