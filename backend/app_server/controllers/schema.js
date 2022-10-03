const {Schema, model} = require("mongoose")

const resultSchema = new Schema({
    text: {
        type: String,
        required: true
    }
})

//Create Model Object, specify collection and schema
const ResultSchema = model('result', resultSchema)

module.exports = {
    Result: ResultSchema
}