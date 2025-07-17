const ws = new WebSocket(`ws://${location.host}`);
let chart;
let data = {
  labels: [],
  datasets: [{ label: 'Power (kW)', data: [], borderColor: 'blue', fill: false }]
};
ws.onmessage = evt => {
  const msg = JSON.parse(evt.data);
  if (msg.type === 'power') {
    document.getElementById('inst').textContent = msg.power.toFixed(2);
    document.getElementById('avg').textContent = msg.average.toFixed(2);
    const now = new Date(msg.timestamp);
    data.labels.push(now.toLocaleTimeString());
    data.datasets[0].data.push(msg.power);
    if (data.labels.length > 60) {
      data.labels.shift();
      data.datasets[0].data.shift();
    }
    chart.update();
  }
};
window.onload = () => {
  const ctx = document.getElementById('chart').getContext('2d');
  chart = new Chart(ctx, { type: 'line', data, options: { animation: false } });
};
