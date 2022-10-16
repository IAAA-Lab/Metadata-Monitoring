const express = require('express');
const router = express.Router();
const evaluateController = require('../controllers/evaluateController')


/* GET users listing. */
router.get('/mqa_sparql', evaluateController.mqa_sparql);

module.exports = router;
