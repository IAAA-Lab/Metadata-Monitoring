const mongoose = require('mongoose');
const config = require('../config/db.config');

let uri = config.url;

mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true });

// Monitored the Mongoose connection events
mongoose.connection.on('connected', () => {
    console.log(`Mongoose connected to ${uri}`);
});

mongoose.connection.on('error', err => {
    console.log('Mongoose connection error:', err);
});
mongoose.connection.on('disconnected', () => {
    console.log('Mongoose disconnected');
});


module.exports = {
    mongoose
}
