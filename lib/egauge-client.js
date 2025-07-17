import fetch from 'node-fetch';
import crypto from 'crypto';

export default class EgaugeClient {
  constructor({ host, username, password }) {
    this.host = host;
    this.username = username;
    this.password = password;
    this.token = null;
    this.tokenExpiry = 0;
  }

  async _authenticate() {
    const url = `http://${this.host}/auth`; // placeholder auth endpoint
    const res = await fetch(url, { headers: { Accept: 'application/json' } });
    if (!res.ok) throw new Error(`Auth failed ${res.status}`);
    const challenge = await res.json();
    const cnonce = crypto.randomBytes(8).toString('hex');
    const ha1 = crypto
      .createHash('md5')
      .update(`${this.username}:${challenge.realm}:${this.password}`)
      .digest('hex');
    const ha2 = crypto
      .createHash('md5')
      .update(`GET:${challenge.uri}`)
      .digest('hex');
    const response = crypto
      .createHash('md5')
      .update(`${ha1}:${challenge.nonce}:00000001:${cnonce}:auth:${ha2}`)
      .digest('hex');

    const auth = `Digest username="${this.username}", realm="${challenge.realm}", nonce="${challenge.nonce}", uri="${challenge.uri}", cnonce="${cnonce}", response="${response}", qop=auth, nc=00000001`;
    const tokenRes = await fetch(url, { headers: { Authorization: auth } });
    if (!tokenRes.ok) throw new Error(`Token fetch failed ${tokenRes.status}`);
    const { token, exp } = await tokenRes.json();
    this.token = token;
    this.tokenExpiry = Date.now() + (exp || 600) * 1000 - 10000; // renew 10s early
  }

  async _ensureToken() {
    if (!this.token || Date.now() >= this.tokenExpiry) {
      await this._authenticate();
    }
  }

  async fetchInstantaneousPower() {
    await this._ensureToken();
    const url = `http://${this.host}/api/register?rate`;
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${this.token}` },
    });
    if (!res.ok) throw new Error(`register fetch failed ${res.status}`);
    const data = await res.json();
    let total = 0;
    if (Array.isArray(data.registers)) {
      data.registers.forEach(r => {
        const watts = r.wattseconds_per_second || 0;
        total += watts / 1000; // convert to kW
      });
    }
    return total;
  }
}
