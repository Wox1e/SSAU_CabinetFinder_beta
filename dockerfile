FROM python:3.14.0a3-alpine3.20

WORKDIR /app

COPY . .

EXPOSE 6840

CMD ["python", "main.py"]
