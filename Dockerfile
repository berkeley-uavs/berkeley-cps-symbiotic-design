FROM pmallozzi/devenvs:base-310

RUN apt-get update && apt-get install -y \
    graphviz

COPY . /home/headless/temp
WORKDIR /home/headless/temp

RUN pdm config python.use_venv false
RUN pdm install

RUN mkdir /home/headless/dependencies
RUN cp -r /home/headless/temp/__pypackages__/ /home/headless/dependencies

RUN cp /home/headless/temp/entrypoint.sh /home/headless/code/
#RUN chmod +x /home/headless/code/entrypoint.sh

RUN rm -r /home/headless/temp

ENV PYTHONPATH "/home/headless/code/__pypackages__/3.10/lib:/home/headless/code/src"

WORKDIR /home/headless/code

ENTRYPOINT ["./entrypoint.sh"]