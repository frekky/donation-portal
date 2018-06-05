'use strict';
var mongoose = require('mongoose');

// Here we define the schema used by the model for gumby documents
var memberSchema = mongoose.Schema({
  firstname: String,
  lastname: String,
  is_student: Boolean,
  is_guild: Boolean,
  id_number: String,
  email: String,
  phone: String,
  birthdate: Date,
  username: String,
  tlas: [String],
  signupdate: Date,
  renewals: [{renewtype: String, date: Date}]
});

// And we export (return) a model based on the schema
module.exports = mongoose.model('Member', memberSchema);