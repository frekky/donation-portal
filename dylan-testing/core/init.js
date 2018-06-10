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

function initConfig(configPath){
    var rawConfig, config;

    // Try to open config file
    try {rawConfig = fs.readFileSync(configPath);}
    catch(e){
        throw new Error(
            "Could not open config file \"" + configPath + "\": " + e.message
        );
    }
    
    // Try to parse config file as JSON
    try {config = JSON.parse(rawConfig);}
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

        // serviceUser: verify that a user and group of this name exist,
        // then set serviceUid and serviceGid for later lookup
        var ids = getUserIds(config.serviceUser);
        config.serviceUid = ids.uid;
        config.serviceGid = ids.gid;

    }
    catch(e){
        throw new Error(
            "Error while validating \"" + configPath + "\": " + e.message
        );
    }

    return config;
}

module.exports = function main(){
	try {
        // Verify that we're currently running as root
        if(process.getuid() != 0){
            throw new Error(
                "UCCPortal must be run as root to function correctly.\n"
                + "If you're worried about security, privileges will be dropped "
                + "to that of the serviceUser listed in config.json, once "
                + "initialisation is complete. An exception to this is "
                + "auth-service.js, which requires it for PAM to function "
                + "correctly."
            );
        }
        
        // Attempt to load config.json, or fail
        var config = initConfig("config.json");
        console.dir(config);
        
        // Launch services
        var nodejs = process.argv[0];
        var spawnOpts = {
            stdio:"inherit", uid:config.serviceUid, gid:config.serviceGid
        };
        var rootSpawnOpts = {stdio:"inherit", gid:config.serviceGid};
        cproc.spawn(nodejs, ["core/pam-service.js"], rootSpawnOpts);
        cproc.spawn(nodejs, ["core/proxy-service.js"], spawnOpts);
        cproc.spawn(nodejs, ["core/login-service.js"], spawnOpts);

        // Drop privileges
        process.setgid(config.serviceGid);
        process.setuid(config.serviceUid);
    }
    catch(e){
        //console.error("Fatal Error: " + e.message);
        throw e;
        process.exitCode = 1;
    }
}
