FROM python:3.12-slim

WORKDIR /app

RUN pip install dbt-bigquery==1.8.0

COPY . .
RUN dbt deps

ENTRYPOINT ["dbt"]
CMD ["run", "--target", "prod"]
