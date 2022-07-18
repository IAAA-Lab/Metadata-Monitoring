const ejecutarPython = function (req, res) {
    const PythonShell = require('python-shell').PythonShell;

    // E.g : localhost:3000/evaluate?firstname=primero&lastname=segundoo
    console.log("first: " + req.query.firstname)
    console.log("last: " + req.query.lastname)
    var options = {
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

    console.log("terminadoooo")
}

module.exports = {
    ejecutarPython
}