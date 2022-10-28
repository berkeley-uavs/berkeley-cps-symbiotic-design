FROM pmallozzi/devenvs:base-310

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY . /project
WORKDIR /project

RUN pdm config python.use_venv false
RUN pdm install --prod --no-lock --no-editable

ENV PYTHONPATH=/project/pkgs
RUN cp /project/__pypackages__/3.10/lib /project/pkgs


