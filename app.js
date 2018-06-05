var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/users', usersRouter);

app.get("/user/:userid/", function (req, res) {
  res.send({test: 'data'});
});

app.get("/:str/blah/:name/:id", function (req, res) {
  res.send("Get request to " + req.url + " was received!");
  res.send(req.params);
});


module.exports = app;
