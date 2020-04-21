FROM python:3

RUN mkdir /app/
WORKDIR /app/

ADD *.py /app/
ADD funia_generators.json /app/
ADD haarcascade_frontalface_default.xml /app/
ADD cmd/* /app/cmd/
ADD cv_modules/* /app/cv_modules/

COPY requirements.txt /
RUN pip install -r /requirements.txt

CMD ["python", "app/bot.py"]