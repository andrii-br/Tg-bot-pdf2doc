FROM python:3.12

WORKDIR /tgbot

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "bot.py" ]






