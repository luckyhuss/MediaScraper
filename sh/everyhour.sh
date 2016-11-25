#!/bin/bash

# This program launches the following commands (every hour by cron)
# Author : Anwar Buchoo (luckyhuss@msn.com | http://ideaof.me)
# Date : 21/02/2016
# Date : 25/11/2016
# Version : 1.1
# chmod 755 everyhour.sh

#pyLoadCore -q && pyLoadCore --daemon

sudo rsync -av --progress --log-file=/media/shares/SEAGATE-II/RasperryPi/rsync_torrents.log /var/lib/transmission-daemon/info/torrents/ /media/shares/SEAGATE-II/RasperryPi/torrents/
