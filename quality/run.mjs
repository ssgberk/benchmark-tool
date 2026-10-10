// SSGBerk quality collector (benchmark-tool spec 009). Writes raw data only:
// toolset/quality/reduce.py turns raw.json into quality.json.
import { execFile } from 'node:child_process';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs, promisify } from 'node:util';
import zlib from 'node:zlib';

import * as chromeLauncher from 'chrome-launcher';
import { HtmlValidate } from 'html-validate';
import lighthouse from 'lighthouse';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';
import { chromium } from 'playwright';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const RUNS = 3;
const PRESETS = { mobile: undefined, desktop: desktopConfig };
const CATEGORIES = ['performance', 'accessibility', 'best-practices', 'seo'];
const CHROME_FLAGS = ['--headless=new', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage'];
const NOT_SCORED = new Set(['informative', 'manual', 'notApplicable', 'error']);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.gif': 'image/gif', '.ico': 'image/x-icon', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.wasm': 'application/wasm',
};
const COMPRESSIBLE = /^(text\/|application\/(json|xml|wasm)|image\/svg\+xml)/;
const execFileP = promisify(execFile);

async function guard(fn) {
  try {
    return await fn();
  } catch (e) {
    return { error: String(e && e.message ? e.message : e) };
  }
}

async function isFile(p) {
  try {
    return (await fs.stat(p)).isFile();
  } catch {
    return false;
  }
}

async function resolveFile(root, pathname) {
  let rel;
  try {
    rel = decodeURIComponent(pathname).replace(/^\/+/, '');
  } catch {
    return null;
  }
  const base = path.resolve(root, rel);
  if (base !== root && !base.startsWith(root + path.sep)) return null;
  const candidates = rel === '' || rel.endsWith('/')
    ? [path.join(base, 'index.html')]
    : [base, path.join(base, 'index.html'), `${base}.html`];
  for (const c of candidates) if (await isFile(c)) return c;
  return null;
}

// Fixed static server: gzip, no-cache, directory index, 404.html with status 404.
function serve(root) {
  const handle = async (req, res) => {
    const { pathname } = new URL(req.url, 'http://127.0.0.1');
    let file = await resolveFile(root, pathname);
    let status = 200;
    if (!file) {
      status = 404;
      file = (await isFile(path.join(root, '404.html'))) ? path.join(root, '404.html') : null;
    }
    let body = file ? await fs.readFile(file) : Buffer.from('Not found');
    const type = file ? TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream'
      : 'text/plain; charset=utf-8';
    const headers = { 'content-type': type, 'cache-control': 'no-cache' };
    if (COMPRESSIBLE.test(type) && /\bgzip\b/.test(req.headers['accept-encoding'] || '')) {
      body = zlib.gzipSync(body);
      headers['content-encoding'] = 'gzip';
      headers.vary = 'accept-encoding';
    }
    headers['content-length'] = body.length;
    res.writeHead(status, headers);
    res.end(req.method === 'HEAD' ? undefined : body);
  };
  // A failing request must never take the collector down (spec R-16).
  const server = http.createServer(async (req, res) => {
    try {
      await handle(req, res);
    } catch (e) {
      if (!res.headersSent) res.writeHead(500, { 'content-type': 'text/plain; charset=utf-8' });
      res.end('Internal error');
    }
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve({
    server, origin: `http://127.0.0.1:${server.address().port}`,
  })));
}

function summarize(lhr) {
  const audits = lhr.audits;
  const value = (id) => audits[id]?.numericValue ?? null;
  const requests = audits['network-requests']?.details?.items ?? [];
  const bytes = (type) => requests.filter((r) => r.resourceType === type)
    .reduce((sum, r) => sum + (r.transferSize || 0), 0);
  return {
    scores: Object.fromEntries(CATEGORIES.map((c) => [c, lhr.categories[c]?.score ?? null])),
    metrics: {
      fcp: value('first-contentful-paint'),
      lcp: value('largest-contentful-paint'),
      tbt: value('total-blocking-time'),
      cls: value('cumulative-layout-shift'),
      si: value('speed-index'),
    },
    resources: {
      totalBytes: value('total-byte-weight'),
      jsBytes: bytes('Script'),
      cssBytes: bytes('Stylesheet'),
      requests: requests.length,
      domSize: value('dom-size') ?? value('dom-size-insight'),
    },
    failedAudits: Object.values(audits)
      .filter((a) => !NOT_SCORED.has(a.scoreDisplayMode) && a.score !== null && a.score < 1)
      .map((a) => a.id).sort(),
  };
}

async function runLighthouse(origin, pages) {
  const chrome = await chromeLauncher.launch({
    chromePath: chromium.executablePath(), chromeFlags: CHROME_FLAGS,
  });
  try {
    const out = {};
    for (const [preset, config] of Object.entries(PRESETS)) {
      out[preset] = {};
      for (const [key, page] of Object.entries(pages)) {
        const runs = [];
        for (let i = 0; i < RUNS; i += 1) {
          runs.push(await guard(async () => {
            const result = await lighthouse(origin + page.url, {
              port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: CATEGORIES,
            }, config);
            if (!result?.lhr) throw new Error('lighthouse returned no report');
            if (result.lhr.runtimeError) throw new Error(result.lhr.runtimeError.message);
            return summarize(result.lhr);
          }));
        }
        out[preset][key] = runs;
      }
    }
    return out;
  } finally {
    await chrome.kill();
  }
}

async function runBrowserChecks(origin, pages) {
  const axeSource = await fs.readFile(path.join(HERE, 'node_modules', 'axe-core', 'axe.min.js'), 'utf8');
  const browser = await chromium.launch({ args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  try {
    const axe = {};
    for (const [key, page] of Object.entries(pages)) {
      axe[key] = await guard(async () => {
        const tab = await browser.newPage();
        try {
          await tab.goto(origin + page.url, { waitUntil: 'load' });
          await tab.addScriptTag({ content: axeSource });
          const result = await tab.evaluate(() => window.axe.run(document, { resultTypes: ['violations'] }));
          return {
            violations: result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })),
          };
        } finally {
          await tab.close();
        }
      });
    }
    const post = await guard(async () => {
      const tab = await browser.newPage();
      try {
        await tab.goto(origin + pages.post.url, { waitUntil: 'networkidle' });
        const text = async (selector) => ((await tab.locator(selector).first()
          .textContent({ timeout: 5000 })) || '').trim();
        return { title: await text('h1.post-title'), firstParagraph: await text('.post-body p') };
      } finally {
        await tab.close();
      }
    });
    return { axe, rendered: { post }, chromium: browser.version() };
  } finally {
    await browser.close();
  }
}

async function runHtmlValidate(site, pages) {
  const validator = new HtmlValidate({ extends: ['html-validate:recommended'] });
  const out = {};
  for (const [key, page] of Object.entries(pages)) {
    out[key] = await guard(async () => {
      const report = await validator.validateFile(path.join(site, page.file));
      return {
        messages: report.results.flatMap((r) => r.messages)
          .map((m) => ({ ruleId: m.ruleId, severity: m.severity })),
      };
    });
  }
  return out;
}

async function runLychee(site, outDir) {
  const report = path.join(outDir, 'lychee.json');
  try {
    await execFileP('lychee', ['--offline', '--no-progress', '--include-fragments', '--index-files', 'index.html',
      '--format', 'json', '--output', report, '--root-dir', site, site], { maxBuffer: 64 * 1024 * 1024 });
  } catch (e) {
    // exit code 2 means broken links; the report is still written
    if (!(await isFile(report))) throw e;
  }
  return { report: JSON.parse(await fs.readFile(report, 'utf8')) };
}

async function listFiles(dir) {
  const out = [];
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...await listFiles(full));
    else if (entry.isFile()) out.push(full);
  }
  return out;
}

async function sizes(site) {
  const files = [];
  for (const full of (await listFiles(site)).sort()) {
    const data = await fs.readFile(full);
    files.push({
      path: path.relative(site, full).split(path.sep).join('/'),
      bytes: data.length,
      gzip: zlib.gzipSync(data, { level: 9 }).length,
      br: zlib.brotliCompressSync(data, {
        params: { [zlib.constants.BROTLI_PARAM_QUALITY]: 11 },
      }).length,
    });
  }
  return files;
}

async function packageVersion(name) {
  const file = path.join(HERE, 'node_modules', name, 'package.json');
  return JSON.parse(await fs.readFile(file, 'utf8')).version;
}

async function tools(chromiumVersion) {
  const lychee = await guard(async () => (await execFileP('lychee', ['--version'])).stdout.trim()
    .split(/\s+/).pop());
  return {
    node: process.version,
    lighthouse: await packageVersion('lighthouse'),
    playwright: await packageVersion('playwright'),
    chromium: chromiumVersion ?? null,
    axeCore: await packageVersion('axe-core'),
    htmlValidate: await packageVersion('html-validate'),
    chromeLauncher: await packageVersion('chrome-launcher'),
    lychee: typeof lychee === 'string' ? lychee : null,
  };
}

async function main() {
  const { values } = parseArgs({
    options: { site: { type: 'string' }, pages: { type: 'string' }, out: { type: 'string' } },
  });
  const site = path.resolve(values.site);
  const pages = JSON.parse(values.pages);
  const outDir = path.resolve(values.out);
  await fs.mkdir(outDir, { recursive: true });
  const raw = { pages };
  const { server, origin } = await serve(site);
  try {
    const browser = await guard(() => runBrowserChecks(origin, pages));
    raw.axe = browser.error ? browser : browser.axe;
    raw.rendered = browser.error ? browser : browser.rendered;
    raw.lighthouse = await guard(() => runLighthouse(origin, pages));
    raw.html = await guard(() => runHtmlValidate(site, pages));
    raw.links = await guard(() => runLychee(site, outDir));
    raw.files = await guard(() => sizes(site));
    raw.tools = await guard(() => tools(browser.chromium));
  } finally {
    server.close();
  }
  await fs.writeFile(path.join(outDir, 'raw.json'), JSON.stringify(raw, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
