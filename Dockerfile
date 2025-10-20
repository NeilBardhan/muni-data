# muni-data-ingest-pipeline
FROM python:3.11-slim

RUN apt-get update \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
wget ca-certificates make curl

WORKDIR /app
COPY . /app

# Download and install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install package dependencies
RUN poetry install

# TODO orchestrator script
COPY scripts/muni_data_pipeline.sh /usr/local/bin/muni_data_pipeline.sh
RUN chmod +x /usr/local/bin/muni_data_pipeline.sh
ENTRYPOINT ["muni_data_pipeline.sh"]


# CMD ["functions-framework", "--target", "main"]
