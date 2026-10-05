const STATIC_CLOUD_ORIGINS=new Set([
 'https://beastboxcosmos.xyz',
 'https://www.beastboxcosmos.xyz',
 'http://127.0.0.1:3000',
 'http://localhost:3000',
]);

export function isTrustedCloudOrigin(origin){
 if(STATIC_CLOUD_ORIGINS.has(origin))return true;
 try{
  const url=new URL(origin);
  if(url.protocol!=='https:'||url.port||url.username||url.password)return false;
  return /^the-beast-box(?:-[a-z0-9-]+)?-zerefs-end\.vercel\.app$/i.test(url.hostname);
 }catch{return false;}
}
