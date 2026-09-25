FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends make git && rm -rf /var/lib/apt/lists/*
RUN addgroup --system python && adduser --system --group python
RUN mkdir opt/app
RUN chown -R python:python opt/app
USER python

ENV VIRTUAL_ENV=/opt/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /opt/app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip --default-timeout=1000 install -r requirements.txt

COPY ./data ./data
COPY app.py app.py
COPY sync_translate.py sync_translate.py
COPY test.xml test.xml
COPY worker_metadata.py worker_metadata.py
COPY worker_paragraphs.py worker_paragraphs.py
COPY worker_translations.py worker_translations.py
COPY Makefile Makefile

ENV PYTHONPATH "${PYTHONPATH}:/opt/app"
ENTRYPOINT ["make", "-f", "/opt/app/Makefile", "start_inside_docker"]