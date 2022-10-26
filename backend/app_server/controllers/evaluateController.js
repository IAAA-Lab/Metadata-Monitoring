const { Results_mqa_sparql } = require('./schema')

const PythonShell = require('python-shell').PythonShell;
const myPython = './app_server/pythonPrograms/my-environment/bin/python3'

//incoming parameters are: mqa, iso19157, sparql, ckan, nti, dcatAp, direct, local, url, days
const evaluate = function (req, res) {
    let evaluationStarted = false
    if (req.query.mqa === 'true') {
        evaluationStarted = mqa_sparql(req.query.url);
    }
    if (req.query.iso19157 === 'true') {
        evaluationStarted = iso19157(req.query.url)
    }
    if (evaluationStarted) {
        res.json({evaluationStarted: evaluationStarted});
    } else {
        res.json({evaluationStarted: evaluationStarted});
    }
}

const mqa_sparql = function (url) {
    const options = {
        pythonPath: myPython,
        args: [url]
    };

    // PythonShell.run('./app_server/pythonPrograms/mqa_sparql/run.py', options, function (err, output) {
    //     if (err) {
    //         console.log(err)
    //         return false
    //     }
    //
    //     let properties = []
    //     //component 1 and output.length-2 is ignored because the last message is not usefull
    //     for(let i=1; i<output.length-2; i++) {
    //         let property = output[i].split(',')
    //         let property_item = {
    //             Dimension: property[0],
    //             Indicator_property: property[1],
    //             Count: property[2],
    //             Population: property[3],
    //             Percentage: property[4],
    //             Points: property[5]
    //         }
    //         properties.push(property_item)
    //     }
    //     let result = {
    //         Date: new Date(),
    //         properties: properties
    //     }
    //     Results_mqa_sparql.create(result)
    //     console.log('guardado')
    // });
    return true
};

const iso19157 = function (url) {
    const options = {
        pythonPath: myPython,
        args: [url]
    };

    console.log('empieza')
    PythonShell.run('./app_server/pythonPrograms/iso19157/run.py', options, function (err, output) {
        if (err) {
            console.log(err)
            return false
        }

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
        console.log(result)
        // Results_mqa_sparql.create(result)
        console.log('guardado')
    });
    return true
};

module.exports = {
    evaluate
};