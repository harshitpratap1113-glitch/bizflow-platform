const fs = require('fs');
const path = require('path');
const http = require('https');

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, { headers: { 'User-Agent': 'BizFlowSim/2.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch(e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function runSimulation() {
  console.log('🚀 SIMULATING USER INTERACTION ON BIZFLOW LIVE UI...\n');
  
  const verifiedData = await fetchJson('https://bizflow-platform.vercel.app/api/leadradar/leads/matched');
  const generalData = await fetchJson('https://bizflow-platform.vercel.app/api/leadradar/general');
  const spamData = await fetchJson('https://bizflow-platform.vercel.app/api/leadradar/spam');
  
  const globalAllLeads = verifiedData.leads || [];
  const globalGeneralLeads = generalData.general_leads || [];
  const spamLeads = spamData.spam_leads || [];

  console.log(`[✓] Fetched from Live Server -> Verified: ${globalAllLeads.length}, General: ${globalGeneralLeads.length}, Spam: ${spamLeads.length}\n`);

  const fields = [
    'all',
    'Tech & Dev',
    'AI & Automation',
    'Design & Creative',
    'Video & Content',
    'Marketing & SEO',
    'E-Commerce & Retail',
    'Startups & SaaS',
    'Mobile Apps',
    'DevOps & Cloud',
    'Local Biz & Finance'
  ];

  const COMMUNITY_FIELD_MAP = {
    'webdev': 'Tech & Dev', 'javascript': 'Tech & Dev', 'reactjs': 'Tech & Dev', 'nextjs': 'Tech & Dev',
    'python': 'Tech & Dev', 'node': 'Tech & Dev', 'fastapi': 'Tech & Dev', 'django': 'Tech & Dev',
    'vuejs': 'Tech & Dev', 'golang': 'Tech & Dev', 'rust': 'Tech & Dev', 'programming': 'Tech & Dev',
    'frontend': 'Tech & Dev', 'fullstack': 'Tech & Dev', 'hackernews': 'Tech & Dev', 'devto': 'Tech & Dev',
    
    'openai': 'AI & Automation', 'chatgpt': 'AI & Automation', 'artificialinteligence': 'AI & Automation',
    'machinelearning': 'AI & Automation', 'localllama': 'AI & Automation', 'langchain': 'AI & Automation',
    'automate': 'AI & Automation', 'n8n': 'AI & Automation', 'zapier': 'AI & Automation',
    'claudeai': 'AI & Automation', 'promptengineering': 'AI & Automation',
    
    'designjobs': 'Design & Creative', 'graphic_design': 'Design & Creative', 'ui_design': 'Design & Creative',
    'artstore': 'Design & Creative', 'hungryartists': 'Design & Creative', '3dmodeling': 'Design & Creative',
    'blender': 'Design & Creative', 'motiondesign': 'Design & Creative', 'logodesign': 'Design & Creative',
    
    'videography': 'Video & Content', 'videoediting': 'Video & Content', 'aftereffects': 'Video & Content',
    'creatorservices': 'Video & Content', 'youtube_startups': 'Video & Content', 'premiere': 'Video & Content',
    
    'marketing': 'Marketing & SEO', 'seo': 'Marketing & SEO', 'digitalmarketing': 'Marketing & SEO',
    'ppc': 'Marketing & SEO', 'socialmediamarketing': 'Marketing & SEO', 'copywriting': 'Marketing & SEO',
    'content_marketing': 'Marketing & SEO', 'growthhacking': 'Marketing & SEO',
    
    'ecommerce': 'E-Commerce & Retail', 'shopify': 'E-Commerce & Retail', 'dropship': 'E-Commerce & Retail',
    'amazonseller': 'E-Commerce & Retail', 'fulfillmentbyamazon': 'E-Commerce & Retail',
    
    'saas': 'Startups & SaaS', 'startups': 'Startups & SaaS', 'entrepreneur': 'Startups & SaaS',
    'sideproject': 'Startups & SaaS', 'indiebiz': 'Startups & SaaS', 'indiehackers': 'Startups & SaaS',
    
    'flutterdev': 'Mobile Apps', 'flutterhelp': 'Mobile Apps', 'reactnative': 'Mobile Apps',
    'iosprogramming': 'Mobile Apps', 'androiddev': 'Mobile Apps', 'swift': 'Mobile Apps', 'kotlin': 'Mobile Apps',
    
    'devops': 'DevOps & Cloud', 'aws': 'DevOps & Cloud', 'docker': 'DevOps & Cloud',
    'kubernetes': 'DevOps & Cloud', 'sysadmin': 'DevOps & Cloud', 'selfhosted': 'DevOps & Cloud',
    
    'accounting': 'Local Biz & Finance', 'bookkeeping': 'Local Biz & Finance', 'realestate': 'Local Biz & Finance',
    'realtors': 'Local Biz & Finance', 'restaurateur': 'Local Biz & Finance', 'smallbusiness': 'Local Biz & Finance',
    'dentistry': 'Local Biz & Finance', 'fitnessbusiness': 'Local Biz & Finance', 'consulting': 'Local Biz & Finance',
    'sales': 'Local Biz & Finance',
    
    'forhire': 'Tech & Dev', 'freelance': 'Tech & Dev', 'freelance_forhire': 'Tech & Dev', 'jobbit': 'Tech & Dev'
  };

  function filterList(list, selectedField) {
    if (selectedField === 'all') return list;
    const tf = selectedField.toLowerCase();
    return list.filter(l => {
      const cat = (l.intent_category || '').toLowerCase();
      const tags = (l.niche_tags || '').toLowerCase();
      const comm = (l.community || '').toLowerCase();
      const mapped = (COMMUNITY_FIELD_MAP[comm] || '').toLowerCase();
      
      if (cat === tf || mapped === tf || cat.includes(tf) || tags.includes(tf) || mapped.includes(tf)) {
        return true;
      }
      if (tf.includes('dev') && (cat.includes('dev') || comm.includes('dev') || comm.includes('web') || comm.includes('react') || comm.includes('python') || comm.includes('node') || comm.includes('rust') || comm.includes('hackernews'))) return true;
      if (tf.includes('video') && (cat.includes('video') || comm.includes('video') || comm.includes('film') || comm.includes('edit') || comm.includes('creator') || comm.includes('aftereffects'))) return true;
      if (tf.includes('design') && (cat.includes('design') || comm.includes('design') || comm.includes('art') || comm.includes('blender') || comm.includes('ui') || comm.includes('logo'))) return true;
      if (tf.includes('ai') && (cat.includes('ai') || comm.includes('ai') || comm.includes('gpt') || comm.includes('llama') || comm.includes('automate') || comm.includes('n8n') || comm.includes('machine'))) return true;
      if (tf.includes('marketing') && (cat.includes('marketing') || comm.includes('market') || comm.includes('seo') || comm.includes('copy') || comm.includes('ppc'))) return true;
      if (tf.includes('e-commerce') && (cat.includes('e-commerce') || comm.includes('ecom') || comm.includes('shop') || comm.includes('amazon') || comm.includes('dropship'))) return true;
      if (tf.includes('saas') && (cat.includes('saas') || comm.includes('saas') || comm.includes('startup') || comm.includes('entrepreneur') || comm.includes('sideproject') || comm.includes('indie'))) return true;
      if (tf.includes('mobile') && (cat.includes('mobile') || comm.includes('flutter') || comm.includes('ios') || comm.includes('android') || comm.includes('swift') || comm.includes('kotlin') || comm.includes('reactnative'))) return true;
      if (tf.includes('cloud') && (cat.includes('cloud') || comm.includes('aws') || comm.includes('docker') || comm.includes('devops') || comm.includes('kube') || comm.includes('sysadmin'))) return true;
      if (tf.includes('local') && (cat.includes('local') || comm.includes('business') || comm.includes('account') || comm.includes('estate') || comm.includes('bookkeeping') || comm.includes('smallbusiness'))) return true;
      return false;
    });
  }

  console.log('--- TESTING EVERY FIELD FILTER IN BOX 1 (VERIFIED LEADS) ---');
  for (const f of fields) {
    const res = filterList(globalAllLeads, f);
    console.log(`  • Field [${f}]: ${res.length} leads visible ${res.length > 0 ? '✅' : '❌ EMPTY'}`);
  }

  console.log('\n--- TESTING EVERY FIELD FILTER IN BOX 2 (CASUAL DISCUSSIONS) ---');
  for (const f of fields) {
    const res = filterList(globalGeneralLeads, f);
    console.log(`  • Field [${f}]: ${res.length} discussions visible ${res.length > 0 ? '✅' : '❌ EMPTY'}`);
  }
}

runSimulation();
