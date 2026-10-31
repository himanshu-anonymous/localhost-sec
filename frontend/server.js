/**
 * Production Static & Proxy Server for BASTION X (ES Module)
 * Serves compiled React production bundle from dist/ and proxies API/WS to FastAPI backend
 */
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import net from 'node:net';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT = process.env.PORT || 3000;
const BACKEND_PORT = process.env.BACKEND_PORT || 8000;
const BACKEND_HOST = process.env.BACKEND_HOST || '127.0.0.1';

const DIST_DIR = path.join(__dirname, 'dist');
const INDEX_PATH = path.join(DIST_DIR, 'index.html');

const MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.mjs': 'application/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf'
};

const server = http.createServer((req, res) => {
    // 1. Proxy API routes to FastAPI Backend
    if (req.url.startsWith('/api') || req.url.startsWith('/health') || req.url.startsWith('/docs') || req.url.startsWith('/openapi.json')) {
        const options = {
            hostname: BACKEND_HOST,
            port: BACKEND_PORT,
            path: req.url,
            method: req.method,
            headers: req.headers
        };
        const proxyReq = http.request(options, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers);
            proxyRes.pipe(res, { end: true });
        });
        proxyReq.on('error', (err) => {
            res.writeHead(502, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Backend unreachable', details: err.message }));
        });
        req.pipe(proxyReq, { end: true });
        return;
    }

    // 2. Serve static files from dist/
    const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    let pathname = decodeURIComponent(parsedUrl.pathname);
    if (pathname === '/') pathname = '/index.html';

    let filePath = path.join(DIST_DIR, pathname);

    // Prevent directory traversal
    if (!filePath.startsWith(DIST_DIR)) {
        res.writeHead(403);
        res.end('Forbidden');
        return;
    }

    fs.stat(filePath, (err, stats) => {
        if (!err && stats.isFile()) {
            const ext = path.extname(filePath).toLowerCase();
            const mime = MIME_TYPES[ext] || 'application/octet-stream';
            res.writeHead(200, {
                'Content-Type': mime,
                'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=31536000',
                'Access-Control-Allow-Origin': '*'
            });
            fs.createReadStream(filePath).pipe(res);
        } else {
            // SPA Fallback: serve index.html
            fs.readFile(INDEX_PATH, (err2, data) => {
                if (err2) {
                    res.writeHead(500, { 'Content-Type': 'text/plain' });
                    res.end('Error loading dashboard: ' + err2.message);
                    return;
                }
                res.writeHead(200, {
                    'Content-Type': 'text/html; charset=utf-8',
                    'Access-Control-Allow-Origin': '*'
                });
                res.end(data);
            });
        }
    });
});

// Forward WebSocket upgrade requests to backend
server.on('upgrade', (req, socket, head) => {
    const proxySocket = net.connect(BACKEND_PORT, BACKEND_HOST, () => {
        proxySocket.write(
            `${req.method} ${req.url} HTTP/${req.httpVersion}\r\n` +
            Object.keys(req.headers).map(k => `${k}: ${req.headers[k]}`).join('\r\n') +
            '\r\n\r\n'
        );
        if (head && head.length) proxySocket.write(head);
        proxySocket.pipe(socket);
        socket.pipe(proxySocket);
    });

    proxySocket.on('error', () => {
        socket.destroy();
    });
    socket.on('error', () => {
        proxySocket.destroy();
    });
});

server.listen(PORT, '0.0.0.0', () => {
    console.log(`=======================================================`);
    console.log(` BASTION X Frontend Server listening at http://localhost:${PORT}`);
    console.log(` Serving production assets from: ${DIST_DIR}`);
    console.log(` Proxying API & WebSockets to http://${BACKEND_HOST}:${BACKEND_PORT}`);
    console.log(`=======================================================`);
});
