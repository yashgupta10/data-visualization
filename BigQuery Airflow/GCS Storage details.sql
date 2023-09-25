with item_detail as (
select 

  bucket_id,
  item_size,
  item_content_type,
  item_storage_class,
  item_owner,
  item_time_created,
  item_updated ,
  item_name,
  insert_datetime,
  MAX(insert_datetime) over () as latest_date,
  case when  ARRAY_LENGTH(REGEXP_EXTRACT_ALL(item_name, "/")) >= 1 then 
  SPLIT(item_name, '/')[OFFSET(0) ] else 'root' end  as folder_level1,
   case when  ARRAY_LENGTH(REGEXP_EXTRACT_ALL(item_name, "/")) >= 2 then 
  SPLIT(item_name, '/')[OFFSET(1) ] else null end  as folder_level2,
     case when  ARRAY_LENGTH(REGEXP_EXTRACT_ALL(item_name, "/")) >= 2 then 
  SPLIT(item_name, '/')[OFFSET(2) ] else null end  as folder_level3,
  ARRAY_REVERSE(SPLIT(item_name, '/'))[OFFSET(0) ] as file_name


from `project.dataset.gcs_object_details` as item
where item_size>0
--and bucket_id = 'wx-cd6830b0-5374-4cfd-aa04-4d125c6c9-in'
)
, project_bucket_item as (
SELECT 
  item.* 
  ,bucket.bucket_name
  ,bucket_location
  ,bucket_location_type
  ,bucket_storage_class
  ,projectId
  ,project.name as project_name
  ,labels_cost_centre as project_cost_centre
  ,labels_environment as project_env
  ,labels_business_unit as project_bu
  ,labels_owner as project_owner
  ,labels_project_code as project_code
  ,labels_support_contact as project_support_Contact
  ,labels_squad as project_squad
 FROM item_detail item 
 LEFT JOIN `project.dataset..gcs_bucket_details` bucket
 on item.bucket_id = bucket.bucket_id
 and DATE(item.insert_datetime)  = DATE(bucket.insert_datetime)
 LEFT JOIN `project.dataset..gcp_project_list` project
 on bucket.bucket_project_number = cast(project.projectNumber as NUMERIC)
 and DATE(item.insert_datetime)  = DATE(project.insert_datetime)
 )

select * from project_bucket_item
