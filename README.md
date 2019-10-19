# Kontability Web App
Simple app to keep track of house bills payment.

## Usage
With `python3` and `pip3` installed run the `launch.sh` script in the main project folder.
The script will create and start a `virtualenv` in which the dependencies will be locally installed through `pip`, then it will start the `Flask` web application through `gunicorn`.

## Reaching Kontability in LAN through a web browser
You need to find the `LOCAL IP` address of the machine on which Kontability is running.
For Ubuntu server you can show it running `hostname -I`.

After that you should reach the web app from your other devices at `LOCAL-IP:5000`, for example `192.168.1.50:5000`.
Be sure to be connected a the same local network.

## Coudn't reach the web app in my local network
An issue could come up when your hosting machine is not listening http traffic at port `5000`.

This could be resolved running `sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT`.
This solution is not permanent after reboot.
