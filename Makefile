
default: deps repos dashd

deps:
	sudo apt-get -y install vim git python3-pil xinput python3-pil.imageTK xscreensaver unclutter curl unzip screen python-setuptools ufw
	sudo pip3 install pyzmq
	pip3 install pyqrcode screeninfo

repos:
	mkdir -p repos
	cd repos; \
	git clone https://github.com/jgarzik/python-bitcoinrpc.git; \
	ln -f -s ../repos/python-bitcoinrpc/bitcoinrpc ../bin/bitcoinrpc; \
	
dashd:
	bin/_install_dashd.sh

clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	sudo rm -rf repos bin/bitcoin bin/pycoin bin/bitcoinrpc
