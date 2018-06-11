var express = require("express");
var fs = require("fs");

var config;
var app;

function main(){
    // Read in config from environment
    config = JSON.parse(process.env.UCCPORTAL_CONFIG);
    
    app = express();
    app.get("/", function(req, res){
        res.write("Hello World!");
        res.end();
    });

    app.listen(config.varPath + "/login-service.sock");
}
main();
