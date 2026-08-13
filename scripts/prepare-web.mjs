import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const source = path.join(root, 'standalone', 'SIM_EARTH_7_07_ALIEN_CONTROL_CENTER.html');
const outDir = path.join(root, 'app');
const target = path.join(outDir, 'index.html');
if (!fs.existsSync(source)) throw new Error(`Missing canonical engine: ${source}`);
fs.mkdirSync(outDir, { recursive: true });
let html = fs.readFileSync(source, 'utf8');
const head = `
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#020611">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="SIM EARTH 7.07">
`;
const boot = `
<script>if('serviceWorker' in navigator){addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(console.warn));}</script>
`;
html = html.replace('</head>', `${head}</head>`).replace('</body>', `${boot}</body>`);
fs.writeFileSync(target, html);
console.log(`Prepared ${target} from canonical standalone engine.`);
