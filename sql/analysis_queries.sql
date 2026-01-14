-- Example analytics queries for Athena (or any SQL engine with minor tweaks).

-- 1) Executive KPIs (last 30 days)
SELECT
  COUNT(DISTINCT e.user_id) AS users,
  COUNT(DISTINCT e.session_id) AS sessions,
  COUNT(DISTINCT o.order_id) AS orders,
  ROUND(SUM(o.revenue), 2) AS revenue_usd,
  ROUND(CAST(COUNT(DISTINCT o.order_id) AS double) / NULLIF(COUNT(DISTINCT e.session_id), 0), 4) AS orders_per_session
FROM analytics_demo.events e
LEFT JOIN analytics_demo.orders o
  ON e.session_id = o.session_id;

-- 2) Daily revenue + orders
SELECT
  o.order_date,
  COUNT(DISTINCT o.order_id) AS orders,
  ROUND(SUM(o.revenue), 2) AS revenue_usd
FROM analytics_demo.orders o
GROUP BY 1
ORDER BY 1;

-- 3) Funnel counts (sessions that reached each step)
WITH session_steps AS (
  SELECT
    session_id,
    MAX(CASE WHEN event_type = 'product_view' THEN 1 ELSE 0 END) AS did_view,
    MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS did_cart,
    MAX(CASE WHEN event_type = 'checkout' THEN 1 ELSE 0 END) AS did_checkout,
    MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS did_purchase
  FROM analytics_demo.events
  GROUP BY 1
)
SELECT
  COUNT(*) AS sessions_total,
  SUM(did_view) AS sessions_viewed,
  SUM(did_cart) AS sessions_carted,
  SUM(did_checkout) AS sessions_checkout,
  SUM(did_purchase) AS sessions_purchased
FROM session_steps;

-- 4) Conversion rate by device
WITH per_session AS (
  SELECT
    session_id,
    MAX(device) AS device,
    MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchased
  FROM analytics_demo.events
  GROUP BY 1
)
SELECT
  device,
  COUNT(*) AS sessions,
  SUM(purchased) AS purchases,
  ROUND(CAST(SUM(purchased) AS double) / NULLIF(COUNT(*), 0), 4) AS conversion_rate
FROM per_session
GROUP BY 1
ORDER BY conversion_rate DESC;

-- 5) Top products by revenue
SELECT
  product_id,
  product_name,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(revenue), 2) AS revenue_usd
FROM analytics_demo.orders
GROUP BY 1, 2
ORDER BY revenue_usd DESC
LIMIT 15;


