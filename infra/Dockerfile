FROM python:3.13.2-slim@sha256:6b3223eb4d93718828223966ad316909c39813dee3ee9395204940500792b740
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock && pip check
COPY src/ src/
USER 65532:65532
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
