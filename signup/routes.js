"use strict"

/* This file constructs the workflow for signups using the web API
  - Entirely new signups (no existing username)
    0. Collect email address and send email to confirm containing token with temporary account info.
    1. Collect name, birthdate, student number/ID number.
       a. If student number provided, verify by student email or LDAP or something
       b. If student ID is valid, allow student prices
       c. If Guild member, allow Guild prices
    2. Process payment for account creation
    3. Collect username, password and snack machine PIN to create account in AD, dispense etc.
    4. Dispense appropriate membership
    5. Delete/revoke temporary session ID.
  - Renewal of membership (using a valid AD username and password)
    0. Verify existing account information, record changes if made.
       a. If student number provided, verify student & Guild membership status
    1. Process payment with appropriate amount
    2. Unlock account and dispense appropriate membership
*/

var crypto = require('crypto');
var express = require('express');
var router = express.Router();

router.use('/', express.static('./wwwroot', {
    index: 'index.html',
}));

// For entirely new members, does email confirmation etc to create an "uccportal" login (and memberdb entry minus payments)
router.get('/new', function (req, res, next) {
    res.send("GET");
});

// receive email address and produce session token
router.put('/new', function (req, res) {
    var token = crypto.randomBytes(64).toString('base64');


});

// 

// For logging in using an existing account, regardless of login status
router.get('/login', function (req, res, next) {

    res.send(req.cookies.session)
});

module.exports = router;