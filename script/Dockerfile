FROM python:latest

WORKDIR /script/src

COPY ./ /script

COPY requirements.txt /script
COPY src /script/src

RUN apt-get update && apt-get install -y python3-pip
RUN pip install -r /script/requirements.txt
RUN chmod +x /script/src/script.py

CMD ["python3", "/script/src/script.py"]