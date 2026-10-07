const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, 'backend', 'static', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

const scriptMatches = html.match(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/gi);
if (scriptMatches) {
  scriptMatches.forEach((s, idx) => {
    const code = s.replace(/<script[^>]*>|<\/script>/gi, '');
    try {
      new Function(code);
      console.log(`Script block ${idx}: VALID JAVASCRIPT ✓`);
    } catch(e) {
      console.error(`Script block ${idx} SYNTAX ERROR: ${e.message}`);
      // Find line number
      console.error(e.stack);
    }
  });
}
