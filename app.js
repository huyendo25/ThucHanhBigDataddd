const express = require('express');
const bodyParser = require('body-parser');
const todo = require('./routes/todo.route');
const app = express();
const dbConfig = 'mongodb://localhost:27017/todo';
const mongoose = require('mongoose');

//Connect to mongoose
mongoose.connect(dbConfig, { useNewUrlParser: true }).then(() => {
    console.log("Successfully connected to the database");
}).catch(err => {
    console.log('Could not connect to the database. Exiting now...', err);
    process.exit();
});
app.set('view engine','ejs');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true}));




app.use('/todo', todo);
let port = 1234;
app.listen(port, () => {
    console.log('Server is up and running on port numner ' + port);
});


