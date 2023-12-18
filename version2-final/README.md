# dcss
Data Collection Scheduling System

### Requirements

`apt-get install python3-pip` or equivalent in non-Debian distros

`pip3 install . --upgrade`

Have a REDIS installed and running.

Install Kafka Confluence

### Operations


Celery Beat is needed to schedule tasks

`/usr/local/bin/celery -A dcss.app beat --loglevel=debug`

Celery Worker is needed to execute tasks

`/usr/local/bin/celery -A dcss.app worker --loglevel=debug`

Proper daemon-ized operation is achieved via supervisord

`systemctl start supervisor`

Configurations are stored in conf.d
