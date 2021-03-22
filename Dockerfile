FROM python:3.8.6-alpine

COPY app/requirements.txt /opt/prometheus-jsonpath-exporter/requirements.txt

RUN pip install -r /opt/prometheus-jsonpath-exporter/requirements.txt

COPY app/exporter.py /opt/prometheus-jsonpath-exporter/exporter.py

EXPOSE 9158

ENTRYPOINT ["python", "/opt/prometheus-jsonpath-exporter/exporter.py"]
