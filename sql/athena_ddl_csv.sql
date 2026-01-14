-- Athena external tables (CSV) for the synthetic dataset.
-- This is the easiest path if you cannot generate Parquet locally.
--
-- Update the S3 LOCATIONs to match your bucket + prefix.
--
-- Example:
--   s3://your-bucket/data-analytics-demo/events/
--   s3://your-bucket/data-analytics-demo/orders/

CREATE DATABASE IF NOT EXISTS analytics_demo;

-- EVENTS (CSV)
CREATE EXTERNAL TABLE IF NOT EXISTS analytics_demo.events_csv (
  event_id string,
  event_ts string,
  event_date string,
  user_id string,
  session_id string,
  event_type string,
  product_id string,
  product_name string,
  device string,
  country string,
  traffic_source string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '\"',
  'escapeChar'    = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://REPLACE_ME_BUCKET/REPLACE_ME_PREFIX/events/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- ORDERS (CSV)
CREATE EXTERNAL TABLE IF NOT EXISTS analytics_demo.orders_csv (
  order_id string,
  order_ts string,
  order_date string,
  user_id string,
  session_id string,
  product_id string,
  product_name string,
  quantity int,
  unit_price double,
  revenue double,
  currency string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar'     = '\"',
  'escapeChar'    = '\\'
)
STORED AS TEXTFILE
LOCATION 's3://REPLACE_ME_BUCKET/REPLACE_ME_PREFIX/orders/'
TBLPROPERTIES ('skip.header.line.count'='1');


