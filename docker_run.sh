#!/bin/bash

port_ssh=9922
my_platform=linux/arm64
container=dev_env_base_310
image=pmallozzi/devenvs:base-310-symcps

cleanup() {
  echo "Checking if container already exists.."
  if [[ $(docker ps -a --filter="name=$container" --filter "status=running" | grep -w "$container") ]]; then
    docker stop $container
    docker rm $container
    echo "Cleaning up..."
  elif [[ $(docker ps -a --filter="name=$container") ]]; then
    docker rm $container || true
    echo "Cleaning up..."
  else
    echo "No existing container found"
  fi
}

main() {
  repo_dir="$(pwd)"
  mount_local=" -v ${repo_dir}:/home/headless/code -v /home/headless/code/__pypackages__"
  port_arg="-p ${port_ssh}:22"

  which docker 2>&1 >/dev/null
  if [ $? -ne 0 ]; then
    echo "Error: the 'docker' command was not found.  Please install docker."
    exit 1
  fi

  cleanup

  case "${1}" in
    bash )
      echo "Entering docker environment..."
      docker run \
        -it \
        --name $container \
        --privileged \
        --workdir /home/headless/code \
        --platform ${my_platform} \
        ${mount_local} \
        $port_arg \
        $image bash
      ;;
    mount )
      echo "Entering docker environment..."
      docker run \
        -d \
        --name $container \
        --privileged \
        --workdir /home/headless/code \
        --platform ${my_platform} \
        ${mount_local} \
        $port_arg \
        $image
      ;;
    *)
      echo "Launching docker environment in background..."
      docker run \
        -d \
        --name $container \
        --privileged \
        --workdir /home/headless/code \
        --platform ${my_platform} \
        $port_arg \
        $image
      ;;

  esac

}

main "$@"

