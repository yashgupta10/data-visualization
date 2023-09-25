-- Sample SQL to pull compute and storage details for a GCP project

SELECT
creation_time,
main.project_id,
referenced_tables.dataset_id,
user_email,
job_id,
job_type,
total_bytes_processed,
total_slot_ms,
cache_hit,
labels.key,
case when STARTS_WITH(key,'dts') then 'query_run' else value end as value,
STRING_AGG(distinct referenced_tables.table_id,',') as refrenced_tables,
STRING_AGG(distinct destination_table.table_id,',') as destination_tables,
STRING_AGG(distinct job_stages.compute_mode,',') as compute_mode,




FROM
  `gcp-project`.`region-us`.INFORMATION_SCHEMA.JOBS as main,
  UNNEST (referenced_tables) as referenced_tables ,
  UNNEST (labels) as labels,
  UNNEST (job_stages) as job_stages
WHERE

  creation_time BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY) AND CURRENT_TIMESTAMP()

  group by 1,2,3,4,5,6,7,8,9,10,11 ;
  
 SELECT * FROM 
 `gcp-project`.`region-us`.INFORMATION_SCHEMA.TABLE_STORAGE
where deleted =FALSE
order by active_logical_bytes desc ;