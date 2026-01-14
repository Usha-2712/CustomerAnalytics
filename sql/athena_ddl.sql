-- Athena external tables (Parquet) for the synthetic dataset.
-- Update the S3 LOCATIONs to match your bucket + prefix.
--
-- Example:
--   s3://your-bucket/data-analytics-demo/events/
--   s3://your-bucket/data-analytics-demo/orders/

CREATE DATABASE IF NOT EXISTS analytics_demo;

-- EVENTS
CREATE EXTERNAL TABLE IF NOT EXISTS analytics_demo.events (
  event_id string,
  event_ts timestamp,
  event_date date,
  user_id string,
  session_id string,
  event_type string,
  product_id string,
  product_name string,
  device string,
  country string,
  traffic_source string
)
STORED AS PARQUET
LOCATION 's3://REPLACE_ME_BUCKET/REPLACE_ME_PREFIX/events/';

-- ORDERS
CREATE EXTERNAL TABLE IF NOT EXISTS analytics_demo.orders (
  order_id string,
  order_ts timestamp,
  order_date date,
  user_id string,
  session_id string,
  product_id string,
  product_name string,
  quantity int,
  unit_price double,
  revenue double,
  currency string
)
STORED AS PARQUET
LOCATION 's3://REPLACE_ME_BUCKET/REPLACE_ME_PREFIX/orders/';


