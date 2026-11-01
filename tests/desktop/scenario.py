pg.call('Emulation.setEmulatedMedia', features=[{'name': 'prefers-color-scheme', 'value': 'dark'}]); time.sleep(0.5)
print('ver', pg.js("document.querySelector('#jw-ver').textContent.slice(0,16)"), pg.js("[getComputedStyle(document.querySelector('#props')).backgroundColor, getComputedStyle(document.querySelector('.pitem')).color]"))
