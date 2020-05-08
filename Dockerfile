FROM python:3

WORKDIR /

COPY requirements.txt /
RUN pip install -r /requirements.txt

ARG bot_version="unknown version"
ENV BOT_VERSION=$bot_version

RUN mkdir /data/
RUN mkdir /config/

ADD *.py /
ADD funia_generators.json /
ADD static/* /static/
ADD cmd/* /cmd/
ADD cv_modules/* /cv_modules/

CMD ["python", "bot.py"]