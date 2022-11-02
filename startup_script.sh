echo "Updating repository from github..."
git reset --hard
git config pull.rebase true
git pull

# Connect to AWS VPN
echo "Connecting to VPN..."
openvpn --config ../challenge_data/aws-cvpn-config.ovpn --daemon

# Mount shared drive
echo "Mounting shared drive..."
mount -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws

# Config broker
echo "Configuring broker..."
pdm run suam-config install --no-symlink --input=../challenge_data/data/broker.conf.yaml

if [ $# -eq 0 ]
  then
    echo "No parameters provided, background mode"
else
    while test $# -gt 0; do
      case "$1" in
        -h|--help)
          echo "options:"
          echo "-h, --help                show brief help"
          exit 0
          ;;
        bash)
          echo "Launching bash..."
          bash
          ;;
        *)
          break
          ;;
      esac
    done
fi