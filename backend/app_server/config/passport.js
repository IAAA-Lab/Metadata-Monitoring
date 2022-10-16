const LocalStrategy = require('passport-local').Strategy;
const { Admin } = require('../controllers/schema');

// expose this function to our app using module.exports
module.exports = function(passport) {

    passport.serializeUser(function(user, done) {
        done(null, user);
    });
    passport.deserializeUser(function(user, done) {
        done(null, user);
    });

    passport.use('local', new LocalStrategy(function(username, password, done) {
        Admin.findOne({ username:  username }, function(err, user) {
            // if there are any errors, return the error
            if (err) { return done(err); }

            if (!user) {
                return done(null, false, {message: 'Wrong username'});
            }

            if (!user.validPassword(password)) {
                return done(null, false, {message: 'Wrong password'});
            }
            // all is well, return successful user
            return done(null, user);
        });
    }));
};