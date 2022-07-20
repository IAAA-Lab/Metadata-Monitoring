const executePython = function (req, res) {
    const PythonShell = require('python-shell').PythonShell;

    const options = {
        pythonPath: "./app_server/pythonPrograms/my-environment/bin/python3",
        args: [req.query.firstname, req.query.lastname]
    };

    PythonShell.run('./app_server/pythonPrograms/mqa_sparql/run.py', options, function (err, results) {
        if (err)
            throw err;
        // Results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        res.send(results.toString())
    });
}

module.exports = {
    executePython
}