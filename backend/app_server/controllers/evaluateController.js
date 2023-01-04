const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')
const { createWriteStream, createReadStream, unlinkSync } = require('fs')
const https = require('https');
const { createModel } = require('mongoose-gridfs');
const path = require('path');
const dateFormat = require('date-and-time')
const {connectionDB, url_fuseki, url_agenda} = require('../config/db.config');
const {Agenda} = require('agenda');
const request = require('request');

const PythonShell = require('python-shell').PythonShell;
const myPython = './app_server/pythonPrograms/my-environment/bin/python3'

function uploadFuseki(filePath, fileName, dataset, isMQA, isISO19157, interval) {
    let options = {
        'method': 'POST',
        'url': url_fuseki + dataset,
        'headers': {
        },
        formData: {
            'data': {
                'value': createReadStream(filePath),
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
        console.log('upload to fuseki completed')
        if (isMQA === 'true') {
            evaluate_mqa_sparql(url_fuseki + dataset, interval)
        }
        if (isISO19157 === 'true') {
            evaluate_ISO19157_sparql(url_fuseki + dataset, interval)
        }
    });
    return true
}

function downloadRDF(url, dataset, isMQA, isISO19157, interval) {
    let fileName = url.replace(/\//g, '-')
    const realPath = path.resolve('./app_server/downloadedFiles/' + fileName)

    https.get(url,(res) => {
        // file will be stored at this path
        const filePath = createWriteStream(realPath);
        res.pipe(filePath);
        filePath.on('finish',() => {
            filePath.close();
            console.log('Download completed from: ' + url);
            uploadFuseki(realPath, fileName, dataset, isMQA, isISO19157, interval)
        })
    })
    return true
}

//incoming parameters are: mqa, iso19157, sparql, ckan, nti, dcatAp, direct, local, days, url
const evaluate = function (req, res) {
    let evaluationStarted = false
    let url = req.query.url
    let interval = Number(req.query.days)
    let isMQA = req.query.mqa
    let isISO19157 = req.query.iso19157

    if (req.query.local === 'true') {
        // let dataset = req.query.dataset
        let dataset = 'prueba'
        evaluationStarted = downloadRDF(url, dataset, isMQA, isISO19157, interval);
    } else {
        if (isMQA === 'true') {
            evaluationStarted = evaluate_mqa_sparql(url, interval)
        }
        if (isISO19157 === 'true') {
            evaluationStarted = evaluate_ISO19157_sparql(url, interval)
        }
    }

    res.json({evaluationStarted: evaluationStarted});
}

const evaluate_mqa_sparql = function (url, interval) {
    let actualDate = new Date()
    let jobID = url.replace(/\//g, '-')
        + ' - ' + ' MQA - '
        + actualDate.toISOString()
            .replace(/T/, ' ')
            .replace(/\..+/, '');

    let evaluationStarted = mqa_sparql(url);
    if (interval > 0) {
        schedule_task(url, jobID, interval, true, false)
    }
    return evaluationStarted
};

const evaluate_ISO19157_sparql = function (url, interval) {
    let actualDate = new Date()
    let jobID = url.replace(/\//g, '-')
        + ' - ' + ' ISO19157 - '
        + actualDate.toISOString()
            .replace(/T/, ' ')
            .replace(/\..+/, '');

    let evaluationStarted = iso19157(url)
    if (interval> 0) {
        schedule_task(url, jobID, interval, false, true)
    }
    return evaluationStarted
}

const mqa_sparql = function (url) {
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

const iso19157 = function (url) {
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
            mqa_sparql(url)
        });
    } else if (isISO19157) {
        agenda.define(jobID, function(job) {
            iso19157(url)
        });
    }

    agenda.on('ready', function() {
        agenda.every(interval + ' days', jobID);
        agenda.enable();
        agenda.start();
    });
    console.log('Stored job: ' + jobID + ' every ' + interval + ' days')
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
        // unlinkSync(realPath)
        console.log('Successfully stored DQV file to database: ' + name)
    });

};

module.exports = {
    evaluate
};