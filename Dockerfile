# Возьмем за основу образ 
FROM python:3.10

ENV PYTHON_VERSION=3.10

# Airflow глобальные переменные
ARG AIRFLOW_VERSION=2.3.3
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV AIRFLOW_CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Сборка airflow
RUN pip install \
    apache-airflow[postgres]==${AIRFLOW_VERSION} --constraint ${AIRFLOW_CONSTRAINT_URL} \
    pandas


# Создаем директрию для скриптов и базы данных
RUN mkdir /project && mkdir /content

# Копируем скрипты и конфиг файл
COPY script/ /project/scripts/
COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

# Доступы для скрипта
RUN chmod +x /project/scripts/init.sh

# Запускаем sh скрипт
ENTRYPOINT ["/project/scripts/init.sh"]