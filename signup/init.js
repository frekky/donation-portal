var mongoose = require('mongoose');
var express = require('express');
var signupRoutes = require('./routes');
var app = express();

console.log("Connecting to mongodb...");
mongoose.connect('mongodb://localhost/uccportal-dev'); 
var db = mongoose.connection;
db.on('error', console.error.bind(console, 'db connection error:'));
db.once('open', function() {
  console.log("Connected to mongodb.");
});

// Start web server or crash
console.info("Starting web-service on host \"" + config.host + "\" and port " + config.port);
try {
    app.listen(config.port, config.host);
} catch (e) {
    throw new Error("Failed to start web-service: " + e.message);
}

app.use('/', signupRoutes);