FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY artifacts/model.joblib ./artifacts/model.joblib
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app
CMD ["sh", "-c", "streamlit run src/app/app.py --server.address=0.0.0.0 --server.port=${PORT:-8080} --server.headless=true"]
