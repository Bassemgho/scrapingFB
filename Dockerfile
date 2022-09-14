FROM python:3.8-slim-buster
EXPOSE 8080
USER root
RUN apt-get update \
  && apt-get update; apt-get -y install curl \
  && apt-get -y install gcc gnupg2 \
  && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update \
  && ACCEPT_EULA=Y apt-get -y install msodbcsql17 \
  && ACCEPT_EULA=Y apt-get -y install mssql-tools

RUN echo "export PATH='$PATH:/opt/mssql-tools/bin'" >> ~/.bashrc \
  && echo "export PATH='$PATH:/opt/mssql-tools/bin'" >> ~/.bashrc 
  # && source ~/.bashrc
WORKDIR /app

COPY ./app-vol .

RUN pip install pyodbc pandas sqlalchemy facebook_scraper "fastapi[all]" mechanize cookiejar
CMD [ "python","main.py" ]