# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = 'bento/ubuntu-16.04'
  config.vm.network 'private_network', ip: '192.168.60.61'
  config.vm.provision 'shell', path: 'vagrant-provision.sh'
end
