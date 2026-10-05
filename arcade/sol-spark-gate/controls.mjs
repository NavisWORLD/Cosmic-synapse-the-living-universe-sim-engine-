export const HANDHELD_INPUTS=Object.freeze({
 up:4,down:5,left:6,right:7,a:8,b:0,start:3,select:2,l:10,r:11,
});
export function normalizeHandheldInput(button,down){
 const key=String(button||'').toLowerCase();
 if(!Object.prototype.hasOwnProperty.call(HANDHELD_INPUTS,key)||typeof down!=='boolean')return null;
 return {button:key,index:HANDHELD_INPUTS[key],down};
}
export function applyHandheldInput(gameManager,button,down){
 const input=normalizeHandheldInput(button,down);
 if(!input||typeof gameManager?.simulateInput!=='function')return false;
 gameManager.simulateInput(0,input.index,input.down?1:0);
 return true;
}
