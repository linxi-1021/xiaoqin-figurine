// 通用打包：node pack_generic.cjs <dir> <glb> <title> <h1> <desc>
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const crypto = require('crypto');

const DIR = process.argv[2];
const GLB = path.join(DIR, process.argv[3]);
const TITLE = process.argv[4] || '小秦';
const H1 = process.argv[5] || '小秦';
const DESC = process.argv[6] || '打开页面后自动导入完整精度模型。';
const HTML = path.join(DIR, '小秦_可旋转三维重建.html');

const raw = fs.readFileSync(GLB);
const sha = crypto.createHash('sha256').update(raw).digest('hex');
const packed = zlib.gzipSync(raw, { level: 4 });
const folder = `自动加载数据_${sha.slice(0, 12)}`;
const dataDir = path.join(DIR, folder);
fs.mkdirSync(dataDir, { recursive: true });

const SIZE = 384 * 1024;
const total = Math.ceil(packed.length / SIZE);
for (let i = 0; i < total; i++) {
  const b64 = packed.subarray(i * SIZE, (i + 1) * SIZE).toString('base64');
  fs.writeFileSync(path.join(dataDir, String(i).padStart(4, '0') + '.js'),
    `window.MODEL_PARTS[${i}]=Uint8Array.from(atob("${b64}"),c=>c.charCodeAt(0));`, 'ascii');
}
const ok = crypto.createHash('sha256').update(zlib.gunzipSync(packed)).digest('hex') === sha;

let html = fs.readFileSync(HTML, 'utf8');
html = html.replace(/const total=\d+;/, `const total=${total};`);
html = html.replace(/自动加载数据_[0-9a-f]{12}\//, `${folder}/`);
html = html.replace(/<title>.*?<\/title>/, `<title>${TITLE}</title>`);
html = html.replace(/<h1>.*?<\/h1>/, `<h1>${H1}</h1>`);
html = html.replace(/<p>.*?<br>打开页面后自动导入完整精度模型。<\/p>/, `<p>${DESC}</p>`);
fs.writeFileSync(HTML, html, 'utf8');

fs.writeFileSync(path.join(DIR, '自动导入校验.json'), JSON.stringify({
  mode: 'automatic offline import', file_picker_required: false,
  data_parts: total, glb_sha256: sha, lossless_verified: ok,
}, null, 2), 'utf8');
console.log(JSON.stringify({ folder, total, sha: sha.slice(0, 12), lossless: ok }, null, 2));
