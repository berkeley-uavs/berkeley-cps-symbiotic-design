FROM pmallozzi/devenvs:base-310


RUN dpkg --configure -a

#RUN apt-get update && apt-get install -y \
#    graphviz \
#    openvpn \
#    nfs-common

RUN apt-get update

RUN apt-get install -y graphviz

RUN apt-get install -y openvpn

RUN apt-get install -y nfs-common


WORKDIR /root

RUN mkdir host ide

COPY . /root/host
WORKDIR /root/host

RUN pdm config python.use_venv false
RUN pdm install

ENV PYTHONPATH "/root/host/__pypackages__/3.10/lib:/root/host/src"

ENTRYPOINT ["./entrypoint.sh"]