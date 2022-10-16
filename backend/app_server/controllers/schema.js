const {Schema, model} = require("mongoose")


const properties_ISO19157 = new Schema({
    Dimension: {
        type: String,
        required: true
    },
    Entity: {
        type: String,
        required: true
    },
    Porperty: {
        type: String,
        required: true
    },
    Count: {
        type: Number,
        required: true
    },
    Population: {
        type: Number,
        required: true
    },
    Percentage: {
        type: Number,
        required: true
    },
    Pass: {
        type: Boolean,
        required: true
    }
})

const properties_mqa_sparql_schema = new Schema({
    Dimension: {
        type: String,
        required: true
    },
    Indicator_property: {
        type: String,
        required: true
    },
    Count: {
        type: Number,
        required: true
    },
    Population: {
        type: Number,
        required: true
    },
    Percentage: {
        type: Number,
        required: true
    },
    Points: {
        type: Number,
        required: true
    }
})

const results_mqa_sparql_schema = new Schema({
    Date: {
        type: Date,
        required: true
    },
    properties: {
        type: [properties_mqa_sparql_schema],
        required: true
    }
})

module.exports = {
    results_mqa_sparql: model('results_mqa_sparql', results_mqa_sparql_schema)
}