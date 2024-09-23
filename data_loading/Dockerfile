FROM python:3.12

WORKDIR /app

COPY data_loading/requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY data_loading/data_loading.py data_loading.py

COPY relation_extraction relation_extraction

CMD ["python", "data_loading.py"]