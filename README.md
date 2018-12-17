uccportal - the UCC Computer Controlled Proletarian Organisational Roster That Accesses LDAP
============================================================================================

TODO: This is designed to be the ultimate membership management suite for UCC. Signups are electronic and automatic, data is able to be conveniently stored in the member database and some of it is even automatically validated.

Stuff to do
-----------

- Important structural TODO:
    - Design database schema for rolling memberships
    - Build member-facing initial registration form
    - Build door-facing pending membership approval form
    - Build member-facing post-approval (or post-email-confirmation) registration form
    - Build member-facing renewal form
- Stuff to do after structural bits
    - Administrative user authentication via LDAP/AD
    - Automatic member account creation (after membership approved)

Eventual / Conceptual Workflow Design
-------------------------------------

- __Use case 1: new member__:
    1. New member enters details on registration form, submits
        - Gets confirmation email
    2. Door member logs in and verifies that details are correct, manages payment
        - Cash: door member takes cash and enters amount paid by cash
        - Card (in person): door member enters amount to charge, processed via Square App or custom POS app (Android)
        - Card (online): door member enters amount to charge, can either enter card details directly or new member can access payment form
        - Dispense note: all payments (even before account creation) processed through dispense, money is then given to newly created accounts following step 3
    3. Door member approves pending membership
        - Pending memberships are saved into the main members table
        - Account is created in AD/dispense using provided details
        - Update dispense with payment information after account creation - transfer money from `uccportal` account to `$newuser` account (for example)
    4. New member gets notification (ie. email), clicks link to set password
- __Use case 2: existing member__ (possibly with locked account):
    1. Existing member (with existing AD/LDAP account) logs in and enters details on renewal/registration form (or confirms existing stored details are correct)
        - Pending membership record created
    2. Door member logs in to approve membership, selects payment method as per above
    3. Door member approves pending membership renewal
        - Pending membership record transferred to main members table
    4. Renewing member gets email confirming payment / renewal success
        - confirmation link to reactivate account? should this happen between steps 1-2?

Environment Setup
-----------------

- Install `python-virtualenv`
- `git clone https://gitlab.ucc.asn.au/frekk/uccportal uccportal`
- `cd uccportal`
- `virtualenv env`
- Every time you want to do some uccportal development, do `source env/bin/activate` to set up your environment
- install python dependencies to local environment: `pip install -r pip-packages.txt`
- Run the local development server with `gms/manage.py runserver`

-----------------------------------------------------------

GMS - The Gumby Management System [DEPRECATED]
==============================================
Written by David Adam <zanchey@ucc.gu.uwa.edu.au>
Derived from MemberDB by Danni Madeley

> That's where this whole thing started! 
> - [FVP]

GETTING STARTED EACH YEAR
------------------------

To set up a new database,

(as root on mussel)

mussel:~# su - postgres
postgres@mussel:~$ psql
postgres=# create database uccmemberdb_20XX;
postgres=# GRANT ALL on DATABASE uccmemberdb_20XX to uccmemberdb;

Adjust /services/gms/gms/settings_local.py to point to the new database (usually
changing the databse name is enough).

If you want to make changes to the data you collect, now is the time to do it.

Edit /service/gms/memberdb/models.py
In /services/gms, run `python manage.py makemigrations` to prepare the databae
updates.

mussel:~# cd /services/gms/
mussel:/services/gms# python manage.py validate
0 errors found
mussel:/services/gms# python manage.py syncdb
...
You just installed Django's auth system, which means you don't have any
 superusers defined.
Would you like to create one now? (yes/no): no

Now restart MemberDB by runing
mussel:/services/gms# touch gms/wsgi.wsgi

Now go ahead and log in to the website. It will be totally fresh, with all
committee members being made superusers on first login.

If you would like to allow non-committee users to help out with data entry,
ask them to log in. After the login attempt is denied, you will be able to
find their name in the Auth/Users area of the site. Turn on their staff status
and allow them access to the memberdb permissions.

A CSV download function has been added - select the members you want to
download in the administration interface, then choose Download as CSV file
from the Actions menu.
