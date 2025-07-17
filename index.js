import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';
import Database from '@replit/database';
import EgaugeClient from './lib/egauge-client.js';
import MovingAverage from './lib/moving-average.js';
import RateManager from './lib/rate-manager.js';

dotenv.config();
const PORT = process.env.PORT || 3000;
const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const server = createServer(app);
const wss = new WebSocketServer({ server });

// Replit key-value store for configuration
const db = new Database();

const egauge = new EgaugeClient({
  host: process.env.EGAUGE_HOST,
  username: process.env.EGAUGE_USERNAME,
  password: process.env.EGAUGE_PASSWORD,
});

const movingAvg = new MovingAverage(30); // 30-second moving average

wss.on('connection', ws => {
  ws.send(JSON.stringify({ type: 'info', message: 'connected' }));
});

async function broadcastData() {
  try {
    const power = await egauge.fetchInstantaneousPower();
    movingAvg.add(power);
    const avg = movingAvg.average();
    const data = { type: 'power', power, average: avg, timestamp: Date.now() };
    wss.clients.forEach(client => {
      if (client.readyState === 1) {
        client.send(JSON.stringify(data));
      }
    });
  } catch (err) {
    console.error('eGauge fetch error', err.message);
  }
}
setInterval(broadcastData, 1000);

app.get('/api/config', async (req, res) => {
  const cfg = await db.get('config');
  res.json(cfg || {});
});

app.post('/api/config', async (req, res) => {
  await db.set('config', req.body);
  res.json({ status: 'saved' });
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
