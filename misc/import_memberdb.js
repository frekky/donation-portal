#!/usr/bin/env node

/* script to import users from memberdb format (MySQL) to mongoose for testing */

const pg = require('pg');
var mongoose = require('mongoose');
var conf = require('./pg.json');
var Member = require('../models/memberSchema');

/* specify stuff via environment variables
  PGUSER=uccmemberdb PGHOST=localhost PGPASSWORD=[redacted] PGDATABASE=uccmemberdb_2018 PGPORT=5432 node misc/import_memberdb.js
*/
const pgclient = new pg.Client(conf);
pgclient.connect();

console.log("waiting for pgclient to connect");

mongoose.connect('mongodb://localhost/uccportal-dev'); 
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'db connection error:'));
db.once('open', function() {
  console.log("Connected to db");
  Member.remove({}, function (err) {
    console.log(err);
    pgclient.query('SELECT * FROM memberdb_member', processOldMembers);
  });
});

console.log("waiting for mongoose to open");

/** old memberdb schema from postgresql:
CREATE TABLE memberdb_member (
  id integer NOT NULL,
  real_name character varying(200) NOT NULL,
  username character varying(16) NOT NULL,
  membership_type integer NOT NULL, // 1: O-day, 2: student, 3: non-student
  guild_member boolean NOT NULL,
  phone_number character varying(14) NOT NULL,
  email_address character varying(200) NOT NULL,
  student_no character varying(20) NOT NULL,
  date_of_birth date,
  signed_up date DEFAULT '2018-02-23'::date NOT NULL
);
*/

function processOldMembers(err, res) {
  var newMembers = [];
  if (err) {
    console.log(err.stack);
  } else {
    console.log("Dumping " + res.rows.length + " rows...");
    for (var i = 0; i < res.rows.length; i++) {
      if (res.rows[i].username) {
        console.log("user: " + res.rows[i].username);
      } else {
        console.log("new user: " + res.rows[i].real_name);
      }
      newMembers.push(convertMember(res.rows[i]));
    }
    Member.insertMany(newMembers, function (err, docs) {
      console.log("Done.");
      pgclient.end();
      Member.find().exec(verifyMongoMembers);  
    });
  }
};

function convertMember(row) {
  var renewtype, is_student;
  switch (row.membership_type) {
    case 1: // O-Day
      is_student = true;
      renewtype = "oday";
      break;
    case 2: // Student
      is_student = true;
      renewtype = "student";
      break;
    case 3: // Non-student
      is_student = false;
      renewtype = "nonstudent";
      break;
  }

  return {
    firstname: row.real_name,
    lastname: "",
    is_student: is_student,
    is_guild: row.guild_member,
    id_number: row.student_no,
    email: row.email_address,
    phone: row.phone_number,
    birthdate: row.date_of_birth,
    signupdate: row.signed_up,
    renewals: [ { renewtype: renewtype, date: row.signed_up } ],
    tlas: [ "???" ]
  };
}

function verifyMongoMembers(err, res) {
  console.log(res[0]);
  console.log("Currently " + res.length + " members in mongodb.");
  db.close();
}