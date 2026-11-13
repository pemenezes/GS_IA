# Serviço do Luz Cidadã (API e página de teste). O Ollama roda fora do container, no host.
# A base (com as páginas gov.br locais e os índices) e o cache do Hugging Face entram por volume:
# a imagem só tem o código e as dependências. Uso: docker compose up --build (ver README).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_OFFLINE=1

WORKDIR /app

COPY requirements.txt .
RUN grep -v -E '^(jupyter|nbconvert|pytest|ruff)==' requirements.txt > /tmp/requirements-servico.txt \
    && pip install -r /tmp/requirements-servico.txt

COPY config.yaml pyproject.toml ./
COPY src ./src
COPY dados/paradas_simuladas.csv ./dados/

EXPOSE 8000
CMD ["uvicorn", "src.servico.app:app", "--host", "0.0.0.0", "--port", "8000"]
