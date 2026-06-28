-- CREATE USERS

CREATE USER katherine
WITH LOGIN
PASSWORD 'placeholderpass';

CREATE USER pipeline_user
WITH LOGIN
PASSWORD 'placeholderpass';

-- GRANT PERMISSIONS

GRANT db_admin TO katherine;

GRANT data_uploader TO pipeline_user;