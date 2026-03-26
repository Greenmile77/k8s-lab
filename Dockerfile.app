FROM python:3.9-slim
WORKDIR /app
RUN pip install flask psycopg2-binary
COPY app.py .
EXPOSE 8080
CMD ["python", "app.py"]
