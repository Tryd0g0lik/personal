FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN mkdir /www && \
    mkdir /www/src \
    mkdir /www/src/static
WORKDIR /www/src
COPY ./requirements.txt .

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org"
RUN python -m pip install --upgrade "pip>=25.0"
# --no-cache-dir
RUN pip install -r requirements.txt
COPY . .
RUN rm -rf person/migrations && \
    mkdir person/migrations
COPY person/__init__.py person/migrations/__init__.py
