function getConfig(){
    var config;

    try {config = JSON.parse(process.env.UCCPORTAL_CONFIG);}
    catch(e){
        throw new Error(
            "Failed to retrieve config from UCCPORTAL_CONFIG "
            + "environment variable: " + e.message
        );
    }

    return config;
}

module.exports = getConfig();
