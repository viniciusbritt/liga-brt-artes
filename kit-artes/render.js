// node render.js pagina.html saida_base sel1,sel2,... [transparente=0|1]
// Abre o HTML, espera document.title=='ok' e salva um PNG por seletor: <saida_base>-<n>.png (ou <saida_base>.png se for só 1)
const { chromium } = require('playwright');
(async () => {
  const [html, base, sels, transp] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2200, height: 2200 }, deviceScaleFactor: 1 });
  await p.goto('file://' + require('path').resolve(html));
  await p.waitForFunction(() => document.title === 'ok', null, { timeout: 60000 });
  const list = sels.split(',');
  for (let i = 0; i < list.length; i++) {
    const out = list.length === 1 ? base + '.png' : `${base}-${i + 1}.png`;
    await p.locator(list[i]).screenshot({ path: out, omitBackground: transp === '1' });
    console.log(out);
  }
  await b.close();
})();
