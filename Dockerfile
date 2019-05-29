
FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /skillbott_service
WORKDIR /skillbott_service
ADD . /skillbott_service/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y mysql-client && rm -rf /var/lib/apt
COPY start.sh /start.sh
EXPOSE 8000
CMD ["/start.sh"]

