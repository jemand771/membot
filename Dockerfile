FROM python:3

RUN pwd
RUN ls

COPY *.py /app/
COPY funia_generators.json /app/
COPY haarcascade_frontalface_default.xml /app/
COPY cmd /app/
COPY cv_modules /app/

RUN pip install -r $GITHUB_WORKSPACE/requirements.txt

WORKDIR /app
CMD ["python", "bot.py"]