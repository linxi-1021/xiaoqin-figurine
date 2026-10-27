// 鞋子重建前：俯视/正面/侧面量形
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/小秦_最新三维预览.html';
const views = [
  ['feet-top', [0, .060, .010], [0, .012, .002]],
  ['feet-front', [0, .014, .095], [0, .014, .002]],
  ['feet-side', [.090, .014, .008], [0, .014, .004]],
  ['feet-34', [.045, .030, .055], [0, .013, .004]],
];
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--use-angle=d3d11', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  await p.goto(pathToFileURL(HTML).href, { waitUntil: 'commit' });
  await p.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true && window.pet, { timeout: 240000 });
  await p.waitForTimeout(1200);
  for (const [name, pos, tgt] of views) {
    await p.evaluate(([pos, tgt]) => {
      modelControls.autoRotate = false; modelCamera.up.set(0, 1, 0);
      modelControls.target.set(tgt[0], tgt[1], tgt[2]);
      modelCamera.position.set(pos[0], pos[1], pos[2]);
      modelControls.update();
    }, [pos, tgt]);
    await p.waitForTimeout(400);
    await p.screenshot({ path: `feet-before-${name}.png` });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
