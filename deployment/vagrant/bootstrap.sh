#!/usr/bin/env bash
#
# Prepares a virtual machine for running TFB

# A shell provisioner is called multiple times
if [ ! -e "~/.firstboot" ]; then

  # Workaround mitchellh/vagrant#289
  echo "grub-pc grub-pc/install_devices multiselect     /dev/sda" | sudo debconf-set-selections

  # Install prerequisite tools
  echo "Installing docker"
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -yqq
  sudo apt-get install -yqq docker-ce docker-ce-cli containerd.io
  sudo usermod -aG docker vagrant

  # Setting up passwordless sudo
  echo "vagrant ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers

  sudo chown vagrant:vagrant ~/FrameworkBenchmarks
  cd ~/FrameworkBenchmarks

  # Setup a nice welcome message for our guest
  echo "Setting up welcome message"
  sudo rm -f /etc/update-motd.d/51-cloudguest
  sudo rm -f /etc/update-motd.d/98-cloudguest

  sudo cat <<EOF > motd
Welcome to the FrameworkBenchmarks project!

  You can get lots of help:
    $ ssgberk --help

  You can run a test like:
    $ ssgberk --test hugo -nf 10

  This Vagrant environment is already setup and ready to go.
EOF

  cat <<EOF > /home/vagrant/.bash_aliases
alias ssgberk="/home/vagrant/FrameworkBenchmarks/ssgberk"
EOF

  sudo mv motd /etc/
  sudo chmod 777 /var/run/docker.sock
fi
