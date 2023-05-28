FROM python:3.8.5
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]