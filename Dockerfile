FROM pmallozzi/devenvs:base-310


RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg |  dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&&  chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" |  tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&&  apt update \
&&  apt install gh -y




RUN apt-get update && apt-get install -y \
    graphviz \
    openvpn \
    nfs-common \
    gh


WORKDIR /root

RUN mkdir host ide

COPY . /root/host
WORKDIR /root/host


RUN pdm config python.use_venv false
RUN pdm install

ENV PYTHONPATH "/root/host/__pypackages__/3.10/lib:/root/host/src"

ENTRYPOINT ["./entrypoint.sh"]