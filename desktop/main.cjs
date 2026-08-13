const { app, BrowserWindow, session, shell } = require('electron');
const path = require('node:path');

function createWindow(){
  const win = new BrowserWindow({
    width: 1440, height: 900, minWidth: 900, minHeight: 600,
    backgroundColor: '#020611', autoHideMenuBar: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false, sandbox: true }
  });
  win.loadFile(path.join(__dirname, '..', 'app', 'index.html'));
  win.webContents.setWindowOpenHandler(({url}) => { if(/^https?:/.test(url)) shell.openExternal(url); return {action:'deny'}; });
}

app.whenReady().then(()=>{
  session.defaultSession.setPermissionRequestHandler((_wc, permission, callback)=>{
    callback(['media','geolocation','notifications'].includes(permission));
  });
  createWindow();
  app.on('activate',()=>{ if(BrowserWindow.getAllWindows().length===0) createWindow(); });
});
app.on('window-all-closed',()=>{ if(process.platform!=='darwin') app.quit(); });
