FROM pmallozzi/devenvs:base-310

RUN apt-get update && apt-get install -y \
    graphviz

COPY . /home/headless/code
WORKDIR /home/headless/code

RUN pdm config python.use_venv false
RUN pdm install

ENV PYTHONPATH "/home/headless/code/__pypackages__/3.10/lib:/home/headless/code/src"

