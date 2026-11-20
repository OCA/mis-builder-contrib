CREATE OR REPLACE VIEW mis_total_committed_purchase_analytic_account_rel AS(
    SELECT
        po_mcp.id AS mis_total_committed_purchase_id,
        unnest(string_to_array(dist.key, ','))::INTEGER
            AS analytic_account_id

    FROM purchase_order_line AS po_rel
        CROSS JOIN jsonb_each(po_rel.analytic_distribution) AS dist
        INNER JOIN mis_total_committed_purchase AS po_mcp ON
            po_mcp.res_id = po_rel.id

    WHERE CAST(po_mcp.res_model AS VARCHAR) = 'purchase.order.line'

    UNION ALL

    SELECT
        inv_mcp.id AS mis_total_committed_purchase_id,
        unnest(string_to_array(dist.key, ','))::INTEGER
            AS analytic_account_id

    FROM account_move_line AS inv_rel
        CROSS JOIN jsonb_each(inv_rel.analytic_distribution) AS dist
        INNER JOIN mis_total_committed_purchase AS inv_mcp ON
            inv_mcp.res_id = inv_rel.id

    WHERE CAST(inv_mcp.res_model AS VARCHAR) = 'account.move.line'
)
