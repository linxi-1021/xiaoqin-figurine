// 检查打开入口后的默认视角（不手动设置相机），确认不是耳部特写
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
(async () => {
  const b = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
    args: ['--use-angle=d3d11', '--allow-file-access-from-files'],
  });
  const p = await b.newPage({ viewport: { width: 1200, height: 900 } });
  const errs = [];
  p.on('pageerror', e => errs.push(String(e.message)));
  await p.goto(pathToFileURL('D:/Desktop/相册/二维IP制作_20261012/手办设计/小秦_最新三维预览.html').href, { waitUntil: 'commit' });
  await p.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true && window.pet, { timeout: 240000 });
  await p.waitForTimeout(4000);
  const state = await p.evaluate(() => ({
    camera: modelCamera.position.toArray().map(v => +v.toFixed(4)),
    target: modelControls.target.toArray().map(v => +v.toFixed(4)),
    autoRotate: modelControls.autoRotate,
    status: document.querySelector('#status').textContent,
    buttons: [...document.querySelectorAll('button')].map(b => b.textContent),
  }));
  console.log(JSON.stringify({ ...state, pageErrors: errs }, null, 2));
  await p.screenshot({ path: 'entry-default-view.png' });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
