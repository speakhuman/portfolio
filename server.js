// Simple HTTP server using Node.js built-in http module
const http = require('http');
const fs = require('fs');
const path = require('path');
const net = require('net');

// Function to find an available port
function findAvailablePort(startPort, callback) {
  const server = net.createServer();
  server.listen(startPort, () => {
    const port = server.address().port;
    server.close(() => callback(port));
  });
  
  server.on('error', () => {
    // Port is in use, try the next one
    findAvailablePort(startPort + 1, callback);
  });
}

// MIME types for different file extensions
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

// Create the server
const server = http.createServer((req, res) => {
  console.log(`Request for ${req.url}`);
  
  // Get the file path
  let filePath = '.' + req.url;
  if (filePath === './') {
    filePath = './index.html';
  }
  
  // Get the file extension
  const extname = path.extname(filePath);
  
  // Set the content type based on the file extension
  const contentType = MIME_TYPES[extname] || 'application/octet-stream';
  
  // Read the file
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // File not found
        console.error(`File not found: ${filePath}`);
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1><p>The requested file could not be found.</p>', 'utf-8');
      } else {
        // Server error
        console.error(`Server error: ${err.code}`);
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      // Success
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

  const PORT = process.env.PORT || 3000;
  server.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
    console.log(`Open this URL in your browser to view the blog `);
    console.log(`Press Ctrl+C to stop the server`);
  });
});