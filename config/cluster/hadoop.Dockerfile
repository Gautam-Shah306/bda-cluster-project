# Image for the Hadoop nodes (hdp-master, hdp-worker1, hdp-worker2).
# Java 11 (copied from the Temurin image) + Python 3.11 + Hadoop 3.3.6 + PySpark 3.5.x
# + the Hive 3.1.3 jars copied directly from the already-pulled apache/hive:3.1.3 image (D-012).
FROM eclipse-temurin:11-jdk AS java
FROM apache/hive:3.1.3 AS hive-src

FROM python:3.11-slim-bookworm
COPY --from=java /opt/java/openjdk /opt/java/openjdk
COPY --from=hive-src /opt/hive/lib /opt/hive-jars
ENV JAVA_HOME=/opt/java/openjdk \
    HADOOP_HOME=/opt/hadoop \
    HIVE_JARS_DIR=/opt/hive-jars \
    HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop \
    SPARK_CONF_DIR=/workspace/config/spark \
    HDFS_NAMENODE_USER=root HDFS_DATANODE_USER=root HDFS_SECONDARYNAMENODE_USER=root \
    YARN_RESOURCEMANAGER_USER=root YARN_NODEMANAGER_USER=root
ENV PATH=$PATH:$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

RUN apt-get update && apt-get install -y --no-install-recommends curl procps ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG HADOOP_VERSION=3.3.6
# Use Apache fast CDN mirror for instant download
RUN curl -fsSL https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
      | tar -xz -C /opt && mv /opt/hadoop-${HADOOP_VERSION} /opt/hadoop

# Python dependencies of the pipeline (pyspark version comes from requirements.txt).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY config/cluster/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
