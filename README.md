Online Donation Tracker
=======================

An online donation tracker system for the Cameron Hall Charity Vigil 2020, which is being run online this year #covid-19

Features
--------

- Donations can be made online using the [Square Payment Form](https://docs.connect.squareup.com/payments/sqpaymentform/sqpaymentform-overview)
- Written in Python 3 using [Django](https://www.djangoproject.com/)

Environment Setup <a name="envsetup"></a>
-----------------

- This project uses Python version >= 3.5
- Install packages `apt-get install python3-virtualenv python3-dev build-essential sqlite3`
- `git clone https://github.com/frekky/donation-portal`
- `cd uccportal`
- `virtualenv env`
- Every time you want to do some uccportal development, do `source env/bin/activate` to set up your environment
- Install python dependencies to local environment: `pip install -r pip-packages.txt`
- Configure django: `cp src/donations/settings_local.example.py src/donations/settings_local.py`
    - Edit `src/donations/settings_local.py` and check that the database backend is configured correctly. (sqlite3 is fine for development)
- Initialise the database: `src/manage.py makemigrations squarepay && src/manage.py migrate squarepay`
- Run the local development server with `src/manage.py runserver`

-----------------------------------------------------------

Deployment under Apache on Debian
---------------------------------

This works for Apache 2.4 or above using `mod_wsgi` compiled with Python 3 support.
If the apache version is too low or it already uses `mod_wsgi` for Python 2 then
you should probably give up on that installation and make a new one.

This also assumes you have configured HTTPS certificates already and that apache2
is configured to run as an unprivileged user (ie. `www-data`)

1. Install the packages:
    `apt-get install apache2 libapache2-mod-wsgi-py3 git build-essential libldap2-dev libsasl2-dev`
2. Checkout the git repository somewhere (ie. in `/services/uccportal`):
    `git clone https://gitlab.ucc.asn.au/frekky/uccportal /services/uccportal`
3. Put something like the following in `/etc/apache2/sites-available/uccportal.conf`:
```
<VirtualHost *:443>
    ServerAdmin wheel@ucc.gu.uwa.edu.au
    ServerName portal.ucc.gu.uwa.edu.au
    ServerAlias portal.ucc.guild.uwa.edu.au
    ServerAlias portal.ucc.asn.au

    DocumentRoot /services/uccportal/wwwroot

    <Directory /services/uccportal/wwwroot>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
    </Directory>

    WSGIDaemonProcess uccportal python-home=/services/uccportal/env python-path=/services/uccportal/gms
    WSGIProcessGroup uccportal
    WSGIScriptAlias / /services/uccportal/src/gms/wsgi.py

    <Directory /services/uccportal/src/gms>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    Protocols h2 http:/1.1

    <Directory /services/uccportal/media>
        Require all granted
    </Directory>

    Alias /media /services/uccportal/media

    SSLEngine On
    SSLCertificateFile /etc/letsencrypt/live/portal.ucc.asn.au/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/portal.ucc.asn.au/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/portal.ucc.asn.au/chain.pem

    ErrorLog ${APACHE_LOG_DIR}/uccportal/error.log
    CustomLog ${APACHE_LOG_DIR}/uccportal/access.log combined
</VirtualHost>
```
4. Configure django.
    - Follow the steps from [Environment Setup](#envsetup)
    - `chmod 640 /services/uccportal/src/gms/settings_local.py`
    - `chgrp -R www-data /services/uccportal/`
    - `mkdir /var/log/apache2/uccportal && chgrp www-data /var/log/apache2/uccportal && chmod 775 /var/log/apache2/uccportal && chmod o+x /var/log/apache2`
    - Put the static files in the correct location for apache2 to find them:
        - `src/manage.py collectstatic`

Credits
-------
- Hacked out of the remains of `uccportal` (https://gitlab.ucc.asn.au/ucc/uccportal)
- Adapted from `Gumby Management System` written by David Adam <zanchey@ucc.gu.uwa.edu.au>
- Derived from MemberDB by Danni Madeley
