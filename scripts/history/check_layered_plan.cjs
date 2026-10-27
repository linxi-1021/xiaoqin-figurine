const {chromium}=require('C:/Users/ASUS/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs=require('fs');
const ctx=JSON.parse(fs.readFileSync('models/rebuild/layered-planning-context.json','utf8'));
const path=require('path');
const info=JSON.parse(fs.readFileSync(path.join(ctx.session_dir,'state/server-info'),'utf8'));
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1380,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(info.url);await page.waitForFunction(()=>document.querySelectorAll('.ref').length===65);
 const allImages=await page.evaluate(async()=>{const urls=[...document.querySelectorAll('img')].map(x=>x.src).filter(Boolean);return await Promise.all(urls.map(src=>new Promise(resolve=>{const im=new Image();im.onload=()=>resolve({src,ok:true});im.onerror=()=>resolve({src,ok:false});im.src=src}))) });
 await page.locator('#stages button').nth(7).click();if(await page.locator('#stage-name').textContent()!=='最后装配斜挎包')throw Error('Stage failed');
 await page.locator('#stage-refs button').first().click();await page.locator('#modal[open]').waitFor();const modal=await page.locator('#modal-title').textContent();await page.locator('#modal .close').click();
 await page.locator('#hide-bag').click();if(await page.locator('#diagram-bag').evaluate(e=>e.style.opacity)!=='0')throw Error('Layer toggle failed');await page.locator('#hide-bag').click();
 await page.locator('#filters button').nth(8).click();const bagRefs=await page.locator('.ref').count();if(bagRefs!==8)throw Error('Reference filter failed: '+bagRefs);await page.locator('#filters button').first().click();
 await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(ctx.planning_folder,'规划页检查.png')});
 await page.setViewportSize({width:420,height:900});await page.waitForTimeout(150);const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2);
 const result={title:await page.title(),refs:await page.locator('.ref').count(),images:allImages.length,imageFailures:allImages.filter(x=>!x.ok),stage7:true,bagRefs,modal,layerToggle:true,mobileOverflow:overflow,errors};
 fs.writeFileSync(path.join(ctx.planning_folder,'规划页验证.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();if(errors.length||result.imageFailures.length||overflow)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
