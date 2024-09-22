FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY data_insertion.py data_insertion.py

COPY relation_extraction relation_extraction

CMD ["python", "data_insertion.py"]