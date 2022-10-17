const { Results_mqa_sparql } = require('./schema')

const PythonShell = require('python-shell').PythonShell;
const myPython = './app_server/pythonPrograms/my-environment/bin/python3'

const mqa_sparql = function (req, res) {
    const options = {
        pythonPath: myPython,
        args: [req.query.url]
    };

    PythonShell.run('./app_server/pythonPrograms/mqa_sparql/run.py', options, function (err, output) {
        if (err)
            throw err;

        let properties = []
        //component 1 and output.length-2 is ignored because the last message is not usefull
        for(let i=1; i<output.length-2; i++) {
            let property = output[i].split(',')
            let property_item = {
                Dimension: property[0],
                Indicator_property: property[1],
                Count: property[2],
                Population: property[3],
                Percentage: property[4],
                Points: property[5]
            }
            properties.push(property_item)
        }
        let result = {
            Date: new Date(),
            properties: properties
        }
        Results_mqa_sparql.create(result)
        console.log("guardado")
    });

    res.send("vale ya")
}

const test_true = function (req, res) {
    res.send("dentro")
}

module.exports = {
    mqa_sparql,
    test_true
};