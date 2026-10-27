// v34 网页预览：鞋部近景
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_背包鞋镜框重建_v34_20261025/小秦_可旋转三维重建.html';
const views = [
  ['shoe-side', [0.115, 0.016, 0.008], [0, 0.0145, 0.002]],
  ['shoe-front', [0, 0.016, 0.105], [0, 0.0145, 0.002]],
  ['shoe-34', [0.055, 0.032, 0.070], [0, 0.0145, 0.002]],
];
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--use-angle=d3d11', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1100, height: 1100 } });
  await p.goto(pathToFileURL(HTML).href, { waitUntil: 'commit' });
  await p.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true && window.pet, { timeout: 240000 });
  await p.waitForTimeout(1500);
  for (const [name, pos, tgt] of views) {
    await p.evaluate(([pos, tgt]) => {
      modelControls.autoRotate = false; modelCamera.up.set(0, 1, 0);
      modelControls.target.set(tgt[0], tgt[1], tgt[2]);
      modelCamera.position.set(pos[0], pos[1], pos[2]);
      modelControls.update();
    }, [pos, tgt]);
    await p.waitForTimeout(400);
    await p.screenshot({ path: `v34-${name}.png` });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
