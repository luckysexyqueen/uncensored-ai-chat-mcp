FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

ENV UNCENSORED_API_KEY="uai_sk_live_7nhIQn3hiJ5gUdj8_tV3WJktMbSTWYOSRvKsHzENnz1ZtpZM1b13a"
EXPOSE 8000

CMD ["python", "server.py", "--transport", "streamable-http"]
