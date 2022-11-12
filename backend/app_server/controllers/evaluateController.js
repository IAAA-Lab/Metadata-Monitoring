const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')
const { createReadStream, unlinkSync } = require('fs')
const { createModel } = require('mongoose-gridfs');
const path = require('path');
const dateFormat = require('date-and-time')
const connectionDB = require('../config/db.config');
const {Agenda} = require('agenda');

const PythonShell = require('python-shell').PythonShell;
const myPython = './app_server/pythonPrograms/my-environment/bin/python3'




//incoming parameters are: mqa, iso19157, sparql, ckan, nti, dcatAp, direct, local, days, url
const evaluate = function (req, res) {
    let evaluationStarted = false
    let url = req.query.url
    let interval = Number(req.query.days)
    let actualDate = new Date()
    let date = dateFormat.format(actualDate, 'YYYY-DD-MM')

    if (req.query.mqa === 'true') {
        let fileName = url.replace(/\//g, '-')
            + ' - ' + ' MQA - '
            + actualDate.toISOString()
                .replace(/T/, ' ')
                .replace(/\..+/, '')
            + '.ttl'
        evaluationStarted = mqa_sparql(url, fileName, date);
        if (interval > 0) {
            schedule_task(url, fileName, interval)
        }
    }
    if (req.query.iso19157 === 'true') {
        let fileName = url.replace(/\//g, '-')
            + ' - ' + ' ISO19157 - '
            + actualDate.toISOString()
                .replace(/T/, ' ')
                .replace(/\..+/, '')
            + '.ttl'
        evaluationStarted = iso19157(url, fileName, date)
        if (interval> 0) {
            schedule_task(url, fileName, interval)
        }
    }

    res.json({evaluationStarted: evaluationStarted});
}

const mqa_sparql = function (url, fileName, date) {
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
            Date: date,
            properties: properties
        }
        Results_mqa_sparql.create(result)
        console.log('Evaluation MQA of ' + url + ' saved')
        storeFile(fileName)

    });
    return true
};

const iso19157 = function (url, fileName, date) {
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
            Date: date,
            properties: properties
        }

        Results_ISO19157.create(result)
        console.log('Evaluation ISO19157 of ' + url + ' saved')
        storeFile(fileName)
    });

    return true
};

function schedule_task(url, fileName, interval) {
    const agenda = new Agenda({db: {address: connectionDB.url_agenda}});
    agenda.define(fileName, function(job) {
        console.log("filename: " + fileName + " URL: " + url);
    });

    agenda.on('ready', function() {
        agenda.every(interval + ' days', fileName);
        agenda.enable();
        agenda.start();
    });

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
        console.log('Successfully stored DQV file to databe')
    });

};

module.exports = {
    evaluate
};