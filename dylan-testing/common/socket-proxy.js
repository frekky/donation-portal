var fs = require("fs");

/**
 * Creates a new middleware for express that proxies all requests to the
 * specified UNIX domain socket.
 *
 * @param {string} socketPath - the path to the socket
 * @return {function} - an express middleware function
 */
module.exports = function socketProxy(socketPath){
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

