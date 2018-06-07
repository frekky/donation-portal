#!/usr/bin/env node

/* script to import users from memberdb format (MySQL) to mongoose for testing */

const pg = require('pg');
const mongoose = require('mongoose');
const conf = require('./pg.json');
const Member = require('../models/memberSchema');
const TLA = require('../models/tlaSchema');
const Fuse = require('fuse.js');
const tlaParser = require('./tlaParser');

/* DEPRECATED: specify stuff via environment variables
  PGUSER=uccmemberdb PGHOST=localhost PGPASSWORD=[redacted] PGDATABASE=uccmemberdb_2018 PGPORT=5432 node misc/import_memberdb.js
*/

const pgclient = new pg.Client(conf);
console.log("Connecting to memberdb...");

pgclient.connect(function (err) {
  if (err) {
    console.warn(err);
    console.warn("could not connect to memberdb!");
    process.exit(1);
  } else {
    console.log("memberdb connected OK");
  }
});

console.log("Connecting to mongodb...");
mongoose.connect('mongodb://localhost/uccportal-dev'); 
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'db connection error:'));
db.once('open', function() {
  console.log("Connected to mongodb.");
  TLA.remove({}, function (err) {
    if (err) {
      console.warn(err);
    }
    TLA.insertMany(tlas, function (err) {
      if (err) {
        console.warn(err);
        console.warn("could not update TLAs in database");
      }
    });
  });
  Member.remove({}, function (err) {
    if (err) {
      console.log(err);
      process.exit(1);
    }
    pgclient.query('SELECT * FROM memberdb_member', processOldMembers);
  });
});

const tlafile = process.argv[2];
var tlas = tlaParser.parse(tlafile);
tlaParser.print(tlas);
console.log('Finished parsing TLAs, got ' + tlas.length + ' different TLAs.');

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
); */
function processOldMembers(err, res) {
  var newMembers = [];
  if (err) {
    console.log(err.stack);
  } else {
    console.log("Dumping " + res.rows.length + " rows...");
    for (var i = 0; i < res.rows.length; i++) {
      if (res.rows[i].username) {
        // console.log("user: " + res.rows[i].username);
      } else {
        // console.log("new user: " + res.rows[i].real_name);
      }
      newMembers.push(convertMember(res.rows[i]));
    }
    Member.insertMany(newMembers, function (err, docs) {
      console.log("Done, found " + newMembers.length + " members.");
      pgclient.end();
      Member.find({}).exec(verifyMongoMembers);
      TLA.find({}).exec(function (err, res) {
        if (err) {
          console.warn(err);
        } else {
          console.log(res.length + " TLAs imported into DB.");
        }
      });
    });
  }
};

function matchTLAs(members) {
  // Fuse doesn't like to search across multiple fields so we have to combine firstname and lastname again to make it work.
  var fixedTLAs = [];
  for (var i = 0; i < tlas.length; i++) {
    fixedTLAs.push({
      name: tlas[i].firstname + " " + tlas[i].lastname,
      tla: tlas[i].tla,
    });
  }

  var options = {
    shouldSort: true,
    threshold: 0.3,
    location: 0,
    distance: 100,
    maxPatternLength: 50,
    minMatchCharLength: 1,
    keys: [
      "name"
    ]
  };
  var fuse = new Fuse(fixedTLAs, options); // "list" is the item array

  var saved = 0;
  var toSave = 0;

  function tryCloseDB() {
    saved += 0.5;
    if (saved == toSave) {
      // everything is saved, time to stop.
      db.close(function (err) {
        if (err) {
          console.warn(err);
          console.warn("could not close mongodb connection!");
        } else {
          console.log("closed mongodb connection.");
        }
      });
    }
  }

  // now loop through members and find their TLAs
  for (var mi = 0; mi < members.length; mi++) {
    var m = members[mi];

    var results = fuse.search(m.firstname + " " + m.lastname);
    // console.log("searching for tlas for " + m.firstname + " " + m.lastname);
    if (results.length > 0) {
      console.log(m.firstname + " has " + results.length + " tlas, using [" + results[0].tla + "]");
      // Some false positives: only use the first TLA.
      m.tlas = [results[0].tla];

      // Update Member to include TLAs we found
      toSave++;
      m.save(function (err) {
        // since the saving is done asynchronously, we need to close the db after everything has been saved.
        if (err) {
          console.warn("error saving TLA to member!");
          console.warn(err);
        }
        tryCloseDB();
      });

      // query and update TLA document so we can associate it with a member.
      TLA.findOneAndUpdate({tla: results[0].tla}, {_memberId: m._id}, function (err, doc) {
        if (err) {
          console.warn(err);
        }
        console.warn("Updated TLA [" + doc.tla + "] with member ID " + doc._memberId);
        tryCloseDB();
      });
    }
    if (results.length == 0) {
      // console.log(m.firstname + " has no TLA.");
    }
  }

  console.log(toSave + " TLAs assigned to members, total " + tlas.length + ", unclaimed " + (tlas.length - toSave));
}

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

  var m = {
    firstname: row.real_name,
    lastname: "",
    is_student: is_student,
    is_guild: row.guild_member,
    id_number: row.student_no,
    email: row.email_address,
    phone: row.phone_number,
    birthdate: row.date_of_birth,
    signupdate: row.signed_up,
    username: row.username,
    renewals: [ { renewtype: renewtype, date: row.signed_up } ],
    tlas: []
  };
  return m;
}

function verifyMongoMembers(err, res) {
  console.log("Currently " + res.length + " members in mongodb.");
  matchTLAs(res);
}