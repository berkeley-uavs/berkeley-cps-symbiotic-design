FROM pmallozzi/devenvs:base-310

RUN apt-get update && apt-get install -y \
    graphviz

WORKDIR /root

RUN mkdir host ide

COPY . /root/host
WORKDIR /root/host

RUN pdm config python.use_venv false
RUN pdm install

ENV PYTHONPATH "/root/host/__pypackages__/3.10/lib:/root/host/src"

