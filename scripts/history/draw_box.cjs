// 在预览页上叠加一个 3D 线框（视口坐标，输入为 mm），用于核对切割区域
// node draw_box.cjs x0 x1 y0 y1 z0 z1 out.png
const { chromium } = require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const { pathToFileURL } = require('url');
const HTML = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_鞋履收敛_v35_20261025/小秦_可旋转三维重建.html';

const [x0, x1, y0, y1, z0, z1] = process.argv.slice(2, 8).map(Number);
const out = process.argv[8] || 'box.png';

(async () => {
  const b = await chromium.launch({ executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true, args: ['--use-angle=d3d11', '--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1000, height: 1000 } });
  await p.goto(pathToFileURL(HTML).href, { waitUntil: 'commit' });
  await p.waitForFunction(() => window.MODEL_AUTO_IMPORTED === true && window.pet, { timeout: 240000 });
  await p.waitForTimeout(3500);
  await p.evaluate(() => {
    modelControls.autoRotate = false;
    modelCamera.up.set(0, 1, 0);
    modelControls.target.set(0.024, 0.066, 0.018);
    modelCamera.position.set(0.030, 0.068, 0.065);
    modelControls.update();
    modelCamera.updateMatrixWorld(true);
  });
  await p.waitForTimeout(600);
  await p.evaluate(([x0, x1, y0, y1, z0, z1]) => {
    const mm = v => v / 1000;
    const pts = [];
    for (const x of [x0, x1]) for (const y of [y0, y1]) for (const z of [z0, z1]) {
      const v = modelCamera.position.clone().set(mm(x), mm(y), mm(z));
      v.project(modelCamera);
      pts.push([(v.x * 0.5 + 0.5) * innerWidth, (-v.y * 0.5 + 0.5) * innerHeight]);
    }
    const edges = [[0,1],[0,2],[0,4],[1,3],[1,5],[2,3],[2,6],[3,7],[4,5],[4,6],[5,7],[6,7]];
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', innerWidth); svg.setAttribute('height', innerHeight);
    svg.style.cssText = 'position:fixed;left:0;top:0;pointer-events:none;z-index:9999';
    for (const [a, c] of edges) {
      const l = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      l.setAttribute('x1', pts[a][0]); l.setAttribute('y1', pts[a][1]);
      l.setAttribute('x2', pts[c][0]); l.setAttribute('y2', pts[c][1]);
      l.setAttribute('stroke', '#ff3b30'); l.setAttribute('stroke-width', '2');
      svg.appendChild(l);
    }
    document.body.appendChild(svg);
  }, [x0, x1, y0, y1, z0, z1]);
  await p.waitForTimeout(300);
  await p.screenshot({ path: out });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
