FROM python:3.10-alpine3.16

ENV PYTHONDONTWRITEBYTECODE 1
COPY --from=zricethezav/gitleaks:v8.5.1 /usr/bin/gitleaks /usr/bin/gitleaks

WORKDIR /code
COPY . /code/

ENTRYPOINT ["python", "controller.py"]