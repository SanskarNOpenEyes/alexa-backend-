FROM python:3.12.2-slim-bookworm
WORKDIR /app
ADD . ./
RUN pip install -r requirements.txt
EXPOSE 8001
CMD python3 -m uvicorn main:app --workers 10 --host 0.0.0.0 --port 8000
