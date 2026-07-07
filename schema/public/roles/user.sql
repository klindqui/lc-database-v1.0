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

-- CREATE ERICA'S USER
CREATE USER ericaholswade
WITH LOGIN
PASSWORD 'placeholderpass';

GRANT db_admin to ericaholswade

REVOKE db_admin FROM ericaholswade;
GRANT data_analyst TO ericaholswade;

-- OTHER USERS

-- charles here
CREATE USER cbarry
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO cbarry;

-- uncle 
CREATE USER rlindquist
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO rlindquist;

-- marc
CREATE USER mweiss
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO mweiss;

-- mark
CREATE USER mkrikorian
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO mkrikorian;

-- glenn
CREATE USER ghitchcock
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO ghitchcock;

-- sarah
CREATE USER swilliams
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO swilliams;

-- ganesh
CREATE USER gnehru
WITH LOGIN
PASSWORD 'placeholderpass';
GRANT data_analyst TO gnehru;

