#!/bin/bash

port_ssh=9922
repo_dir="$(pwd)"
container=sym_cps
image=pmallozzi/devenvs:base-310-symcps
challenge_data_relative_path=../challenge_data/

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

main() {

  docker pull ${image}

  repo_dir="$(pwd)"
  challenge_data_dir=$(readlink -f ${challenge_data_relative_path})
  mount_arg=" -v ${repo_dir}:/root/host -v ${challenge_data_dir}:/root/challenge_data -v /root/host/__pypackages__"
  port_arg="-p ${port_ssh}:22"

  echo "Pruning containers"
  docker container prune -f
  echo ${mount_arg}
  echo  ${port_arg}
#  docker run \
#    -d \
#    --name $container \
#    --privileged \
#    --workdir /root/host \
#    ${mount_arg} \
#    ${port_arg} \
#    $image
#  docker run -d --name sym_cps-repo --privileged --workdir /root/host -v .:/root/host
}

main "$@"
