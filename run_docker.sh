#!/bin/bash

container=dev_env_base_310
image=pmallozzi/devenvs:base-310
port_ssh=9922

cleanup() {
  if [[ $(docker ps -a --filter="name=$container" --filter "status=exited" | grep -w "$container") ]]; then
    docker rm $container || true
    echo "Cleaning up..."
  elif [[ $(docker ps -a --filter="name=$container" --filter "status=running" | grep -w "$container") ]]; then
    docker stop $container
    docker rm $container
    echo "Cleaning up..."
  else
    echo "No existing container found"
  fi
}

main() {
  pwd_dir="$(pwd)"
  mount_local=" -v ${pwd_dir}:/home/headless/code"
  port_arg="-p $portssh:22"

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
        --platform linux/arm64 \
        ${mount_local} \
        $port_arg \
        $image bash
      ;;
    *)
      echo "Launching docker environment in background..."
      docker run \
        -d \
        --name $container \
        --privileged \
        --workdir /home/headless/code \
        --platform linux/arm64 \
        ${mount_local} \
        $port_arg \
        $image
      ;;

  esac

}

main $@
