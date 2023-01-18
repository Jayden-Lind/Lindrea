FROM python:alpine

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev 

RUN apk add --no-cache build-base
WORKDIR /root/

COPY app.py .
COPY models.py .
ADD realestate_com_au/ realestate_com_au/
COPY crontab .
COPY requirements.txt .
COPY query.py .
ENV TZ="Australia/Melbourne"
RUN pip install -r requirements.txt --no-cache-dir
RUN apk --purge del .build-deps
RUN crontab crontab

CMD ["crond", "-f"]
