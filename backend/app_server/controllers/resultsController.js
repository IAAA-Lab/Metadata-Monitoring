const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')
const { createModel } = require('mongoose-gridfs');

//Return every 'URL - DATE - MQA/ISO19157' in the database
const resultsIndex = async function (req, res) {
    let indexes = []
    await Results_mqa_sparql.find({}).then(r => {
        for(let i=0; i<r.length; i++) {
            let property = {
                URL: r[i].URL,
                Date: r[i].Date,
                Method: 'MQA'
            }
            indexes.push(property)
        }
    })

    await Results_ISO19157.find({}).then(r => {
        for(let i=0; i<r.length; i++) {
            let property = {
                URL: r[i].URL,
                Date: r[i].Date,
                Method: 'ISO19157'
            }
            indexes.push(property)
        }
    })

    res.json(indexes)
}

const analysis = async function (req, res) {
    let method = req.query.method
    let date = req.query.date
    let url = req.query.url
    let analysis

    if (method === 'MQA') {
        analysis = await Results_mqa_sparql.findOne({URL: url, Date: date}, {_id: 0, URL: 0, Date: 0},
            function (err, r) {
            return r;
        }).clone().catch(function(err){ console.log(err)})

    } else if (method === 'ISO19157') {
        analysis = await Results_ISO19157.findOne({URL: url, Date: date}, {_id: 0, URL: 0, Date: 0},
        function (err, r) {
            return r;
        }).clone().catch(function(err){ console.log(err)})
    }
    res.json(analysis)
};

const exportData = function (req, res) {
    // use default bucket
    const Attachment = createModel();

    const fileName = req.query.filename
    Attachment.read({ filename: fileName }, (error, buffer) => {
        if (error) {
            res.status(404).send('file does not exists')
            return
        }
        res.setHeader('Content-Disposition','attachment; filename=' + fileName);
        res.send(buffer.toString())
    });
}



module.exports = {
    resultsIndex,
    exportData,
    analysis
};