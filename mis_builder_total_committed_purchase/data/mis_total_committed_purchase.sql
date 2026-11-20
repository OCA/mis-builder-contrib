CREATE OR REPLACE VIEW mis_total_committed_purchase AS (
    SELECT
        ROW_NUMBER() OVER (
            ORDER BY mis_total_committed_purchase.res_model,
                mis_total_committed_purchase.res_id,
                mis_total_committed_purchase.analytic_account_id
        ) AS id,
        mis_total_committed_purchase.* FROM (
        WITH currency_rate as (
            SELECT
              r.currency_id,
              COALESCE(r.company_id, c.id) as company_id,
              r.rate,
              r.name AS date_start,
              (SELECT name FROM res_currency_rate r2
              WHERE r2.name > r.name AND
                    r2.currency_id = r.currency_id AND
                    (r2.company_id is null or r2.company_id = c.id)
               ORDER BY r2.name ASC
               LIMIT 1) AS date_end
            FROM res_currency_rate r
              JOIN res_company c ON (r.company_id is null or r.company_id = c.id)
        ),
        pol_analytic AS (
            SELECT
                pol_d.id,
                split_part(dist.key, ',', 1)::INTEGER AS analytic_account_id,
                dist.value::NUMERIC AS analytic_amount
            FROM purchase_order_line pol_d,
                jsonb_each_text(pol_d.analytic_distribution) AS dist
        ),
        expense_default AS (
            SELECT d.company_id, d.json_value::INTEGER AS account_id
            FROM ir_default d
                JOIN ir_model_fields f ON f.id = d.field_id
            WHERE f.model = 'product.category'
                AND f.name = 'property_account_expense_categ_id'
                AND d.user_id IS NULL
        )

        /* ALL CONFIRMED PURCHASES */
    SELECT
        pol.company_id AS company_id,
        pol.name AS name,
        po.date_planned::date as date,
        pol.product_id as product_id,
        pol.order_id as purchase_order_id,
        pol.id AS res_id,
        'purchase.order.line' AS res_model,
        COALESCE(
            (pt.property_account_expense_id ->> po.company_id::TEXT)::INTEGER,
            (pc1.property_account_expense_categ_id ->> po.company_id::TEXT)::INTEGER,
            (pc2.property_account_expense_categ_id ->> po.company_id::TEXT)::INTEGER,
            (pc3.property_account_expense_categ_id ->> po.company_id::TEXT)::INTEGER,
            (pc4.property_account_expense_categ_id ->> po.company_id::TEXT)::INTEGER,
            (pc5.property_account_expense_categ_id ->> po.company_id::TEXT)::INTEGER,
            (SELECT ed.account_id FROM expense_default ed
             WHERE ed.company_id = po.company_id OR ed.company_id IS NULL
             ORDER BY ed.company_id NULLS LAST LIMIT 1)
        ) AS account_id,

        CASE
            WHEN
                (
                    pol_analytic.analytic_account_id IS NULL
                    OR aaa.id = pol_analytic.analytic_account_id
                )
                AND (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2) >= 0.0
            THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)
                * COALESCE(pol_analytic.analytic_amount, 100.0) / 100.0
            ELSE 0.0
        END AS debit,

        CASE
            WHEN
                (
                    pol_analytic.analytic_account_id IS NULL
                    OR aaa.id = pol_analytic.analytic_account_id
                )
                AND (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)  < 0
            THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * pol.product_qty)::decimal(16,2)
                * COALESCE(pol_analytic.analytic_amount, 100.0) / 100.0
        ELSE 0.0
        END AS credit,
        pol_analytic.analytic_account_id

        FROM purchase_order_line pol
            LEFT JOIN pol_analytic ON pol.id = pol_analytic.id
            LEFT JOIN account_analytic_account aaa ON pol_analytic.analytic_account_id = aaa.id
            LEFT JOIN purchase_order po on po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc1 ON pc1.id = pt.categ_id
            LEFT JOIN product_category pc2 ON pc2.id = pc1.parent_id
            LEFT JOIN product_category pc3 ON pc3.id = pc2.parent_id
            LEFT JOIN product_category pc4 ON pc4.id = pc3.parent_id
            LEFT JOIN product_category pc5 ON pc5.id = pc4.parent_id
            LEFT JOIN currency_rate cur on (cur.currency_id = po.currency_id and
                cur.company_id = po.company_id and
                cur.date_start <= coalesce(po.date_order, now()) and
                (cur.date_end is null or cur.date_end > coalesce(po.date_order, now())))
        WHERE po.state != 'cancel' AND po.state != 'draft'
    ) AS mis_total_committed_purchase
)
