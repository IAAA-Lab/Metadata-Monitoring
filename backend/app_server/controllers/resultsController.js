const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')


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

module.exports = {
    resultsIndex
};