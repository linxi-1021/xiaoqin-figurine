// 打包 v34：glb -> 分块 gzip 数据 + 预览页 + 校验 JSON
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const crypto = require('crypto');

const DIR = 'D:/Desktop/相册/二维IP制作_20261012/手办设计/3D重建_v6基础_背包鞋镜框重建_v34_20261025';
const GLB = path.join(DIR, '小秦_v6背包鞋镜框重建.glb');
const HTML = path.join(DIR, '小秦_可旋转三维重建.html');
const TITLE = '小秦 · 背包/鞋/镜框重建 v34';
const H1 = '小秦 · 背包与鞋履重建 v34';
const DESC = '加厚分层鞋底、两条搭带与扣片；帽绒、头发、底座与刻字保持不变。<br>打开页面后自动导入完整精度模型。';

const raw = fs.readFileSync(GLB);
const sha = crypto.createHash('sha256').update(raw).digest('hex');
const packed = zlib.gzipSync(raw, { level: 4 });
const folder = `自动加载数据_${sha.slice(0, 12)}`;
const dir = path.join(DIR, folder);
fs.mkdirSync(dir, { recursive: true });

const SIZE = 384 * 1024;
const total = Math.ceil(packed.length / SIZE);
for (let i = 0; i < total; i++) {
  const b64 = packed.subarray(i * SIZE, (i + 1) * SIZE).toString('base64');
  const code = `window.MODEL_PARTS[${i}]=Uint8Array.from(atob("${b64}"),c=>c.charCodeAt(0));`;
  fs.writeFileSync(path.join(dir, String(i).padStart(4, '0') + '.js'), code, 'ascii');
}

// 校对无损
const back = zlib.gunzipSync(packed);
const ok = crypto.createHash('sha256').update(back).digest('hex') === sha;

let html = fs.readFileSync(HTML, 'utf8');
const before = html;
html = html.replace(/const total=\d+;/, `const total=${total};`);
html = html.replace(/自动加载数据_[0-9a-f]{12}\//, `${folder}/`);
html = html.replace(/<title>.*?<\/title>/, `<title>${TITLE}</title>`);
html = html.replace(/<h1>.*?<\/h1>/, `<h1>${H1}</h1>`);
html = html.replace(/<p>.*?<br>打开页面后自动导入完整精度模型。<\/p>/, `<p>${DESC}</p>`);
if (html === before) throw new Error('HTML 未被修改，检查替换规则');

fs.writeFileSync(HTML, html, 'utf8');
fs.writeFileSync(path.join(DIR, '自动导入校验.json'), JSON.stringify({
  mode: 'automatic offline import',
  file_picker_required: false,
  data_parts: total,
  glb_sha256: sha,
  lossless_verified: ok,
}, null, 2), 'utf8');

console.log(JSON.stringify({ folder, total, sha, lossless: ok, glbBytes: raw.length }, null, 2));
