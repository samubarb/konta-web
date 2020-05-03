# Kontability Web App

Simple app to keep track of house bills payment.

## Usage

With `python3` and `pip3` installed run the `launch.sh` script in the main project folder.
The script will create and start a `virtualenv` in which the dependencies will be locally installed through `pip`, then it will start the `Flask` web application through `gunicorn` and the necessary file, such a secret key and a database.

## Reaching Kontability in LAN through a web browser

You need to find the `LOCAL-IP` address of the machine on which Kontability is running.
For Ubuntu server you can show it running `hostname -I`.

After that you should reach the web app from your other devices at `LOCAL-IP:5000`, for example `192.168.1.50:5000`.
Be sure to be connected a the same local network.

## Autorun at boot

In the main folder is included a user systemd service called `kontability.service`, it needs to be copied in the user systemd folder.

In order to make it work with your system you need to adjust the paths in `WorkingDirectory=` and `ExecStart=`. My default values are left as reference in the file.

After adjusting the paths, copy it in the default systemd's user folder:

```
`cp kontability.service ~/.config/systemd/user/`
```

If the path doesn't exist, create the nested folder structure as above.

Enable the service through:

```
systemctl --user enable kontability.service
```

Using *[lingering][lingering]* to permits user's systemd unit to run without requiring login:

```
# loginctl enable-linger <username>
```

Reboot and you should the webapp up and running.

## Troubleshooting

### Systemd fails at boot

Use `systemctl --user status kontability.service` to investigate the issue.

Remember also to apply further modifications in `kontability.service` through these steps:

```
systemctl --user daemon-reload
systemctl --user restart (or reload) kontability.service
```

### Coudn't reach the web app in my local network

An issue could come up when your hosting machine is not listening http traffic at port `5000`.

This could be resolved running `sudo iptables -I INPUT -p tcp --dport 5000 -j ACCEPT` on the machine running Kontability.
This solution is not permanent after reboot.

<!-- Links -->
[lingering]: https://wiki.archlinux.org/index.php/Systemd/User#Automatic_start-up_of_systemd_user_instances
