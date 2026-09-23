/* Refresh public GitHub Pages from the author's published content without write access. */
const upstream='https://yiqing-personal-journal.gottenelm.chatgpt.site';
const path=location.pathname.endsWith('/')?location.pathname:location.pathname+'/';
function rewriteAssets(document){
 for(const node of document.querySelectorAll('link[href],script[src],img[src],source[src],video[src]')){
  const attr=node.hasAttribute('href')?'href':'src',value=node.getAttribute(attr);
  if(value&&!/^(?:https?:|data:)/.test(value))node.setAttribute(attr,new URL(value,upstream+path).href);
 }
 for(const link of document.querySelectorAll('a[href]')){
  const value=link.getAttribute('href');
  if(value?.startsWith('/studio/')||value?.startsWith('/media/')||/\.(?:jpe?g|png|webp|gif|svg|mp4)$/i.test(value||''))link.href=upstream+value;
 }
}
try{
 const response=await fetch(upstream+'/api/public-page?path='+encodeURIComponent(path),{cache:'no-store'});
 if(response.ok){
  const next=new DOMParser().parseFromString(await response.text(),'text/html');
  rewriteAssets(next);
  document.replaceChild(document.importNode(next.documentElement,true),document.documentElement);
 }else if(response.status===404){
  document.title='页面暂未公开';
  document.body.innerHTML='<main style="max-width:42rem;margin:15vh auto;padding:2rem;font:1.1rem/1.7 system-ui,sans-serif"><h1>页面暂未公开</h1><p>这篇内容尚未发布，或已被作者移除。</p><p><a href="/">返回首页</a></p></main>';
 }
}catch(error){console.warn('Latest journal content is temporarily unavailable; showing the saved page.',error);}
