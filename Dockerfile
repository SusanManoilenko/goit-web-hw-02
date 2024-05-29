FROM python:3.12
LABEL authors="Сюзанна"

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "hw-1.py"]