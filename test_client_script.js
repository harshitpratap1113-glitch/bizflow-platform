const fs = require('fs');
const html = fs.readFileSync('static/index.html', 'utf8');

// Find all script tags
const scripts = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/gi);
console.log(`Found ${scripts ? scripts.length : 0} inline script tags.`);

if (scripts) {
  const mainScript = scripts[scripts.length - 1].replace(/<\/?script>/gi, '');
  
  // Create mock environment
  const mockDOM = {
    addEventListener: (ev, fn) => { if (ev === 'DOMContentLoaded') setTimeout(fn, 10); },
    getElementById: (id) => ({
      innerText: '',
      value: '0',
      style: {},
      classList: { add: ()=>{}, remove: ()=>{}, contains: ()=>false },
      innerHTML: '',
      dataset: {}
    }),
    querySelectorAll: (sel) => []
  };

  global.window = global;
  global.document = mockDOM;
  global.activePitchLeadId = null;
  global.AudioContext = class { createOscillator() { return { connect: ()=>{}, start: ()=>{}, stop: ()=>{} }; } createGain() { return { connect: ()=>{}, gain: { setValueAtTime: ()=>{}, exponentialRampToValueAtTime: ()=>{} } }; } };
  global.fetch = (url) => Promise.resolve({
    json: () => Promise.resolve({
      status: 'success',
      leads: [
        { id: 1, title: 'Need Next.js Dev', author: 'steve', community: 'forhire', intent_category: 'Tech & Dev', intent_score: 95 }
      ]
    })
  });

  try {
    eval(mainScript);
    console.log('✅ Main Script evaluated without errors!');
    loadLeads(false).then(() => {
      console.log('✅ loadLeads executed without errors! Lead count:', globalAllLeads.length);
    }).catch(e => {
      console.error('❌ loadLeads runtime error:', e);
    });
  } catch (err) {
    console.error('❌ Script evaluation error:', err);
  }
}
