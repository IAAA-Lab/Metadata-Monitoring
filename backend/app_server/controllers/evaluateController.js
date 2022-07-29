const executePython = function (req, res) {
    const PythonShell = require('python-shell').PythonShell;

    const options = {
        pythonPath: "./app_server/pythonPrograms/my-environment/bin/python3",
        args: [req.query.url]
    };

    PythonShell.run('./app_server/pythonPrograms/mqa_sparql/run.py', options, function (err, results) {
        if (err)
            throw err;
        // Results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        res.send(results.toString())
    });


    // console.log("entrado: " + req.query.url)
    // const CronJob = require('cron').CronJob;
    // new CronJob('* * * * * *', function() {
    //     console.log("URL: " + req.query.url)
    // },
    //     null,
    //     true);
    // res.send("vale ya")
}

module.exports = {
    executePython
}