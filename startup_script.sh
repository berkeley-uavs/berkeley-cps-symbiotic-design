if [ $# -eq 0 ]; then
  echo "No parameters provided. Launching bash"
  bash
else
  while test $# -gt 0; do
    case "$1" in
    -h | --help)
      echo "options:"
      echo "-h, --help                show brief help"
      echo "-r,                       launch random designs evaluation"
      exit 0
      ;;
    -r)
      bash
      ;;
    *)
      echo "Unknown option. Launching $1.."
      eval $1
      ;;
    esac
  done
fi

tail -f /dev/null
