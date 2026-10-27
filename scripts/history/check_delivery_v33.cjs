// 独立交付校验：全新浏览器打开预览，自动加载、无文件选择器、无控制台错误、四向截图
// 用法: node check_delivery_v33.cjs <html路径> <截图前缀> <报告json>
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const fs = require('fs');
const crypto = require('crypto');

const target = process.argv[2];
const prefix = process.argv[3] || 'delivery-check';
const reportPath = process.argv[4] || 'delivery-check.json';

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
    args: ['--use-angle=d3d11', '--enable-webgl', '--allow-file-access-from-files'],
  });
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 900 } });
  const page = await ctx.newPage();
  const consoleMsgs = [];
  const pageErrors = [];
  const failedRequests = [];
  page.on('console', m => consoleMsgs.push({ type: m.type(), text: m.text() }));
  page.on('pageerror', e => pageErrors.push(String(e && e.message || e)));
  page.on('requestfailed', r => failedRequests.push({ url: r.url(), err: r.failure() && r.failure().errorText }));

  const started = Date.now();
  await page.goto(pathToFileURL(target).href, { timeout: 180000, waitUntil: 'commit' });
  await page.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true, { timeout: 240000 });
  await page.waitForFunction(() => !!window.pet, { timeout: 240000 });
  await page.waitForTimeout(2500);
  const loadSeconds = (Date.now() - started) / 1000;

  // 页面内：自动加载状态、文件选择器数量、模型规模、解压后字节的 SHA-256
  const info = await page.evaluate(async () => {
    const hex = b => Array.from(new Uint8Array(b)).map(x => x.toString(16).padStart(2, '0')).join('');
    let sha = null;
    if (window.MODEL_BYTES) sha = hex(await crypto.subtle.digest('SHA-256', window.MODEL_BYTES));
    let meshes = 0, tris = 0, verts = 0;
    const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
    const apply = (m, v) => {
      const e = m.elements, x = v[0], y = v[1], z = v[2];
      return [e[0] * x + e[4] * y + e[8] * z + e[12], e[1] * x + e[5] * y + e[9] * z + e[13], e[2] * x + e[6] * y + e[10] * z + e[14]];
    };
    if (window.pet) {
      window.pet.updateMatrixWorld(true);
      window.pet.traverse(o => {
        if (o.isMesh && o.geometry) {
          meshes++;
          const g = o.geometry;
          verts += g.attributes.position ? g.attributes.position.count : 0;
          if (g.index) tris += g.index.count / 3;
          else if (g.attributes.position) tris += g.attributes.position.count / 3;
          if (!g.boundingBox) g.computeBoundingBox();
          const b = g.boundingBox;
          if (b) {
            for (const cx of [b.min.x, b.max.x]) for (const cy of [b.min.y, b.max.y]) for (const cz of [b.min.z, b.max.z]) {
              const p = apply(o.matrixWorld, [cx, cy, cz]);
              for (let k = 0; k < 3; k++) { if (p[k] < min[k]) min[k] = p[k]; if (p[k] > max[k]) max[k] = p[k]; }
            }
          }
        }
      });
    }
    return {
      autoImported: window.MODEL_AUTO_IMPORTED === true,
      filePickerCount: document.querySelectorAll('input[type=file]').length,
      statusText: (document.querySelector('#status') || {}).textContent,
      title: document.title,
      h1: (document.querySelector('h1') || {}).textContent,
      modelBytes: window.MODEL_BYTES ? window.MODEL_BYTES.length : 0,
      modelSha256: sha,
      meshes, vertices: verts, triangles: Math.round(tris),
      bbox: { min: min.map(v => +v.toFixed(4)), max: max.map(v => +v.toFixed(4)) },
      baseHref: (document.querySelector('base') || {}).href || null,
    };
  });

  // 四向全身图 + 双耳近景
  const views = [
    ['front', [0, .075, .30], [0, .075, 0]],
    ['back', [0, .075, -.30], [0, .075, 0]],
    ['left', [-.30, .075, 0], [0, .075, 0]],
    ['right', [.30, .075, 0], [0, .075, 0]],
    ['ear-left', [-.075, .092, .045], [-.016, .086, -.002]],
    ['ear-right', [.075, .092, .045], [.018, .086, -.002]],
    ['temple-left', [-.045, .088, .055], [-.010, .080, .010]],
    ['temple-right', [.045, .088, .055], [.014, .080, .010]],
  ];
  const shots = [];
  for (const [name, pos, tgt] of views) {
    await page.evaluate(([pos, tgt]) => {
      modelControls.autoRotate = false;
      modelCamera.up.set(0, 1, 0);
      modelControls.target.set(tgt[0], tgt[1], tgt[2]);
      modelCamera.position.set(pos[0], pos[1], pos[2]);
      modelControls.update();
    }, [pos, tgt]);
    await page.waitForTimeout(450);
    const path = `${prefix}-${name}.png`;
    await page.screenshot({ path, timeout: 120000 });
    shots.push(path);
  }

  // 解压字节与 GLB 文件逐字节比对
  const modelFile = process.argv[5] || target.replace(/[^\\/]+$/, '') + '小秦_v6右耳残留绒毛清理.glb';
  let glb = null;
  if (fs.existsSync(modelFile)) glb = crypto.createHash('sha256').update(fs.readFileSync(modelFile)).digest('hex');

  const report = {
    checkedAt: new Date().toISOString(),
    target,
    loadSeconds: +loadSeconds.toFixed(1),
    ...info,
    glbFileSha256: glb,
    losslessMatch: !!glb && glb === info.modelSha256,
    consoleErrors: consoleMsgs.filter(m => m.type === 'error'),
    consoleWarnings: consoleMsgs.filter(m => m.type === 'warning').slice(0, 10),
    pageErrors,
    failedRequests,
    screenshots: shots,
  };
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf8');
  console.log(JSON.stringify(report, null, 2));
  await browser.close();
})().catch(e => { console.error('CHECK_FAILED', e); process.exit(1); });
