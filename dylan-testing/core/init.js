"use strict";

var fs = require("fs");
var cproc = require("child_process");

function getUserIds(username){
    var ids = {uid:NaN, gid:NaN};

    try{
        ids.uid = Number.parseInt(cproc.execFileSync("id", ["-u",username]));
        ids.gid = Number.parseInt(cproc.execFileSync("id", ["-g",username]));
        if(ids.uid == NaN || ids.gid == NaN)
            throw new Error("The `id` command returned an invalid uid or gid");
    }
    catch(e){
        throw new Error(
            "Error looking up uid and gid of \"" + username + "\": "
            + e.message
        );
    }

    return ids;
}

function initConfig(configPath, shadowConfig){
    var rawConfig, config;

    // Try to open config file
    console.info("Loading config from \"" + configPath + "\"");
    try {rawConfig = fs.readFileSync(configPath);}
    catch(e){
        throw new Error(
            "Could not open config file \"" + configPath + "\": " + e.message
        );
    }
    
    // Try to parse config file as JSON
    try {
        // Make config inherit properties from shadowConfig, so it they're
        // undefined in the current config file, their defaults take precedence
        // from the default config file.
        config = Object.assign({}, shadowConfig, JSON.parse(rawConfig));
    }
    catch(e){
        throw new Error(
            "\"" + configPath + "\" is not in a valid JSON format: "
            + e.message
        );
    }

    // Verify options provided in config file
    try {
        // varPath: verify that it exists and is a directory
        try {fs.readdirSync(config.varPath);}
        catch(e){
            throw new Error(
                "varPath: the provided directory could not be opened: "
                + e.message
            );
        }

        // user: verify that a user and group of this name exist,
        // then set uid and gid for later lookup
        var ids = getUserIds(config.user);
        config.uid = ids.uid;
        config.gid = ids.gid;

        // host: verify that host is in a (somewhat) valid format
        // TODO: Improve this?
        if(typeof config.host != "string" || !config.host.match(
            /[a-z0-9:.-]+/i
        )) throw new Error("host: not a valid hostname nor IP address");

        // port: verify that a valid port was specified
        if(
            typeof config.port != "number"
            || config.port%1 > 0 || config.port < 0 || config.port > 65536
        ) throw new Error("port: invalid port number specified");
    }
    catch(e){
        throw new Error(
            "Error while validating \"" + configPath + "\": " + e.message
        );
    }

    // configPath: if the config file specifies a different path to a config
    // file, then try to load this instead.
    // Config files loaded later inherit from config files loaded earlier :)
    if(config.configPath){
        // Make sure that we don't keep re-loading the current config file
        // recursively and overflow the stack.
        configPath = config.configPath;
        delete config.configPath
        return initConfig(configPath, config);
    }

    return config;
}

module.exports = function main(){
	try {
        // Attempt to load config.json
        var config = initConfig("config.json");

        // Set up environment for child processes
        process.env.UCCPORTAL_CONFIG = JSON.stringify(config);
        process.env.NODE_PATH = 
            (process.env.NODE_PATH ? process.env.NODE_PATH + ":" : "")
            + process.cwd()
        ;

        // Launch services
        var nodejs = process.argv[0];
        var spawnOpts = {stdio: "inherit"};
        cproc.spawn(nodejs, ["core/web-service.js"], spawnOpts);
        cproc.spawn(nodejs, ["core/login-service.js"], spawnOpts);
    }
    catch(e){
        //console.error("Fatal Error: " + e.message);
        process.exitCode = 1;
        throw e;
    }
}
