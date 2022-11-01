const express = require('express');
const router = express.Router();
const resultsController = require('../controllers/resultsController')

//root is '/results'
router.get('/', resultsController.resultsIndex);
router.get('/export', resultsController.exportData);


module.exports = router;
