FROM alpine

WORKDIR /app

RUN apk update && apk add curl

RUN apk add python3 && apk add py-pip

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app

CMD ["python3", "shorturl.py"]
