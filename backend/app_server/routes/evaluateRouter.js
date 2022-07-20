const express = require('express');
const router = express.Router();
const evaluateController = require('../controllers/evaluateController')


/* GET users listing. */
router.get('/', evaluateController.executePython);

module.exports = router;
