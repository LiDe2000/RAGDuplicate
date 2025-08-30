import express from 'express'; // Express is a web application framework for Node.js.
import { createProxyMiddleware } from 'http-proxy-middleware'; // Import proxy middleware to forward requests from frontend to backend (e.g. Python FastAPI service).
import path from 'path'; // Node.js built-in module for handling file paths.
import { fileURLToPath } from 'url'; // Node.js built-in module for URL operations.
import { dirname } from 'path'; // Node.js built-in module to get directory name from file path.

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express(); // Create a web application using Express.
const port = 3000; // The port number the server will listen on.

// Serve static files from current directory (frontend)
// app.use(...)：means "use a certain feature".
// express.static('.')：means "use the current folder (.) as a static file directory".
app.use(express.static('.'));

// Proxy API requests to the Python backend
// app.use('/api', ...)：All requests starting with /api are handled by the subsequent "proxy middleware".
// createProxyMiddleware({ ... }): Creates a "proxy rule".
// Requests to /api/search will be forwarded to http://localhost:8000/api/search
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000', // Forward requests to http://localhost:8000 (your Python backend, such as FastAPI service)
  changeOrigin: true, // Allow modification of the "origin address" of the request to avoid cross-domain issues (CORS)
  pathRewrite: {
    '^/api': '/api', // remove base path, this actually doesn't rewrite because 'api' → 'api' is the same. Normally we would write '^/api': '' to "remove the /api prefix".
  },
}));

// Serve index.html for all other routes (SPA support)
// app.get('*', ...): * means "match all routes" (except those already defined, such as /api). Used to support SPA (Single Page Application), such as React, Vue projects.
// (req, res) => { ... }: This is a function that takes two parameters: req: user request (request); res: server response (response).
// res.sendFile(...): Send a file as a response. Here we send the index.html file, used to support SPA (Single Page Application).
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));  // NOTE: __dirname: C:\Users\Administrator\Desktop\RAGDuplicate\frontend
});
// console.log(`__dirname: ${__dirname}`);

// app.listen(...): Makes the server start "listening" on a port, waiting for user access.
app.listen(port, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${port}/`);
  console.log('Local access: http://localhost:3000/');
  console.log('Network access: http://[your-ip-address]:3000/');
});