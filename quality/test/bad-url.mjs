// Regression check: a malformed percent-escape in a page URL must not crash the collector.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';

const pages = { post: { url: '/%E0%A4%A/', file: 'post/hello/index.html' } };
const r = spawnSync('node', ['/quality/run.mjs', '--site', '/fixture', '--pages', JSON.stringify(pages), '--out', '/tmp/bad'],
  { encoding: 'utf8' });
if (r.status !== 0) { console.error(`collector exited ${r.status}\n${r.stderr}`); process.exit(1); }
if (!fs.existsSync('/tmp/bad/raw.json')) { console.error('raw.json not written'); process.exit(1); }
console.log('bad url survived, raw.json written');
