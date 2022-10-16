const express = require('express');
const router = express.Router();
const evaluateController = require('../controllers/evaluateController')
const passport = require('passport')

/* GET users listing. */
router.get('/mqa_sparql', evaluateController.mqa_sparql);
router.get('/admin_tasks', isAdminLoggedIn, evaluateController.test_true);


// route middleware to make sure a user is logged in
function isAdminLoggedIn(req, res, next) {
    // if user is authenticated in the session, carry on
    if (req.isAuthenticated())
        return next();
    // if they aren't redirect them to the home page
    res.redirect('/');
}


module.exports = router;
