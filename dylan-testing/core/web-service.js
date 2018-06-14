"use strict";

var express = require("express");
var http = require("http");
var fs = require("fs");
var config = require("common/config");
var httpSockets = require("common/http-sockets");

var config;
var app;

function main(){
    // Set up express app and routes
    app = express();
    app.use("/login", httpSockets.proxy(config.varPath + "/login-service.sock"));

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
