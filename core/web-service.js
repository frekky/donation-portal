"use strict";

var express = require("express");
var http = require("http");
var fs = require("fs");
var config = require("common/config");
var hsocks = require("common/http-sockets");

function main(){
    var app;

    // Set up express app and routes
    app = express();
    app.use("/api/login", hsocks.proxy(config.varPath + "/login-service.sock"));
    app.get("/", function(req, res){res.redirect("/login.html");});
    app.use("/", express.static("static/"));

    // Start web server or crash
    console.info(
        "Starting web-service on host \"" + config.host
        + "\" and port " + config.port
    );
    try {app.listen(config.port, config.host);}
    catch(e){
        throw new Error("Failed to start web-service: " + e.message);
    }
}
main();
