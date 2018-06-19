"use strict";

var cproc = require("child_process");

// TODO: JSDoc
module.exports = function sudo(command, args, options, callback){
    const REGEX_USER = /^[a-zA-Z0-9_]+$/;
    const REGEX_GROUP = REGEX_USER;
    const REGEX_PASS = /^[^\x00-\x1f\x7f]+$/;
    
    var argv = [];

    try {
        // Process and validate arguments, building an array of args for
        // the underlying exec call
        if(!command || typeof command != "string")
            throw new Error("command must be a non-empty string");    
        
        // Validate any additional options
        if(options && typeof options == "object"){
            if(options.username){
                if(
                    typeof options.username != "string"
                    || !options.username.match(REGEX_USER)
                )
                    throw new Error(
                        "username must be a string with only letters, "
                        + "numbers, and underscores"
                    );
                else argv.push("-u", options.username);
            }
            // TODO: Add test cases for this
            if(options.password){
                if(
                    typeof options.password != "string"
                    || !options.password.match(REGEX_PASS)
                )
                    throw new Error(
                        "password must only contain printable characters"
                    );
            }
            if(options.group){
                if(
                    typeof options.group != "string"
                    || !options.group.match(REGEX_GROUP)
                )
                    throw new Error(
                        "group must be a string with only letters, "
                        + "numbers, and underscores"
                    );
                else argv.push("-g", options.group);
            }
            if(options.timeout); // here for readability
        }

        // Add -k to avoid credential caching, -S to accept password from
        // stdin, and -- to prevent args from injecting arguments that affect
        // the behaviour of sudo. Finally, add command to the list of arguments
        // for sudo
        argv.push("-kS", "--");
        argv.push(command);

        // If args was specified, append these one by one to argv for sudo,
        // casting each to a string, and checking for null character abuse 
        if(args && args.length > 0){
            for(var i = 0; i < args.length; i++){
                var arg = ""+args[i];
                if(arg.indexOf("\0") >= 0)
                    throw new Error("args must not contain null characters");
                argv.push(arg);
            }
        }
        console.dir(argv);

        // Call sudo, and write password (if any) to its stdin, then return
        // the resulting ChildProcess
        var execOpts = {
            timeout: (options.timeout>0 ? options.timeout : 0),
            killSignal: (options.timeout>0 ? "SIGKILL" : "SIGTERM")
        };
        var childProc = cproc.execFile("sudo", argv, execOpts, callback);
        childProc.stdin.end((options.password ? options.password : "") + "\n");
        return childProc;
    }
    catch(e){
        if(typeof callback == "function") callback(e);
    }
}
