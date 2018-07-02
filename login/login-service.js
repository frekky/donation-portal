"use strict";

var http = require("http");
var fs = require("fs");
var cproc = require("child_process");
var qstring = require("querystring");
var express = require("express");

var hsocks = require("common/http-sockets");
var sudo = require("common/sudo");
var config = require("common/config");


// TODO: replace with sudo implementation
// This is a stub that will likely just be replaced with
// a call to the sudo function
function testCredentials(username, password, callback){ 
    // Validate input
    if(
        typeof username != "string" || !username
        || !username.match(/^[a-zA-Z0-9_]+$/)
        || typeof password != "string" || !password
        || typeof callback != "function"
    ) callback(false);
    
    // Try to run sudo
    // TODO: come up with a better way of verifying credentials
    callback(true);
}

function main(){
    var app = express();
    var server;

    // Set up routes
    app.get("/", function(req, res){res.redirect("/login.html");});
    app.post("/", function(req, res){ 
        req.once("readable", function(){
            var parsed = {};

            // Read in first chunk of req, try to parse it...
            try{parsed = qstring.parse(req.read().toString());}
            catch(e){
                res.status(400).end();
                return;
            }

            // Validate provided username/password (or lack thereof)
            testCredentials(parsed.username, parsed.password, function(valid){
                if(valid) res.status(200).end();
                else res.status(401).end();
            });
        });
    });

    // Create server and listening socket, ensuring only processess running
    // as config.user can access the socket
    var sockPath = config.varPath + "/login-service.sock";
    server = hsocks.createServer(app);
    process.umask(0o177); //u=rw,go=-
    server.listen(sockPath);
}
main();
