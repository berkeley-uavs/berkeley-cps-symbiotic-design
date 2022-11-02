echo "Updating repository from github..."
git pull

# Connect to AWS VPN
echo "Connecting to VPN..."
openvpn --config ../challenge_data/aws-cvpn-config.ovpn --daemon

# Mount shared drive
echo "Mounting shared drive...(it can take some time...)"
mkdir -p ../challenge_data/aws
mount -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws

# Config broker
echo "Configuring broker..."
#pdm run suam-config install --no-symlink --input=../challenge_data/data/broker.conf.yaml
mkdir /etc/xdg/SimpleUAM
mkdir /etc/xdg/SimpleUAM/config
cp ../challenge_data/data/broker.conf.yaml /etc/xdg/SimpleUAM/config

echo "Done"

if [ $# -eq 0 ]
  then
    echo "No parameters provided, background mode"
else
    case "$1" in
      -h|--help)
        echo "options:"
        echo "-h, --help                show brief help"
        ;;
      bash)
        echo "Launching bash..."
        bash
        ;;
      *)
        ;;
    esac
fi