FROM python:3.11.0rc2-slim-bullseye as builder
RUN pip3 install -U poetry
WORKDIR /app
COPY . .
RUN poetry build

FROM python:3.11.0rc2-slim-bullseye
COPY --from=builder /app/dist/ /dist
RUN apt update && apt install -y openssh-client && \
  find /dist -name '*.whl' -exec pip install {} \;
