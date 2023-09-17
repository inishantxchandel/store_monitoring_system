## Init Postgresql

1. Login postgres\
   `sudo -i -u postgres`\
   ~$ `psql`

2. Create User and Password\
   `CREATE USER user_name with PASSWORD 'password';`

3. Dop Database\
   please remove the old database and create a new one.\
   ~$ `DROP DATABASE db_name;`

4. Create Database\
   ~$ `CREATE DATABASE db_name;`

5. Grant access to user
   ~$ `GRANT ALL ON DATABASE  db_name TO user_name`
# store_monitoring_system
