const express = require('express');
const router = express.Router();
const evaluateController = require('../controllers/evaluateController')
const passport = require('passport')

//root is '/evaluate'
router.get('/', evaluateController.evaluate);


module.exports = router;
