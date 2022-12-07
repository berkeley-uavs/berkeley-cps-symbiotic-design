echo "Updating repository from github..."
git pull

if [ $# -eq 0 ]
  then
    echo "No parameters provided, background mode"
else
    case "$1" in
      -h|--help)
        echo "options:"
        echo "-h, --help                show brief help"
        exit 0
        ;;
      bash)
        echo "Launching bash..."
        bash
        exit 0
        ;;
      *)
        ;;
    esac
fi

exit 0