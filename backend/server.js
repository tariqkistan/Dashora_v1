const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = 'your-secret-key'; // In production, use env variable

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: 'Forbidden' });
    req.user = user;
    next();
  });
};

// Sample data
const DOMAINS = [
  {
    domain: 'example.com',
    name: 'Example Store',
    woocommerce_enabled: true,
    ga_enabled: true
  },
  {
    domain: 'test-store.com',
    name: 'Test Store',
    woocommerce_enabled: true,
    ga_enabled: false
  }
];

const generateMetrics = (domain, days = 30) => {
  const metrics = [];
  const now = Math.floor(Date.now() / 1000);
  const dayInSeconds = 86400;
  
  for (let i = 0; i < days; i++) {
    const timestamp = now - (i * dayInSeconds);
    metrics.push({
      domain,
      timestamp,
      pageviews: Math.floor(Math.random() * 500) + 100,
      visitors: Math.floor(Math.random() * 200) + 50,
      orders: Math.floor(Math.random() * 20) + 1,
      revenue: parseFloat((Math.random() * 1000 + 100).toFixed(2))
    });
  }
  
  return metrics;
};

// Routes
app.post('/login', (req, res) => {
  const { email, password } = req.body;
  
  // Simple validation - in production, you'd check against a database
  if (email === 'admin@example.com' && password === 'password') {
    const token = jwt.sign({ email }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

app.get('/domains', authenticateToken, (req, res) => {
  res.json({ domains: DOMAINS });
});

app.get('/metrics/:domain', authenticateToken, (req, res) => {
  const { domain } = req.params;
  
  if (!DOMAINS.some(d => d.domain === domain)) {
    return res.status(404).json({ error: 'Domain not found' });
  }
  
  res.json({ metrics: generateMetrics(domain) });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 