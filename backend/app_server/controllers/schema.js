const {Schema, model} = require("mongoose")
const bcrypt = require('bcrypt');

const properties_ISO19157_schema = new Schema({
    Dimension: {
        type: String,
        required: true
    },
    Entity: {
        type: String,
        required: true
    },
    Property: {
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
    URL: {
        type: String,
        required: true
    },
    Date: {
        type: String,
        required: true
    },
    properties: {
        type: [properties_mqa_sparql_schema],
        required: true
    }
})

const results_ISO19157_sparql_schema = new Schema({
    URL: {
        type: String,
        required: true
    },
    Date: {
        type: String,
        required: true
    },
    properties: {
        type: [properties_ISO19157_schema],
        required: true
    }
})

const admin_schema = new Schema({
    username: {
        type: String,
        required: true
    },
    password: {
        type: String,
        required: true
    }
})

// check if the user password is valid
admin_schema.methods.validPassword = function(password) {
    return password === this.password
    // return bcrypt.compareSync(password, this.password);
};

module.exports = {
    Results_mqa_sparql: model('results_mqa_sparql', results_mqa_sparql_schema),
    Results_ISO19157: model('results_ISO19157', results_ISO19157_sparql_schema),
    Admin: model('admin', admin_schema)
}