/**
 * ==============================================================================
 * METRI-REPORT PRODUCTION SERVER & GATEWAY
 * ==============================================================================
 * 
 * Functions:
 * 1. Serves the Three.js WebGL 3D Platform (Homepage, Evaluation Wizard, Subpages).
 * 2. Static asset streaming with caching and correct MIME type dispatch.
 * 3. Reverse-proxy gateway for FastAPI Backend (`/api/v1/*`, `/docs`, `/openapi.json`).
 * 4. Pretty-route mapping for all 7 Statutory Metrology Modules.
 * ==============================================================================
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.wasm': 'application/wasm',
  '.bin': 'application/octet-stream',
  '.hdr': 'image/vnd.radiance'
};

const ROUTE_MAP = {
  '/': '/index.html',
  '/index': '/index.html',
  '/index.html': '/index.html',

  '/instruments': '/instrument-registry/index.html',
  '/instruments/': '/instrument-registry/index.html',
  '/instrument-registry': '/instrument-registry/index.html',
  '/instrument-registry/': '/instrument-registry/index.html',
  '/use-cases': '/instrument-registry/index.html',
  '/use-cases/': '/instrument-registry/index.html',

  '/workspace': '/evaluation-workspace/index.html',
  '/workspace/': '/evaluation-workspace/index.html',
  '/evaluation-workspace': '/evaluation-workspace/index.html',
  '/evaluation-workspace/': '/evaluation-workspace/index.html',
  '/pricing': '/evaluation-workspace/index.html',
  '/pricing/': '/evaluation-workspace/index.html',

  '/reports': '/report-archive/index.html',
  '/reports/': '/report-archive/index.html',
  '/report-archive': '/report-archive/index.html',
  '/report-archive/': '/report-archive/index.html',
  '/docs': '/report-archive/index.html',
  '/docs/': '/report-archive/index.html',

  '/standards': '/OIML-Rule-Engine/index.html',
  '/standards/': '/OIML-Rule-Engine/index.html',
  '/OIML-Rule-Engine': '/OIML-Rule-Engine/index.html',
  '/OIML-Rule-Engine/': '/OIML-Rule-Engine/index.html',
  '/oiml-rule-engine': '/OIML-Rule-Engine/index.html',
  '/oiml-rule-engine/': '/OIML-Rule-Engine/index.html',
  '/book-demo': '/OIML-Rule-Engine/index.html',
  '/book-demo/': '/OIML-Rule-Engine/index.html',

  '/evidence': '/evidence-&-vault/index.html',
  '/evidence/': '/evidence-&-vault/index.html',
  '/evidence-&-vault': '/evidence-&-vault/index.html',
  '/evidence-&-vault/': '/evidence-&-vault/index.html',
  '/evidence-vault': '/evidence-&-vault/index.html',
  '/evidence-vault/': '/evidence-&-vault/index.html',
  '/blog': '/evidence-&-vault/index.html',
  '/blog/': '/evidence-&-vault/index.html',

  '/users': '/user-privileges-&-rbac/index.html',
  '/users/': '/user-privileges-&-rbac/index.html',
  '/user-privileges-&-rbac': '/user-privileges-&-rbac/index.html',
  '/user-privileges-&-rbac/': '/user-privileges-&-rbac/index.html',
  '/user-privileges-rbac': '/user-privileges-&-rbac/index.html',
  '/user-privileges-rbac/': '/user-privileges-&-rbac/index.html',
  '/about': '/user-privileges-&-rbac/index.html',
  '/about/': '/user-privileges-&-rbac/index.html',

  '/audit-logs': '/audit-trail-log/index.html',
  '/audit-logs/': '/audit-trail-log/index.html',
  '/audit-trail-log': '/audit-trail-log/index.html',
  '/audit-trail-log/': '/audit-trail-log/index.html',
  '/contact': '/audit-trail-log/index.html',
  '/contact/': '/audit-trail-log/index.html',

  '/privacy': '/privacy/index.html',
  '/privacy/': '/privacy/index.html',
  '/terms-of-service': '/terms-of-service/index.html',
  '/terms-of-service/': '/terms-of-service/index.html'
};

function proxyRequest(req, res) {
  const parsedBackend = new URL(BACKEND_URL);
  const options = {
    hostname: parsedBackend.hostname,
    port: parsedBackend.port || 8000,
    path: req.url,
    method: req.method,
    headers: {
      ...req.headers,
      host: `${parsedBackend.hostname}:${parsedBackend.port || 8000}`
    }
  };

  const proxyReq = http.request(options, (backendRes) => {
    res.writeHead(backendRes.statusCode, backendRes.headers);
    backendRes.pipe(res, { end: true });
  });

  proxyReq.on('error', (err) => {
    console.error('Backend proxy error:', err.message);
    res.writeHead(502, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Backend gateway error', details: err.message }));
  });

  req.pipe(proxyReq, { end: true });
}

function handleRequest(req, res) {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  let pathname = decodeURIComponent(parsedUrl.pathname);

  // 1. Proxy API and OpenAPI / Swagger / ReDoc requests
  if (pathname === '/api' || pathname.startsWith('/api/') || pathname === '/openapi.json' || pathname === '/docs' || pathname.startsWith('/docs/') || pathname === '/redoc' || pathname.startsWith('/redoc/')) {
    return proxyRequest(req, res);
  }

  // 2. Route Aliases
  if (ROUTE_MAP[pathname]) {
    pathname = ROUTE_MAP[pathname];
  }

  // 3. Security
  let safePath = path.normalize(path.join(__dirname, pathname));
  if (!safePath.startsWith(__dirname)) {
    res.writeHead(403, { 'Content-Type': 'text/plain' });
    return res.end('Forbidden');
  }

  // 4. Resolve file
  let targetFile = safePath;
  if (fs.existsSync(targetFile) && fs.statSync(targetFile).isDirectory()) {
    targetFile = path.join(targetFile, 'index.html');
  } else if (!fs.existsSync(targetFile)) {
    if (fs.existsSync(targetFile + '.html')) {
      targetFile = targetFile + '.html';
    } else if (fs.existsSync(path.join(targetFile, 'index.html'))) {
      targetFile = path.join(targetFile, 'index.html');
    }
  }

  if (fs.existsSync(targetFile) && fs.statSync(targetFile).isFile()) {
    const ext = path.extname(targetFile).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.setHeader('Content-Type', contentType);
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    if (ext === '.html' || ext === '.js' || ext === '.css' || ext === '.json' || ext === '.ico' || targetFile.includes('favicon')) {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
    } else {
      res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    }

    const stream = fs.createReadStream(targetFile);
    stream.pipe(res);
  } else {
    const fallback = path.join(__dirname, 'index.html');
    if (fs.existsSync(fallback)) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      fs.createReadStream(fallback).pipe(res);
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found');
    }
  }
}

function startServerOnPort(port) {
  const s = http.createServer(handleRequest);
  s.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} in use, skipping creation.`);
    } else {
      console.error(`Error on port ${port}:`, err.message);
    }
  });
  s.listen(port, () => {
    console.log(`🚀 Metri-Report Server listening at http://localhost:${port}`);
  });
}

const PORT = process.env.PORT || 3000;
startServerOnPort(PORT);
