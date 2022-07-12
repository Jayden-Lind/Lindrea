FROM python:alpine

WORKDIR /root/

COPY app.py .
COPY models.py .
ADD realestate_com_au/ realestate_com_au/
COPY crontab .
COPY requirements.txt .
ENV TZ="Australia/Melbourne"
RUN pip install -r requirements.txt

RUN crontab crontab

CMD ["crond", "-f"]
