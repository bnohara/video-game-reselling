CREATE EXTERNAL TABLE prices (
  id string, 
  console_name string, 
  product_name string, 
  loose_price string, 
  cib_price string, 
  new_price string, 
  graded_price string, 
  box_only_price string, 
  manual_only_price string, 
  bgs_10_price string, 
  condition_17_price string, 
  condition_18_price string, 
  gamestop_price string, 
  gamestop_trade_price string, 
  retail_loose_buy string, 
  retail_loose_sell string, 
  retail_cib_buy string, 
  retail_cib_sell string, 
  retail_new_buy string, 
  retail_new_sell string, 
  upc string, 
  sales_volume string, 
  genre string, 
  tcg_id string, 
  asin string, 
  epid string, 
  release_date string
)

PARTITIONED BY (ingest_date string)

ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde' 

WITH SERDEPROPERTIES ( 
  'escapeChar' = '\\', 
  'quoteChar' = '\"', 
  'separatorChar' = ','
) 

LOCATION 's3://BUCKET_NAME/csv-landing'

TBLPROPERTIES (
  'skip.header.line.count' = '1', 
  'use.null.for.invalid.data' = 'true'
);