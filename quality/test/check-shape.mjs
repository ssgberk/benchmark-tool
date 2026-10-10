// Checks a collector raw.json against expected-shape.json (keys and types, not values).
import fs from 'node:fs';

const [rawPath, shapePath] = process.argv.slice(2);
const raw = JSON.parse(fs.readFileSync(rawPath, 'utf8'));
const shape = JSON.parse(fs.readFileSync(shapePath, 'utf8'));
const errors = [];

function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

function check(value, expected, where) {
  if (typeof expected === 'string') {
    if (!expected.split('|').includes(typeOf(value))) errors.push(`${where}: ${typeOf(value)} is not ${expected}`);
  } else if (Array.isArray(expected)) {
    if (!Array.isArray(value) || value.length === 0) errors.push(`${where}: expected a non-empty array`);
    else value.forEach((v, i) => check(v, expected[0], `${where}[${i}]`));
  } else {
    if (typeOf(value) !== 'object') {
      errors.push(`${where}: expected an object, got ${JSON.stringify(value).slice(0, 200)}`);
      return;
    }
    for (const [k, e] of Object.entries(expected)) check(value[k], e, `${where}.${k}`);
  }
}

check(raw, shape, 'raw');
for (const preset of ['mobile', 'desktop']) {
  for (const page of ['index', 'post', '404']) {
    if ((raw.lighthouse?.[preset]?.[page] || []).length !== 3) errors.push(`lighthouse.${preset}.${page}: expected 3 runs`);
  }
}
if (raw.rendered?.post?.title !== 'Hello') errors.push('rendered.post.title is not "Hello"');
if (raw.lighthouse?.mobile?.post?.[0]?.resources?.jsBytes !== 0) errors.push('fixture post page should request 0 JS bytes');
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log('raw.json shape ok');
