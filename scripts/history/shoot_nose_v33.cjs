// 补充：帽面熊鼻与帽檐的超近景
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/小秦_最新三维预览.html';
const views = [
  ['nose', [0, .103, .058], [0, .101, .022]],
  ['brim-low', [0, .092, .070], [0, .097, .018]],
  ['muzzle-side', [.028, .103, .052], [.004, .100, .020]],
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
    await p.screenshot({ path: `cmp-v33-${name}.png` });
    console.log('shot', name);
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
