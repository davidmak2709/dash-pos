
default: deps repos dashd

deps:
	sudo apt-get -y install vim git python3-pil xinput python3-pil.imageTK xscreensaver unclutter curl unzip screen python-setuptools ufw
	sudo pip3 install pyzmq	
	pip3 install pyqrcode screeninfo

repos:
	mkdir -p repos
	cd repos; \
	git clone https://github.com/jgarzik/python-bitcoinrpc.git; \
	git clone https://github.com/richardkiss/pycoin.git; \
	git clone https://github.com/petertodd/python-bitcoinlib.git; \
	ln -f -s ../repos/python-bitcoinrpc/bitcoinrpc ../bin/bitcoinrpc; \
	ln -f -s ../repos/pycoin/pycoin ../bin/pycoin; \
	ln -f -s ../repos/python-bitcoinlib/bitcoin ../bin/bitcoin; \
	cd pycoin; \
	git reset --hard "994c4c714f599c795f4b7d7f305926ca6cdd0349"; \
	sudo python setup.py install

dashd:
	bin/_install_dashd.sh

clean:
	find . -type f -name '*.pyc' -exec rm {} \;
	sudo rm -rf repos bin/bitcoin bin/pycoin bin/bitcoinrpc
