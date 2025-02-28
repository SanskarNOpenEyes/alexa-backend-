FROM python:3.12.2-slim-bookworm
WORKDIR /app
ADD . ./
RUN pip install -r requirements.txt
CMD python -m uvicorn main:app --workers 10 --host 34.16.121.9

