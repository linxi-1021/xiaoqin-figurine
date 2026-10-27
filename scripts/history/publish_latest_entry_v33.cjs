// 更新固定最新入口：小秦_最新三维预览.html -> v33
// 只改入口文件：注入 <base> 指向 v33 目录，并修正标题文案；v33 版本目录本身不动。
const fs = require('fs');
const path = require('path');

const ROOT = 'D:/Desktop/相册/二维IP制作_20261012/手办设计';
const VERSION_DIR = '3D重建_v6基础_右耳残留绒毛清理_v33_20261025';
const SRC = path.join(ROOT, VERSION_DIR, '小秦_可旋转三维重建.html');
const ENTRY = path.join(ROOT, '小秦_最新三维预览.html');
const BACKUP = path.join(ROOT, '3D重建_v6基础_二维码紧凑留白_v24_20261021', '过程备份', '小秦_最新三维预览_v24_20261021.html');
const REF_IMAGE = '../3D重建_v6基础_后帽粗绒浮贴蝴蝶结_v4_20261020/hat-reference.png';

let html = fs.readFileSync(SRC, 'utf8');
if (!html.includes('<meta charset="utf-8">')) throw new Error('源文件缺少 charset 标记，停止');

// 备份当前入口（若与已存在备份内容相同则跳过）
const old = fs.existsSync(ENTRY) ? fs.readFileSync(ENTRY, 'utf8') : null;
if (old) {
  fs.mkdirSync(path.dirname(BACKUP), { recursive: true });
  if (!fs.existsSync(BACKUP) || fs.readFileSync(BACKUP, 'utf8') !== old) fs.writeFileSync(BACKUP, old, 'utf8');
}

// 1) 注入 base，指向 v33 目录，避免相对路径落到手办设计根目录
const baseTag = `<base href="${encodeURI(VERSION_DIR + '/')}">`;
if (!html.includes('<base ')) {
  html = html.replace('<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">' + baseTag);
}
if (!html.includes(baseTag)) throw new Error('base 注入失败');

// 2) 修正页面文案（原模板误留 v31/v4）
html = html.replace(/<title>.*?<\/title>/, '<title>小秦 · 右耳残留绒毛清理 v33（最新）</title>');
html = html.replace(/<h1>.*?<\/h1>/, '<h1>小秦 · 右耳残留绒毛清理 v33</h1>');
html = html.replace(/<p>实心短绒线簇.*?<\/p>/,
  '<p>清理右耳旁越界绒线，帽绒造型、材质与其余细节保持不变。<br>打开页面后自动导入完整精度模型。</p>');

// 3) 帽子参考图链接改到实际存在的位置（base 之后相对路径会落到 v33 目录）
html = html.replace('href="hat-reference.png"', `href="${encodeURI(REF_IMAGE)}"`);

if (!html.includes('自动加载数据_')) throw new Error('入口未包含自动加载数据引用');
if (html.includes('input type="file"') || html.includes("input type='file'")) throw new Error('入口出现了文件选择器');

fs.writeFileSync(ENTRY, html, 'utf8');
console.log(JSON.stringify({
  entry: ENTRY,
  versionDir: VERSION_DIR,
  bytes: Buffer.byteLength(html, 'utf8'),
  base: baseTag,
  backup: BACKUP,
  title: (html.match(/<title>(.*?)<\/title>/) || [])[1],
}, null, 2));
