FROM python:3.12.2-slim-bookworm
RUN pip install -r requirements.txt
CMD python -m uvicorn main:app --workers 10 --host 

