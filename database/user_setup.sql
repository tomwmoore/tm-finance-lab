-- ===================================================
-- User Setup for tmfl_db (Azure SQL db)
-- ===================================================

USE tmfl_db;

-- Read-write & ddl user for ingestion scripts and creating new tables/objects (for flexible analysis)
CREATE USER analytics_user WITH PASSWORD = '_for_@nalytics!123';
ALTER ROLE db_datareader ADD MEMBER analytics_user;
ALTER ROLE db_datawriter ADD MEMBER analytics_user;
ALTER ROLE db_ddladmin ADD MEMBER analytics_user;

-- Read-only user (for dashboard)
CREATE USER dashboard_user WITH PASSWORD = '_for_d@shbord!123!';
ALTER ROLE db_datareader ADD MEMBER dashboard_user;

-- Verify users
SELECT name, type_desc FROM sys.database_principals;
