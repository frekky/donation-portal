var mongoose = require('mongoose');
var express = require('express');
var cookieParser = require('cookie-parser');
var signupRoutes = require('./routes');
var crypto = require('crypto');
var SessionStore = require('./express-sessions');
var app = express();


console.log("Connecting to mongodb...");
mongoose.connect('mongodb://localhost/uccportal-dev'); 
var db = mongoose.connection;
db.on('error', function (err) {
    console.error("Failed to connect to mongodb:", err);
    console.error("Maybe mongodb isn't started?");
    process.exit(1);
});
db.once('open', function() {
  console.log("Connected to mongodb.");
});

// Start web server or crash
console.info("Starting web-service on http://localhost:3000/");
try {
    app.listen(3000);
} catch (e) {
    console.error("Failed to start web service!");
    process.exit(1);
}

app.use(express.session({
    secret: crypto.randomBytes(32).toString('base64'), // make new secret for each session, this is to make things easier to debug.
    cookie: { maxAge: 2628000000 },
    store: new SessionStore({
        instance: mongoose,
        collection: 'Sessions',
        expire: 86400
    })
}));

app.use(cookieParser());
app.use('/', signupRoutes);
app.use('/', express.static(__dirname + 'wwwroot/'));