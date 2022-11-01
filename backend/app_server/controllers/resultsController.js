const { Results_mqa_sparql, Results_ISO19157 } = require('./schema')


//Return every 'URL - DATE - MQA/ISO19157' in the database
const resultsIndex = async function (req, res) {
    let result_mqa = await Results_mqa_sparql.find({}).then(r => {
        let result = []
        for(let i=0; i<r.length-1; i++) {
            let property = {
                URL: r[i].URL,
                Date: r[i].Date,
                Method: 'MQA'
            }
            result.push(property)
        }
        return result
    })

    let result_ISO19157 = await Results_ISO19157.find({}).then(r => {
        let result = []
        for(let i=0; i<r.length-1; i++) {
            let property = {
                URL: r[i].URL,
                Date: r[i].Date,
                Method: 'ISO19157'
            }
            result.push(property)
        }
        return result
    })
    //Concatenar los dos arrays
    res.json(result_ISO19157)
}

module.exports = {
    resultsIndex
};