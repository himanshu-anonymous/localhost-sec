/**
 * Lightweight Zero-Dependency Frontend Server for BASTION X
 * Binds to http://localhost:3000
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const INDEX_PATH = path.join(__dirname, 'index.html');

const server = http.createServer((req, res) => {
    // Serve index.html for all routes (SPA behavior)
    fs.readFile(INDEX_PATH, (err, data) => {
        if (err) {
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Error loading dashboard: ' + err.message);
            return;
        }
        res.writeHead(200, {
            'Content-Type': 'text/html; charset=utf-8',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(data);
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`=======================================================`);
    console.log(` BASTION X Frontend Server listening at http://localhost:${PORT}`);
    console.log(` Connected to Backend API at http://localhost:8000`);
    console.log(`=======================================================`);
});
