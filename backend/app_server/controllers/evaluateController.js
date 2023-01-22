const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')
const { createWriteStream, createReadStream, unlinkSync } = require('fs')
const https = require('https');
const { createModel } = require('mongoose-gridfs');
const path = require('path');
const fs = require('fs')
const dateFormat = require('date-and-time')
const {connectionDB, url_fuseki, url_agenda} = require('../config/db.config');
const {Agenda} = require('agenda');
const request = require('request');

const PythonShell = require('python-shell').PythonShell;
const myPython = './app_server/pythonPrograms/my-environment/bin/python3'

function uploadFuseki(outputPath, dataset, isMQA, isISO19157, interval, count) {
    let fileName = 'catalog' + count + '.rdf'
    if(fs.existsSync(outputPath + '/' + fileName)) {
        let options = {
            'method': 'POST',
            'url': url_fuseki + dataset,
            'headers': {},
            formData: {
                'data': {
                    'value': createReadStream(outputPath + '/' + fileName),
                    'options': {
                        'filename': fileName,
                        'contentType': null
                    }
                }
            }
        };

        //Uploads the file to fuseki
        request(options, function (error, response) {
            if (error) throw new Error(error);

            unlinkSync(outputPath + '/' + fileName)
            console.log('upload of ' + outputPath + '/' + fileName + ' to fuseki completed')
            uploadFuseki(outputPath, dataset, isMQA, isISO19157, interval, count + 1)
        });
    } else {
        if (isMQA) {
            prepare_mqa_sparql(url_fuseki + dataset, interval)
        }
        if (isISO19157) {
            prepare_ISO19157_sparql(url_fuseki + dataset, interval)
        }
    }
    return true
}

//Ejecutar el harvester correspondiente y al acabar uploadFuseki del fichero creado
function harvester(url, dataset, isMQA, isISO19157, interval, isSPARQL, isCKAN) {
    //replace : . or / by _ for the output folder
    let folderName = url.replace(/[:.\/]/g, '_')
    const outputPath = path.resolve('./app_server/pythonPrograms/harvester/output/' + folderName)

    let scriptPath = ''
    if (isSPARQL) {
        scriptPath = './app_server/pythonPrograms/harvester/SPARQL_harvester.py'
    } else if (isCKAN) {
        scriptPath = './app_server/pythonPrograms/harvester/CKAN_harvester.py'
    }

    const options = {
        pythonPath: myPython,
        args: [url]
    };

    PythonShell.run(scriptPath, options, function (err, output) {
        if (err) {
            console.log('Execution of harvester failed')
            console.log(err)
            return false
        }
        console.log('Execution of harvester for url: ' + url + ' finished.')
        uploadFuseki(outputPath, dataset, isMQA, isISO19157, interval, 1)
    });
    return true
}

//incoming parameters are: mqa, iso19157, sparql, ckan, direct, local, days, url
const evaluate = function (req, res) {
    let evaluationStarted = false
    let url = req.query.url
    let interval = Number(req.query.days)
    let isMQA = req.query.mqa === 'true'
    let isISO19157 = req.query.iso19157 === 'true'
    let isLocal = req.query.local === 'true'
    let isSPARQL = req.query.sparql === 'true'
    let isCKAN = req.query.ckan === 'true'

    if (isLocal) {
        let dataset = req.query.dataset
        evaluationStarted = harvester(url, dataset, isMQA, isISO19157, interval, isSPARQL, isCKAN);
    } else {
        if (isMQA) {
            evaluationStarted = prepare_mqa_sparql(url, interval)
        }
        if (isISO19157) {
            evaluationStarted = prepare_ISO19157_sparql(url, interval)
        }
    }

    res.json({evaluationStarted: evaluationStarted});
}

const prepare_mqa_sparql = function (url, interval) {
    let actualDate = new Date()
    let jobID = url.replace(/\//g, '-')
        + ' - ' + ' MQA - '
        + actualDate.toISOString()
            .replace(/T/, ' ')
            .replace(/\..+/, '');

    let evaluationStarted;
    if (interval > 0) {
        evaluationStarted = schedule_task(url, jobID, interval, true, false)
    } else {
        evaluationStarted = evaluate_mqa_sparql(url);
    }
    return evaluationStarted;
};

const prepare_ISO19157_sparql = function (url, interval) {
    let actualDate = new Date()
    let jobID = url.replace(/\//g, '-')
        + ' - ' + ' ISO19157 - '
        + actualDate.toISOString()
            .replace(/T/, ' ')
            .replace(/\..+/, '');

    let evaluationStarted;
    if (interval > 0) {
        evaluationStarted = schedule_task(url, jobID, interval, false, true);
    } else {
        evaluationStarted = evaluate_iso19157(url)
    }
    return evaluationStarted;
}

const evaluate_mqa_sparql = function (url) {
    let actualDate = new Date()
    let date = dateFormat.format(actualDate, 'YYYY-DD-MM')
    let dateToFileName = actualDate.toISOString()
        .replace(/T/, ' ')
        .replace(/\..+/, '')

    let fileName = url.replace(/\//g, '-')
        + ' - ' + 'MQA - '
        + dateToFileName
        + '.ttl';

    const options = {
        pythonPath: myPython,
        args: [url, fileName, date]
    };

    console.log('Starting evaluation MQA of: ' + url)
    PythonShell.run('./app_server/pythonPrograms/mqa_sparql/run.py', options, function (err, output) {
        if (err) {
            console.log('Evaluation of MQA ' + url + ' failed')
            console.log(err)
            return false
        }

        let properties = []
        //component 1 and output.length-2 is ignored because the last message is not usefull
        for(let i=2; i<output.length-2; i++) {
            let property = output[i].split(';')
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
            URL: url,
            Date: dateToFileName,
            properties: properties
        }
        Results_mqa_sparql.create(result)
        console.log('Evaluation MQA of ' + url + ' saved')
        storeFile(fileName)

    });
    return true
};

const evaluate_iso19157 = function (url) {
    let actualDate = new Date()
    let date = dateFormat.format(actualDate, 'YYYY-DD-MM')
    let dateToFileName = actualDate.toISOString()
        .replace(/T/, ' ')
        .replace(/\..+/, '')

    let fileName = url.replace(/\//g, '-')
        + ' - ' + 'ISO19157 - '
        + dateToFileName
        + '.ttl';

    const options = {
        pythonPath: myPython,
        args: [url, fileName, date]
    };

    console.log('Starting evaluation ISO19157 of: ' + url)
    PythonShell.run('./app_server/pythonPrograms/iso19157/run.py', options, function (err, output) {
        if (err) {
            console.log('Evaluation of ISO19157' + url + ' failed')
            console.log(err)
            return false
        }

        let properties = []
        //component 2 and output.length-2 is ignored because the last message is not usefull
        for(let i=2; i<output.length-2; i++) {
            let property = output[i].split(';')
            let property_item = {
                Dimension: property[0],
                Entity: property[1],
                Property: property[2],
                Count: property[3],
                Population: property[4],
                Percentage: property[5],
                Pass: property[6] === 'True'
            }
            properties.push(property_item)
        }
        let result = {
            URL: url,
            Date: dateToFileName,
            properties: properties
        }

        Results_ISO19157.create(result)
        console.log('Evaluation ISO19157 of ' + url + ' saved')
        storeFile(fileName)
    });

    return true
};

function schedule_task(url, jobID, interval, isMQA, isISO19157) {
    const agenda = new Agenda({db: {address: url_agenda}});

    if (isMQA) {
        agenda.define(jobID, function (job) {
            evaluate_mqa_sparql(url)
        });
    } else if (isISO19157) {
        agenda.define(jobID, function(job) {
            evaluate_iso19157(url)
        });
    }

    agenda.on('ready', function() {
        agenda.every(interval + ' days', jobID);
        agenda.enable();
        agenda.start();
    });
    console.log('Stored job: ' + jobID + ' every ' + interval + ' days')

    //Return only for consistency with no scheduled evaluations
    return true;
}

const storeFile = function (name) {
    // use default bucket
    const Attachment = createModel();

    // write file to gridfs
    const realPath = path.resolve('./app_server/pythonPrograms/DQV_files/' + name)
    const readStream = createReadStream(realPath);
    const options = ({ filename: name, contentType: 'text/plain' });
    Attachment.write(options, readStream, (error, file) => {
        //Deletes the stored file only if its really stored
        unlinkSync(realPath)
        console.log('Successfully stored DQV file to database: ' + name)
    });

};

module.exports = {
    evaluate
};