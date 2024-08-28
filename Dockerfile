
FROM python:3.12-bookworm AS python-base

WORKDIR /src

COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

RUN mkdir persistent

ENV PYTHONUNBUFFERED=1

CMD ["python3.12","__main__.py"]
