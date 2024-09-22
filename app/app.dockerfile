FROM python:3.12-slim

COPY app /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
