# Hive 3.1.3 image plus the PostgreSQL JDBC driver for the metastore. UNTESTED (D-030).
FROM apache/hive:3.1.3
USER root
ADD https://jdbc.postgresql.org/download/postgresql-42.7.3.jar /opt/hive/lib/postgresql.jar
RUN chmod 644 /opt/hive/lib/postgresql.jar
USER hive
