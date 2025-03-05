FROM python:3.12-slim

COPY dist /dist
RUN pip install /dist/*.whl

CMD ["python", "-m", "rox_septentrio"]
