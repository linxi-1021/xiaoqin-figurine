// v35 手部近景
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_鞋履收敛_v35_20261025/小秦_可旋转三维重建.html';
const views = [
  ['wave-front', [0.030, 0.068, 0.065], [0.024, 0.066, 0.018]],
  ['wave-34', [0.050, 0.072, 0.050], [0.024, 0.066, 0.018]],
  ['wave-side', [0.070, 0.066, 0.020], [0.024, 0.066, 0.018]],
  ['hang-front', [-0.020, 0.052, 0.070], [-0.014, 0.048, 0.020]],
  ['hang-34', [-0.050, 0.055, 0.045], [-0.014, 0.048, 0.020]],
];
(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--use-angle=d3d11', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
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
    await p.screenshot({ path: `v35-hand-${name}.png` });
    console.log('shot', name);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
