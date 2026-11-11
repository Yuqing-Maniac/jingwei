/* 界面皮肤独立于图面主题，避免改变导出颜色。 */
var JW_SKINS = { light: '经典蓝', jade: '青竹', paper: '暖纸', dark: '深空' };
function jwSetSkin(key) {
  if (!Object.prototype.hasOwnProperty.call(JW_SKINS, key)) key = 'light';
  document.documentElement.setAttribute('data-theme', key);
  try { localStorage.setItem('hongtu.uiSkin', key); } catch (_) { }
  document.querySelectorAll('.jw-skin-select').forEach(function (el) { el.value = key; });
}
function jwSkinSelect() {
  var el = document.createElement('select');
  el.className = 'jw-skin-select';
  el.title = '界面皮肤（不改变图面和导出配色）';
  el.setAttribute('aria-label', '界面皮肤');
  Object.keys(JW_SKINS).forEach(function (key) {
    var opt = document.createElement('option'); opt.value = key; opt.textContent = JW_SKINS[key]; el.appendChild(opt);
  });
  el.value = document.documentElement.getAttribute('data-theme') || 'light';
  el.onchange = function () { jwSetSkin(el.value); };
  return el;
}
document.querySelector('#b-help').before(jwSkinSelect());
