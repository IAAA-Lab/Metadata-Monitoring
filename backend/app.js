const createError = require('http-errors');
const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const cors = require('cors');
const Agenda = require('agenda');
const connectionDB = require('./app_server/config/db.config')
const passport = require('passport');
var session = require('express-session');

const agenda = new Agenda({db: {address: connectionDB.url_agenda}});
require('./app_server/services/connection')
require('./app_server/config/passport')(passport);

const evaluateRouter = require('./app_server/routes/evaluateRouter');

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

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

//TODO: mirar de reiniciar los jobs cuando se reinicia el server (pruebas posteriores han funcionado
// simplemente haciendo un start
// https://github.com/Trustroots/trustroots/blob/master/config/lib/worker.js#L175-L228
// https://medium.com/techwomenc/c%C3%B3mo-ejecutar-funciones-peri%C3%B3dicamente-en-nodejs-cba7dec14691
agenda.define('sendNewsletter', function(job) {
  console.log("Sending newsletter. Time: " +
      new Date().getMinutes() + ":" + new Date().getSeconds());
});

agenda.on('ready', function() {
  // agenda.every('3 seconds', 'sendNewsletter');
  // agenda.enable();
  agenda.start();

  //Cancelar job despues de 10 segundos
  setTimeout(function() {
    agenda.cancel({name: 'sendNewsletter'}, function(err, numRemoved) {
      console.log('Job canceled');
    });
  }, 100000);
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

//stops the agenda module gracefully
async function graceful() {
  await agenda.stop();
  process.exit(0);
}

process.on("SIGTERM", graceful);
process.on("SIGINT", graceful);

module.exports = app;
