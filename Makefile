
default: deps repos dashd priority

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

priority:
	find ~/.local/lib/python3.[0-9]/site-packages -maxdepth 0 -exec cp -r ./bin/priorityentry/ {} \;

clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	find ~/.local/lib/python3.[0-9]/site-packages -maxdepth 0 -exec rm -r {}/priorityentry \;
	sudo rm -rf repos bin/bitcoinrpc
