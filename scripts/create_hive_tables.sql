-- Hive external tables over the HDFS data (D-011). Run with scripts/create_hive_tables.sh.
-- Raw CSVs are all-string tables; processed data is Parquet (columns are matched by name).
CREATE DATABASE IF NOT EXISTS skills_mirage;
USE skills_mirage;

DROP TABLE IF EXISTS raw_jobs;
CREATE EXTERNAL TABLE raw_jobs (
  company STRING, education STRING, experience STRING, industry STRING, jobdescription STRING,
  jobid STRING, joblocation_address STRING, jobtitle STRING, numberofpositions STRING, payrate STRING,
  postdate STRING, site_name STRING, skills STRING, uniq_id STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"', 'escapeChar' = '"')
STORED AS TEXTFILE LOCATION '/skills_mirage/raw/jobs'
TBLPROPERTIES ('skip.header.line.count' = '1');

DROP TABLE IF EXISTS raw_courses;
CREATE EXTERNAL TABLE raw_courses (
  name STRING, source STRING, domain STRING, url STRING, institution STRING,
  duration_weeks STRING, difficulty STRING, skill_tags STRING, syllabus_weeks STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"', 'escapeChar' = '"')
STORED AS TEXTFILE LOCATION '/skills_mirage/raw/courses'
TBLPROPERTIES ('skip.header.line.count' = '1');

DROP TABLE IF EXISTS jobs;
CREATE EXTERNAL TABLE jobs (
  row_id INT, company STRING, education STRING, experience STRING, industry STRING, jobdescription STRING,
  jobid STRING, joblocation_address STRING, jobtitle STRING, numberofpositions STRING, payrate STRING,
  postdate STRING, site_name STRING, skills ARRAY<STRING>, uniq_id STRING,
  city STRING, title STRING, ai_mentions ARRAY<STRING>)
STORED AS PARQUET LOCATION '/skills_mirage/processed/jobs';

DROP TABLE IF EXISTS courses;
CREATE EXTERNAL TABLE courses (
  course_id BIGINT, name STRING, source STRING, domain STRING, url STRING, institution STRING,
  duration_weeks INT, difficulty STRING, skill_tags ARRAY<STRING>, syllabus_weeks ARRAY<STRING>,
  skill_tags_lower ARRAY<STRING>)
STORED AS PARQUET LOCATION '/skills_mirage/processed/courses';

-- Quick checks used for the demo: row counts and the top cities.
SELECT COUNT(*) AS jobs_rows FROM jobs;
SELECT city, COUNT(*) AS n FROM jobs GROUP BY city ORDER BY n DESC LIMIT 5;
