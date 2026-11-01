'use strict';
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('jwDesk', {
  save: (name, data, opt) => ipcRenderer.invoke('jw:save', Object.assign({ name, data }, opt || {})),
  pickDir: title => ipcRenderer.invoke('jw:pick-dir', title),
  writeIn: (dir, name, data) => ipcRenderer.invoke('jw:write-in', { dir, name, data }),
  read: p => ipcRenderer.invoke('jw:read', p),
  openDialog: () => ipcRenderer.invoke('jw:open-dialog'),
  recent: () => ipcRenderer.invoke('jw:recent'),
  recentRemove: p => ipcRenderer.invoke('jw:recent-remove', p),
  pending: () => ipcRenderer.invoke('jw:pending'),
  info: () => ipcRenderer.invoke('jw:info'),
  confirmClose: name => ipcRenderer.invoke('jw:confirm-close', name),
  closeNow: () => ipcRenderer.send('jw:close-now'),
  win: op => ipcRenderer.send('jw:win', op),
  title: t => ipcRenderer.send('jw:title', t),
  reveal: p => ipcRenderer.send('jw:reveal', p),
  on: (ch, fn) => { const ok = ['jw:open-path', 'jw:win-state', 'jw:before-close']; if (ok.includes(ch)) ipcRenderer.on(ch, (_e, d) => fn(d)); },
});
