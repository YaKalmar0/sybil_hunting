import express from "express";
import ejs from "ejs";
import axios from "axios";
import bodyParser from "body-parser";

const app = express();
const port = 3000;

app.use(express.static("public"));
app.use(bodyParser.urlencoded({extended: true}));

app.get("/", (req, res) => {
    res.render("index.ejs");
});

app.get("/page1", (req, res) => {
    res.render("page1.ejs");
});

app.get("/page2", (req, res) => {
    res.render("page2.ejs");
});

app.get("/page3", (req, res) => {
    res.render("page3.ejs");
});

app.get("/1", (req, res) => {
    res.render("1.ejs");
});

app.get("/2", (req, res) => {
    res.render("2.ejs");
});

app.get("/3", (req, res) => {
    res.render("3.ejs");
});

app.listen(port, (req, res) => {
    console.log(`Server is running on port${port}`);
});