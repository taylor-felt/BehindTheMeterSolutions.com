export default class MovingAverage {
  constructor(size) {
    this.size = size;
    this.buffer = new Array(size).fill(0);
    this.index = 0;
    this.count = 0;
    this.total = 0;
  }
  add(value) {
    this.total -= this.buffer[this.index];
    this.buffer[this.index] = value;
    this.total += value;
    this.index = (this.index + 1) % this.size;
    if (this.count < this.size) this.count++;
  }
  average() {
    if (this.count === 0) return 0;
    return this.total / this.count;
  }
}
