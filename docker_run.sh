#!/bin/bash

port_ssh=9922
container=dev_env_base_310
image=pmallozzi/devenvs:base-310-symcps
challenge_data_relative_path=../challenge_data/

my_platform=""
case $(uname -m) in
    x86_64 | i686 | i386) my_platform="linux/amd64" ;;
    arm)    my_platform="linux/arm64" ;;
esac


docker pull ${image}


resolve_relative_path() (
    # If the path is a directory, we just need to 'cd' into it and print the new path.
    if [ -d "$1" ]; then
        cd "$1" || return 1
        pwd
    # If the path points to anything else, like a file or FIFO
    elif [ -e "$1" ]; then
        # Strip '/file' from '/dir/file'
        # We only change the directory if the name doesn't match for the cases where
        # we were passed something like 'file' without './'
        if [ ! "${1%/*}" = "$1" ]; then
            cd "${1%/*}" || return 1
        fi
        # Strip all leading slashes upto the filename
        echo "$(pwd)/${1##*/}"
    else
        return 1 # Failure, neither file nor directory exists.
    fi
)



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
  challenge_data_dir=$(readlink -f ${challenge_data_relative_path})
  echo $challenge_data_dir
  mount_local=" -v ${repo_dir}:/root/host -v ${challenge_data_dir}:/root/challenge_data -v /root/host/__pypackages__"
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
        --workdir /root/host \
        --platform ${my_platform} \
        ${mount_local} \
        $port_arg \
        $image ${1}
      ;;
    * )
      echo "Launching docker environment in background..."
      docker run \
        -d \
        --name $container \
        --privileged \
        --workdir /root/host \
        --platform ${my_platform} \
        ${mount_local} \
        $port_arg \
        $image
      ;;

  esac

}

main "$@"

