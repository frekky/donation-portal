"use strict";

var fs = require("fs");
var http = require("http");
var net = require("net");

module.exports = {
    HttpSocketServer: HttpSocketServer,
    createServer: createServer,
    proxy: proxy
};

/**
 * A thin wrapper around http.Server with a modified .listen() method that
 * will perservere on an EADDRINUSE error, and attempt to clean up any
 * abandoned sockets that are encountered, before attempting to .listen()
 * again. If such a socket is encountered and is not abandoned, but is
 * instead being used, then .listen() will not try to delete it.
 *
 * @param {function} requestListener - see documentation for http.Server
 * @return {HttpSocketServer}
 */
function HttpSocketServer(requestListener){
    if(!this instanceof HttpSocketServer) return new HttpSocketServer;
    http.Server.call(this, requestListener);
}
HttpSocketServer.prototype = Object.create(http.Server.prototype);

/**
 * Identical to http.Server.prototype.listen (the IPC/socket variant), except
 * that it will delete path if it is an abandoned socket, and then reattempt
 * to listen.
 *
 * @param {string} path - the path to place the socket file
 * @param {number} backlog - see http.Server.listen documentation
 * @param {function} callback - see http.Server.listen documentation
 * @return this {HttpSocketServer}
 */
HttpSocketServer.prototype.listen = function listen(path, backlog, callback){
    var _this = this;

    // If the socket already exists, see if it is being used, and if it isn't,
    // delete it and retry listening. If it is being used, then give up and
    // wait for the next manual invocation of .listen
    this.once("error", function(e){
        if(e.code == "EADDRINUSE"){
            var connTest = new net.Socket();
            
            // Socket was abandoned, delete it then retry .listen
            connTest.on("error", function(e){
                connTest.destroy();
                
                console.warn("Deleting abandoned socket \""+path+"\"");
                fs.unlinkSync(path);
                
                HttpSocketServer.prototype.listen.call(
                    _this, path, backlog, callback
                );
            });
            
            // Socket in use, give up
            connTest.on("connect", function(){
                connTest.destroy();
                e.message =
                    "Could not start server. Socket \""+path
                    +"\" exists and is in use"
                ;
                _this.emit("error", e);
            });
            connTest.connect(path);
        }
        else this.emit("error", e);
    });

    return http.Server.prototype.listen.call(this, path, backlog, callback);
}

/**
 * A shortcut for new HttpSocketSerer to mirror NodeJS's http API
 *
 * @param {function} requestListener - see http.createServer documentation
 * @return {HttpSocketServer}
 */
function createServer(requestListener){
    return new HttpSocketServer(requestListener);
}


/**
 * Creates a new middleware for express that proxies all HTTP requests to the
 * specified UNIX domain socket.
 *
 * @param {string} socketPath - the path to the socket
 * @return {function} - an express middleware function
 */
function proxy(socketPath){
    return function socketProxyMiddleware(req, res, next){
        fs.stat(socketPath, function(err, stats){
            // Check that we can actually open the socket,
            // and that it's a socket
            try {
                if(err) throw err;
                if(!stats.isSocket()) throw new Error("Not a socket");
            }
            catch(e){
                res.status(500).end();
                console.error(
                    "Error proxying to socket \"" + socketPath + "\": "
                    + e.message
                );
                return;
            }

            // Initiate HTTP request to proxy target
            var reqOpts = {
                socketPath: socketPath,
                method: req.method,
                path: req.path,
                headers: req.headers
            };
            var target = http.request(reqOpts, function onResponse(targetRes){
                res.writeHead(targetRes.statusCode, targetRes.headers);
                targetRes.pipe(res);
                // .pipe() will automatically call res.end()
            });
            req.pipe(target);
        });
    };
}
