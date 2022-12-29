FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9 as base

RUN pip install --no-cache-dir sqlalchemy python-jose[cryptography] passlib[bcrypt]



FROM base as development

ENV PYTHONPATH /app
