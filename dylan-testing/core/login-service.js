var express = require("express");
var http = require("http");
var fs = require("fs");

var httpSockets = require("common/http-sockets");
var config = require("common/config");
var app = express();
var server;

// Set up routes
app.get("/", function(req, res){
    res.write("Hello World!");
    res.end();
});

// Create server, start it, and make sure it gracefully shuts down
// when this service gets terminated
server = httpSockets.createServer(app);
server.listen(config.varPath + "/login-service.sock");
