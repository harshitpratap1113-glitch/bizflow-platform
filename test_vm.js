const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, 'backend', 'static', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const scriptMatches = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/gi);
let combinedJs = '';
scriptMatches.forEach(s => {
  combinedJs += s.replace(/<script[^>]*>|<\/script>/gi, '') + '\n';
});

const vm = require('vm');
const context = {
  tailwind: { config: {} },
  document: {
    getElementById: (id) => ({
      innerText: '', value: '0', style: {}, dataset: {}, classList: { add: ()=>{}, remove: ()=>{} },
      innerHTML: '', disabled: false
    }),
    querySelectorAll: () => [],
    addEventListener: (ev, cb) => cb(),
    createElement: () => ({ className: '', innerHTML: '', style: {}, remove: ()=>{} })
  },
  window: { leadsById: {}, generalById: {}, spamById: {}, AudioContext: null },
  navigator: { clipboard: { writeText: ()=>{} } },
  fetch: async () => ({ ok: true, json: async () => ({ status: 'success', leads: [{ id: 1, title: 'Test Lead', body: 'Test body', community: 'webdev', author: 'tester', intent_score: 95, budget_detected: '$5000', intent_category: 'Tech & Dev' }], general_leads: [{ id: 2, title: 'Test Discussion', body: 'Test body', community: 'webdev', author: 'tester2', intent_score: 60, intent_category: 'Tech & Dev' }], spam_leads: [] }) }),
  console: console,
  setTimeout: (cb) => cb(),
  setInterval: (cb) => 1,
  clearInterval: () => {}
};

try {
  vm.createContext(context);
  vm.runInContext(combinedJs, context);
  console.log('✅ VM EXECUTION PASSED! No ReferenceErrors or undefined variables found.');
} catch(e) {
  console.error('❌ VM EXECUTION ERROR:', e.message);
  console.error(e.stack);
}
