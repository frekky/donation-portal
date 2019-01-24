uccportal - the UCC Computer Controlled Proletarian Organisational Roster That Accesses LDAP
============================================================================================

This is designed to be the ultimate membership management suite for UCC. Signups are electronic and automatic, data is able to be conveniently stored in the member database and some of it is even automatically validated.

Features
--------

- Written in Python 3 using [Django](https://www.djangoproject.com/)
- Rolling membership database, retaining data from year to year
- Registration form for new members to sign themselves up
- Connects to Active Directory to authenticate existing users & allow them to renew their own membership
- Administrative interface to approve pending memberships

Stuff to do
-----------

- Online payment of membership fees using [Square Payments](https://squareup.com/au/)
- Email confirmation & payment receipts
- Automatic member account creation in Active Directory (after membership approved)
- Validating student numbers in ID field (also via email)
- Add dispense account balance with Square online payments

Workflow Design
---------------

- __Use case 1: new member__:
    1. New member enters details on registration form, submits
        - Gets confirmation email to the effect of "your membership is pending"
    2. Door member logs in and verifies that details are correct, manages payment
        - Cash: door member takes cash and enters amount paid by cash
        - Card (in person): door member enters amount to charge, processed via Square App or custom POS app (Android)
        - Card (online): door member enters amount to charge, can either enter card details directly or new member can access payment form
        - Dispense note: all payments (even before account creation) processed through dispense, money is then given to newly created accounts following step 3
    3. Door member approves pending membership
        - Pending memberships are saved into the main members table
        - Account is created in AD/dispense using provided details
        - Update dispense with payment information after account creation - transfer money from `uccportal` account to `$newuser` account (for example)
        - User gets email with link to login & change details
    4. New member gets notification (ie. email), clicks link to set password
- __Use case 2: existing member__ (possibly with locked account):
    1. Existing member (with existing AD/LDAP account) logs in and enters details on renewal/registration form (or confirms existing stored details are correct)
        - Pending membership record created
    2. Door member logs in to approve membership, selects payment method as per above
    3. Door member approves pending membership renewal
        - Pending membership record transferred to main members table
    4. Renewing member gets email confirming payment / renewal success
        - confirmation link to reactivate account? should this happen between steps 1-2?

Environment Setup <a name="envsetup"></a>
-----------------

- This project uses Python 3.7
- Install `python-virtualenv`
- `git clone https://gitlab.ucc.asn.au/frekk/uccportal uccportal`
- `cd uccportal`
- `virtualenv env`
- Every time you want to do some uccportal development, do `source env/bin/activate` to set up your environment
- Install packages needed by pip to build python dependencies: `apt-get install build-essential libldap2-dev libsasl2-dev`
- Install python dependencies to local environment: `pip install -r pip-packages.txt`
- Configure django: `cp gms/gms/settings_local.example.py gms/gms/settings_local.py`
    - Edit `gms/gms/settings_local.py` and check that the database backend is configured correctly. (sqlite3 is fine for development)
- Initialise the database: `gms/manage.py makemigrations && gms/manage.py migrate`
    - Make sure you run this again if you make any changes to `gms/memberdb/models.py` to keep the DB schema in sync.
- Run the local development server with `gms/manage.py runserver`

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
    WSGIScriptAlias / /services/uccportal/gms/gms/wsgi.py

    <Directory /services/uccportal/gms/gms>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    Protocols h2 http:/1.1

    <Directory /services/uccportal/gms/static>
        Require all granted
    </Directory>

    Alias /media /services/uccportal/gms/static

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
    - `chmod 640 /services/uccportal/gms/gms/settings_local.py`
    - `chgrp -R www-data /services/uccportal/`
    - `mkdir /var/log/apache2/uccportal && chgrp www-data /var/log/apache2/uccportal && chmod 775 /var/log/apache2/uccportal && chmod o+x /var/log/apache2`
    - Put the static files in the correct location for apache2 to find them:
        - `gms/manage.py collectstatic`


Configuring the database backend
--------------------------------

To set up a the database,

(as root on mussel)
```
mussel:~# su - postgres
postgres@mussel:~$ psql
postgres=# create database uccportal;
postgres=# CREATE USER uccportal WITH ENCRYPTED PASSWORD 'insert-password-here';
postgres=# GRANT ALL on DATABASE uccportal to uccportal;
```

Adjust `/services/uccportal/gms/gms/settings_local.py` to point to the new database (usually
changing the databse name is enough).


Making changes to data being collected
--------------------------------------

Edit `/service/uccportal/gms/memberdb/models.py`
In `/services/uccportal/gms`, run `./manage.py makemigrations` to prepare the databae
updates.

```
uccportal:~# cd /services/uccportal/gms/
uccportal:/services/uccportal/gms# ./manage.py check
System check identified no issues (0 silenced).
uccportal:/services/uccportal/gms# ./manage.py migrate --run-syncdb

...
You just installed Django's auth system, which means you don't have any
 superusers defined.
Would you like to create one now? (yes/no): no

Now restart MemberDB by runing
uccportal:/services/uccportal/gms# touch gms/wsgi.py
```

Now go ahead and log in to the website. It will be totally fresh, with all
committee, door and wheel members being made superusers on first login.

If you would like to allow other users to help out with data entry,
ask them to log in. After the login attempt is denied, you will be able to
find their name in the Auth/Users area of the site. Turn on their staff status
and allow them access to the memberdb permissions.

A CSV download function has been added - select the members you want to
download in the administration interface, then choose Download as CSV file
from the Actions menu.

Credits
-------
- Adapted from `Gumby Management System` written by David Adam <zanchey@ucc.gu.uwa.edu.au>
- Derived from MemberDB by Danni Madeley
