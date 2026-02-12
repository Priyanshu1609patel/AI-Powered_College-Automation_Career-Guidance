FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm --direct

COPY . .

RUN mkdir -p uploads Career_Guidance_SubProject/uploads

EXPOSE 5000

CMD ["python", "run.py"]
