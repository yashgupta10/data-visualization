WITH audit_log as (
SELECT  
resource.labels.dataset_id,
resource.labels.project_id,
--protopayload_auditlog.methodName,
REGEXP_EXTRACT('google.cloud.bigquery.v2.TableService.UpdateTable',r'.*\.([^/$]*)(?:\.)') as service,
REGEXP_EXTRACT(protopayload_auditlog.methodName,r'.*\.([^/$]*)') as method,
--protopayload_auditlog.resourceName,
REGEXP_EXTRACT(protopayload_auditlog.resourceName,r'.*tables\/([^/$]*)') as tableName,
REGEXP_CONTAINS(protopayload_auditlog.authenticationInfo.principalEmail,r'.+(@woolworths\.com\.au)') as is_ww_email,
protopayload_auditlog.authenticationInfo.principalEmail,
protopayload_auditlog.metadataJson,
COALESCE(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableCreation"),"$.table"),"$.view"),"$.query"), JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableChange"),"$.table"),"$.view"),"$.query"), JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDeletion"),"$.reason") ) as query,
case when JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableCreation") is not null then 'tableCreation'
when JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableChange") is not null then 'tableChange'
when  JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDeletion") is not null then 'tableDeletion'
else 'N/A' end as type,
receiveTimestamp

FROM `gcp-wow-rwds-ai-bi-prod.bq_auditlog.cloudaudit_googleapis_com_activity_*` -- Get data from all table partitions
WHERE DATE(timestamp) >= "2022-07-10" 
and severity = 'NOTICE'-- Exclude ERROR

--and protopayload_auditlog.authenticationInfo.principalEmail like '%ygupta%'
and protopayload_auditlog.methodName in 
          ('google.cloud.bigquery.v2.TableService.PatchTable',
          'google.cloud.bigquery.v2.TableService.UpdateTable',
          'google.cloud.bigquery.v2.TableService.InsertTable',
          'google.cloud.bigquery.v2.JobService.InsertJob',
          'google.cloud.bigquery.v2.TableService.DeleteTable',
          'google.cloud.bigquery.v2.JobService.Query' ) 
UNION ALL
SELECT  
resource.labels.dataset_id,
resource.labels.project_id,
--protopayload_auditlog.methodName,
REGEXP_EXTRACT('google.cloud.bigquery.v2.TableService.UpdateTable',r'.*\.([^/$]*)(?:\.)') as service,
REGEXP_EXTRACT(protopayload_auditlog.methodName,r'.*\.([^/$]*)') as method,
--protopayload_auditlog.resourceName,
REGEXP_EXTRACT(protopayload_auditlog.resourceName,r'.*tables\/([^/$]*)') as tableName,
REGEXP_CONTAINS(protopayload_auditlog.authenticationInfo.principalEmail,r'.+(@woolworths\.com\.au)') as is_ww_email,
protopayload_auditlog.authenticationInfo.principalEmail,
protopayload_auditlog.metadataJson,
COALESCE(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableCreation"),"$.table"),"$.view"),"$.query"), JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableChange"),"$.table"),"$.view"),"$.query"), JSON_EXTRACT(JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDeletion"),"$.reason") ) as query,
case when JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableCreation") is not null then 'tableCreation'
when JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableChange") is not null then 'tableChange'
when  JSON_EXTRACT(protopayload_auditlog.metadataJson, "$.tableDeletion") is not null then 'tableDeletion'
else 'N/A' end as type,
 receiveTimestamp

FROM `gcp-wow-rwds-ai-data-prod.bq_auditlog.cloudaudit_googleapis_com_activity_*` 
WHERE DATE(timestamp) >= "2022-07-10" 
and severity = 'NOTICE'-- Exclude ERROR
--and protopayload_auditlog.authenticationInfo.principalEmail like '%ygupta%'
and protopayload_auditlog.methodName in 
          ('google.cloud.bigquery.v2.TableService.PatchTable',
          'google.cloud.bigquery.v2.TableService.UpdateTable',
          'google.cloud.bigquery.v2.TableService.InsertTable',
          'google.cloud.bigquery.v2.JobService.InsertJob',
          'google.cloud.bigquery.v2.TableService.DeleteTable',
          'google.cloud.bigquery.v2.JobService.Query' )

)


select 
  dataset_id,
  project_id,
  service,
  method || '-' || type as change_type,
  tableName,
  is_ww_email,
  principalEmail,
  query,
  receiveTimestamp,
  ROW_NUMBER() over (partition by dataset_id,project_id,tableName order by receiveTimestamp desc) as change_order,
  ROW_NUMBER() over (partition by dataset_id,project_id,tableName order by case when type = 'tableCreation' then 1 else 0 end desc, receiveTimestamp asc) as change_order_table_creation,
  metadataJson,
 case when query = LAG(query)  OVER (PARTITION BY project_id,dataset_id,tableName ORDER BY receiveTimestamp ASC) then 'No'
 when LAG(query)  OVER (PARTITION BY project_id,dataset_id,tableName ORDER BY receiveTimestamp ASC) is NULL then 'N/A'
 else 'Yes' end as query_changed,
 LAST_VALUE(is_ww_email)  OVER (PARTITION BY project_id,dataset_id,tableName,type  ORDER BY receiveTimestamp ASC RANGE BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS last_created_by_mail_type
FROM audit_log
where type != 'N/A'
and tableName = 'gt_lcd'
order by receiveTimestamp asc
