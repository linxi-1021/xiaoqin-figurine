// 按参考图集部位拍模型近景，用于逐项对照
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');

const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/小秦_最新三维预览.html';
const views = [
  ['hat-front', [0, .104, .105], [0, .104, .015]],
  ['hat-brim', [0, .098, .075], [0, .094, .020]],
  ['face', [0, .086, .095], [0, .086, .015]],
  ['bow-back', [0, .100, -.105], [0, .100, -.020]],
  ['body', [0, .055, .115], [0, .050, .010]],
  ['hand-left', [.028, .068, .060], [.024, .066, .018]],
  ['skirt', [0, .040, .100], [0, .038, .005]],
  ['shoes', [0, .016, .090], [0, .012, .004]],
  ['ear-right-side', [.075, .098, .030], [.020, .095, -.005]],
  ['back-hair', [0, .060, -.110], [0, .058, -.010]],
];

(async () => {
  const b = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
    args: ['--use-angle=d3d11', '--allow-file-access-from-files'],
  });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  await p.goto(pathToFileURL(HTML).href, { waitUntil: 'commit' });
  await p.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true && window.pet, { timeout: 240000 });
  await p.waitForTimeout(1500);
  for (const [name, pos, tgt] of views) {
    await p.evaluate(([pos, tgt]) => {
      modelControls.autoRotate = false;
      modelCamera.up.set(0, 1, 0);
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
