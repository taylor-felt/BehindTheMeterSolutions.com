export default class RateManager {
  constructor() {
    this.schedules = [];
  }

  load(schedules) {
    this.schedules = schedules || [];
  }

  currentRate(date = new Date()) {
    // simple example: return first schedule's rate
    const s = this.schedules.find(r => r.start <= date && date <= r.end);
    return s ? s.rate : 0;
  }
}
