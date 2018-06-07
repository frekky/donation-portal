var express = require('express');
var router = express.Router();
var Member = require('../models/memberSchema');

/* GET users listing. */
router.get('/', function(req, res, next) {
    Member.find({}).select('username -_id').exec(function (err, members) {
      var r = [];
      for (var i = 0; i < members.length; i++) {
        if (members[i].username) {
          r.push(members[i].username);
        }
      }
      res.json(r);
    });
});

router.get('/:username', function(req, res, next) {
  Member.find({username: req.params.username}).select('-_id').exec(function (err, d) {
    res.json(d);
  });
});

router.get('/:username/tlas', function (req, res, next) {
  Member.find({username: req.params.username}).select('tlas -_id').exec(function (err, d) {
    res.json(d);
  })
});

module.exports = router;
