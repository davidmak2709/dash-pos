
# Dash point of sale embedded system
Point of sale embedded system based on Dash cryptocurrency. The whole project was done on a Raspberry Pi 3 model B+ with the original 7" touch screen running Raspbian Stretch OS. Based on moocowmoo's [dashvend](https://github.com/moocowmoo/dashvend) project

## Requirements
### Hardware requirements
- Raspberry Pi 3 model B+
- Raspberry Pi official 7" touch screen
- [Qibixx MDB Pi Hat](https://www.qibixx.com/en/products/mdb-pi-hat-interface/)
- External drive for blockchain storage
### Software requirements
- Raspbian Stretch OS

## Installation
The first thing to do is an update/upgrade:
```
sudo apt-get update && sudo apt-get upgrade
```
Position yourself in the root of the repository and run the make command.
```
make
```
Edit the [config](./bin/dashvend/config.py.template) file and set your variables.

Place the following commands in crontab:
```
@reboot python3 <path-to-dashvend>/dashvend/bin/start_dashvend.py
0 */1 * * * python3 <path-to-dashvend>/dashvend/bin/conversion/conversion_dash_hrk.py
```
Conversion only works for HRK (Croatian kunas)

### MDB
To get your Raspberry Pi to work with the Pi Hat follow this [official documentation](https://docs.qibixx.com/qibixx-documentation/pi-and-uarts).

### Display
If you want to use the original 7 inch touch screen in /etc/enviroment add the following line:
```bash
DISPLAY=:0
```
and in ~/.bashrc add the following line:
```bash
export DISPLAY=:0
```
In /boot/config.txt place the following lines:
```bash
display_rotate=1 # or different numbers depending on the orientation
```
Finally, in /etc/xdg/lxsession/LXDE-pi/autostart place the following lines:
```bash
@unclutter -idle 0 # remove mouse pointer
@<path-to-dashvend>/dashvend/bin/fliptouch.sh # flip the touch screen(change the script depending
					      # on your rotation
@xset s off # disable screen turn off after 10 minutes
@xset -dpms # disable screen turn off after 10 minutes
```

## Video demo
[Demonstration video](https://youtu.be/A7MZlR-G4GU)

#### Donations  are always welcome
![QR](https://drive.google.com/uc?export=view&id=1HvvJaiPD2KENB2mth5LfvRAXmH7MTAGn)

