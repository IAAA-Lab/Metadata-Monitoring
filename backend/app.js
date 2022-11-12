const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require('cors');
const connectionDB = require('./app_server/config/db.config')
const passport = require('passport');
var session = require('express-session');
const {Agenda} = require('agenda');



require('./app_server/services/connection')
require('./app_server/config/passport')(passport);

const evaluateRouter = require('./app_server/routes/evaluateRouter');
const resultsRouter = require('./app_server/routes/resultsRouter');

const app = express();

// view engine setup
app.set('views', path.join(__dirname, './app_server/views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));
app.use(cors())

app.use(session({ secret: 'secreto' })); // session secret
app.use(passport.initialize());
app.use(passport.session()); // persistent login sessions


app.post('/login', passport.authenticate('local'), function(req, res) {
  res.json({isAdminLoggedIn: true});
});
app.post('/logout', function(req, res, next){
  req.logout(function(err) {
    if (err) { return next(err); }
    res.redirect('/');
  });
});

app.use('/evaluate', evaluateRouter);
app.use('/results', resultsRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});


// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});



module.exports = app
