FROM python:3.11.0-slim-bullseye as builder
RUN pip3 install -U poetry
WORKDIR /app
COPY . .
RUN poetry build

FROM python:3.11.0-slim-bullseye
COPY --from=builder /app/dist/ /dist
RUN apt update && apt install -y openssh-client && \
  find /dist -name '*.whl' -exec pip install {} \;

ENTRYPOINT ["hidori-pipeline", "run"]
CMD ["/hidori/pipeline.toml"]
