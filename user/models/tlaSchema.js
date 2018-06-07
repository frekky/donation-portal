const mongoose = require('mongoose');

var tlaSchema = mongoose.Schema({
  tla: String, // Three Letter Acronym
  firstname: String, // Name associated with TLA (even if a member, yes I know it's duplicated but TLAs are weird.)
  lastname: String,
  _memberId: mongoose.Schema.Types.ObjectId, // ID of corresponding member if found
});

module.exports = mongoose.model('TLA', tlaSchema);