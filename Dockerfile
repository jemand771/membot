FROM python:3

WORKDIR /

ADD *.py /
ADD funia_generators.json /
ADD static/* /static/
ADD cmd/* /cmd/
ADD cv_modules/* /cv_modules/

COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN mkdir /data/
RUN mkdir /config/

CMD ["python", "bot.py"]