import sqlite3
import os
import sys

sys.path.insert(0, os.path.abspath("backend"))
from app.db.database import get_db, init_db

init_db()
conn = get_db()
cursor = conn.cursor()

# 10 Industries Real-World Verified Buyer Leads (Box 1) + Casual Stream Discussions (Box 2)
ALL_SEED_DATA = [
    # =========================================================================
    # --- 1. DESIGN, UI/UX, 3D & CREATIVE ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-des-001", "DesignJobs",
     "[Hiring] Need senior UI/UX designer to redesign our B2B fintech dashboard in Figma ($3,500)",
     "Looking for an experienced product designer to build a modern dark-mode design system with 20+ responsive screens. Must have prior fintech/SaaS portfolio. Fixed budget $3,500.",
     "FintechProductLead", "https://www.reddit.com/r/DesignJobs/new/", 98, "Design & Creative",
     "ui/ux, figma, design system, fintech, budget", "design,agency", "$3,500 Fixed", "verified", 0, None, 0),

    ("reddit", "lead-des-002", "graphic_design",
     "Looking for a 3D Blender artist to create 10 product render animations for our hardware launch ($2,500)",
     "We are launching an ergonomic mechanical keyboard. Need photorealistic 3D renders and 3 short 360-degree looping video animations. Budget $2,500.",
     "HardwareFounderRay", "https://www.reddit.com/r/graphic_design/new/", 96, "Design & Creative",
     "3d blender, animation, renders, budget", "design,3d", "$2,500 Budget", "verified", 0, None, 0),

    ("reddit", "lead-des-003", "UI_Design",
     "Hiring Landing Page Designer for high-converting Webflow SaaS page ($1,800)",
     "Need a conversion-focused landing page designer. Figma wireframes + responsive desktop/mobile designs required. Ready to hire this week.",
     "SaaSMarketerSam", "https://www.reddit.com/r/UI_Design/new/", 95, "Design & Creative",
     "landing page, webflow, figma, budget", "design", "$1,800", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-des-001", "graphic_design",
     "How do you handle clients who keep asking for 'just one more quick tweak' after final sign-off?",
     "I have a client on a fixed identity project who approved the final brand guidelines last week, but is now emailing daily for small icon adjustments. How do you draw the line politely?",
     "PixelCrafter_99", "https://www.reddit.com/r/graphic_design/new/", 62, "Design & Creative",
     "scope creep, client management, contracts", "design,advice", None, "general", 0, None, 0),

    ("reddit", "disc-des-002", "UI_Design",
     "Is anyone else finding Figma's new Auto-Layout updates much smoother for complex responsive tables?",
     "Been playing around with min/max widths and wrapped flex containers for B2B data grids. The handoff to React developers is finally 1:1 without manual explanations.",
     "UX_ArchitectDan", "https://www.reddit.com/r/UI_Design/new/", 58, "Design & Creative",
     "figma, auto-layout, design tokens, frontend handoff", "design,tools", None, "general", 0, None, 0),

    ("reddit", "disc-des-003", "blender",
     "Geometry Nodes vs procedural shaders for animated UI backgrounds — which is lighter for web exports?",
     "Building some looping 3D hero assets for a WebGL site. Trying to keep the GLTF file size under 1.5MB while maintaining smooth specular lighting.",
     "3DMotionGuy", "https://www.reddit.com/r/blender/new/", 64, "Design & Creative",
     "blender, webgl, 3d assets, performance", "design,3d", None, "general", 0, None, 0),

    # =========================================================================
    # --- 2. VIDEO EDITING & CONTENT CREATORS ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-vid-001", "CreatorServices",
     "[Hiring] Long-term YouTube video editor for 400k tech channel (Budget $250 - $400 per video)",
     "Looking for an experienced Premiere Pro / After Effects editor who understands high retention pacing, sound design, and custom motion graphics. 2 videos per week.",
     "TechChannelHost", "https://www.reddit.com/r/CreatorServices/new/", 97, "Video & Content",
     "youtube editor, premiere, after effects, sound design, per video", "video,creator", "$250 - $400 / Video", "verified", 0, None, 0),

    ("reddit", "lead-vid-002", "videography",
     "Need someone to edit 30 short-form viral TikTok / Reels from our podcast episodes ($1,500/mo)",
     "We host a weekly founder podcast. Looking for an editor to pull out top 30 hooks, add dynamic captions, b-roll, and sound effects monthly. Monthly retainer $1,500.",
     "FounderPodcastNet", "https://www.reddit.com/r/videography/new/", 96, "Video & Content",
     "reels, tiktok, podcast editor, captions, monthly retainer", "video,reels", "$1,500 / Month", "verified", 0, None, 0),

    ("reddit", "lead-vid-003", "VideoEditing",
     "[Hiring] Motion graphics artist to create 60-second 2D SaaS explainer video ($2,000)",
     "We have the voiceover and script ready. Need custom 2D vector animation in After Effects to explain our cloud backup tool. Turnaround 2 weeks.",
     "CloudBackupSaaS", "https://www.reddit.com/r/VideoEditing/new/", 95, "Video & Content",
     "motion graphics, explainer video, after effects, budget", "video,anim", "$2,000 Fixed", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-vid-001", "VideoEditing",
     "DaVinci Resolve 19 vs Premiere Pro for collaborative agency timeline editing — what's your verdict in 2026?",
     "Our studio is debating migrating completely away from Adobe Creative Cloud to DaVinci Studio with Blackmagic Cloud Project Server. Any horror stories or huge wins?",
     "CutterStudioLead", "https://www.reddit.com/r/VideoEditing/new/", 67, "Video & Content",
     "davinci resolve, premiere pro, agency workflow", "video,workflow", None, "general", 0, None, 0),

    ("reddit", "disc-vid-002", "AfterEffects",
     "What's your go-to sound design library for tech / SaaS UI motion graphic accents?",
     "Looking for clean digital swooshes, clicks, and sub-bass drops that don't sound like cheap 2015 EDM stock effects. Any recommended composer packs?",
     "MotionSamurai", "https://www.reddit.com/r/AfterEffects/new/", 59, "Video & Content",
     "after effects, sound design, sfx, motion graphics", "video,sfx", None, "general", 0, None, 0),

    ("reddit", "disc-vid-003", "CreatorServices",
     "YouTube retention analysis: Why the 0:30 drop-off is almost always a pacing issue, not an idea issue",
     "Audited 50 videos across 10 client channels this quarter. The biggest pattern is overly long introductions before delivering on the thumbnail premise.",
     "RetentionStrategist", "https://www.reddit.com/r/CreatorServices/new/", 65, "Video & Content",
     "youtube pacing, retention curve, hook optimization", "video,growth", None, "general", 0, None, 0),

    # =========================================================================
    # --- 3. MARKETING, SEO & COPYWRITING ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-mkt-001", "Marketing",
     "Looking for B2B Lead Generation expert to book 15 qualified enterprise demos per month ($3,000 retainer + commission)",
     "We sell compliance software to mid-market healthcare companies. Need an expert in cold email infrastructure, Smartlead, Apollo, and tailored copy.",
     "HealthComplianceCEO", "https://www.reddit.com/r/Marketing/new/", 97, "Marketing & SEO",
     "lead generation, cold email, b2b outreach, retainer, enterprise", "marketing,sales", "$3,000/mo + Comm", "verified", 0, None, 0),

    ("reddit", "lead-mkt-002", "SEO",
     "Hiring Technical SEO Specialist for 100k page programmatic marketplace ($4,000 audit + sprint)",
     "Our site suffered a crawl budget bottleneck after releasing 80k dynamic city pages. Looking for an expert in log file analysis and internal linking architecture.",
     "MarketplaceFounder", "https://www.reddit.com/r/SEO/new/", 96, "Marketing & SEO",
     "technical seo, crawl budget, programmatic, audit, budget", "seo,audit", "$4,000 Milestone", "verified", 0, None, 0),

    ("reddit", "lead-mkt-003", "copywriting",
     "Need direct response copywriter for VSL + 5-step email onboarding sequence ($2,200)",
     "Launching a new fitness coaching membership. Need an engaging 10-minute Video Sales Letter script and welcome sequence that drives conversions.",
     "FitBizOnline", "https://www.reddit.com/r/copywriting/new/", 94, "Marketing & SEO",
     "direct response, vsl script, email sequence, budget", "copywriting", "$2,200", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-mkt-001", "SEO",
     "Google Search Console reporting huge swings in Discover traffic after the latest Core Algorithm update",
     "Anyone else noticing informational intent keywords getting pushed down in favor of forum and Reddit results? How are you adjusting your internal link strategy?",
     "RankMaster_99", "https://www.reddit.com/r/SEO/new/", 65, "Marketing & SEO",
     "google core update, search console, discover traffic, algorithms", "marketing,seo", None, "general", 0, None, 0),

    ("reddit", "disc-mkt-002", "copywriting",
     "The 'PAS' (Problem-Agitate-Solve) formula vs Story-Driven hooks for cold SaaS email outreach in 2026",
     "Tested 5,000 cold emails last month. Direct 2-sentence value statements outperformed long PAS frameworks by 3.4x on reply rates.",
     "CopyScribe_Ray", "https://www.reddit.com/r/copywriting/new/", 60, "Marketing & SEO",
     "cold email, copywriting frameworks, response rates", "marketing,copy", None, "general", 0, None, 0),

    ("reddit", "disc-mkt-003", "PPC",
     "Meta Ads Advantage+ campaigns vs manual bidding for $50-$100 AOV e-commerce products",
     "Seeing ASC campaigns fatiguing creatives 2x faster than 6 months ago. What structure is working best for keeping CPA stable at $5k/day ad spend?",
     "MediaBuyerElite", "https://www.reddit.com/r/PPC/new/", 63, "Marketing & SEO",
     "meta ads, facebook ads, roas, advantage plus", "marketing,ppc", None, "general", 0, None, 0),

    # =========================================================================
    # --- 4. AI, AUTOMATION & LLM WORKFLOWS ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-ai-001", "Automate",
     "Looking to hire an n8n / Make.com expert to automate our multi-channel sales pipeline ($2,000 - $3,500)",
     "We need to connect HubSpot CRM, Stripe webhooks, Slack alerts, and Google Sheets for automated invoicing. Fixed price project with fast turnaround.",
     "SalesDirectorMark", "https://www.reddit.com/r/Automate/new/", 98, "AI & Automation",
     "n8n, make.com, hubspot, stripe webhooks, automation, budget", "ai,automation", "$2,000 - $3,500", "verified", 0, None, 0),

    ("reddit", "lead-ai-002", "OpenAI",
     "[Hiring] AI Engineer to build local RAG pipeline with Llama 3 / OpenAI for internal legal docs ($6,000)",
     "Need someone with LangChain/LlamaIndex and Qdrant vector database experience to build a high-accuracy legal citation search engine with strict data privacy.",
     "LegalTechFounder", "https://www.reddit.com/r/OpenAI/new/", 97, "AI & Automation",
     "rag, llama 3, qdrant, vector database, ai engineer, budget", "ai,llm", "$6,000 Budget", "verified", 0, None, 0),

    ("reddit", "lead-ai-003", "ChatGPT",
     "Need AI voice assistant developer using Vapi.ai / Retell AI for dental clinic appointment booking ($3,000)",
     "Looking for an automation contractor to configure inbound phone AI bot connected to our EHR calendar. Fixed budget $3,000.",
     "DentalGroupManager", "https://www.reddit.com/r/ChatGPT/new/", 95, "AI & Automation",
     "vapi.ai, retell, voice bot, appointment scheduling, budget", "ai,voice", "$3,000", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-ai-001", "LocalLLaMA",
     "Llama 3.1 70B vs Mistral Large 2 for tool calling and JSON structured outputs in local agents",
     "Benchmarking function calling accuracy with Ollama and vLLM. Seeing near 98% schema compliance with GBNF grammars. What quantizations are you deploying?",
     "SelfHostedML", "https://www.reddit.com/r/LocalLLaMA/new/", 68, "AI & Automation",
     "localllama, vllm, ollama, structured outputs, json", "ai,llm", None, "general", 0, None, 0),

    ("reddit", "disc-ai-002", "n8n",
     "Self-hosted n8n on Hetzner VPS with queue mode (Redis + PostgreSQL) — complete production setup tips",
     "Running 100,000 webhook triggers daily. Here is how we scaled concurrency without hitting execution timeouts or memory leaks.",
     "AutoFlowDev", "https://www.reddit.com/r/n8n/new/", 64, "AI & Automation",
     "n8n, self-hosted, redis queue, postgresql, scaling", "ai,automation", None, "general", 0, None, 0),

    ("reddit", "disc-ai-003", "ChatGPT",
     "How are agencies packaging AI automation retainers in 2026? Fixed setup fee vs maintenance monthly?",
     "Seeing many clients balk at $5k upfront, but enthusiastically agreeing to $1.5k setup + $500/mo ongoing monitoring and prompt updates.",
     "AgencyPioneer", "https://www.reddit.com/r/ChatGPT/new/", 61, "AI & Automation",
     "agency pricing, ai retainers, business models", "ai,business", None, "general", 0, None, 0),

    # =========================================================================
    # --- 5. E-COMMERCE & RETAIL GROWTH ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-ecom-001", "Shopify",
     "[Hiring] Shopify Plus Developer to build custom bundle builder app & checkout extension ($4,500)",
     "Our 7-figure supplement brand needs a bespoke mix-and-match bundle drawer using Shopify Functions and React Checkout UI extension.",
     "NutritionD2C", "https://www.reddit.com/r/Shopify/new/", 98, "E-Commerce & Retail",
     "shopify plus, checkout extension, custom app, budget", "ecom,shopify", "$4,500 Fixed", "verified", 0, None, 0),

    ("reddit", "lead-ecom-002", "ecommerce",
     "Looking for Klaviyo Email Flow Specialist to increase repeat purchase rate ($2,000/mo retainer)",
     "Apparel brand doing $80k/mo. Need an expert to redesign our post-purchase flows, win-back campaigns, and VIP loyalty segments.",
     "ApparelBrandCEO", "https://www.reddit.com/r/ecommerce/new/", 96, "E-Commerce & Retail",
     "klaviyo, email flows, retention, repeat purchase, retainer", "ecom,marketing", "$2,000 / Month", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-ecom-001", "Shopify",
     "Shopify Hydrogen 2 (Remix) vs Liquid Theme with Sections Everywhere — is headless actually worth it for sub-$5M brands?",
     "Debating if the developer maintenance overhead of a headless storefront offsets the sub-second page loads. What are your real conversion lift numbers?",
     "EcomArchitect", "https://www.reddit.com/r/Shopify/new/", 63, "E-Commerce & Retail",
     "shopify hydrogen, headless commerce, remix, page speed", "ecom,shopify", None, "general", 0, None, 0),

    ("reddit", "disc-ecom-002", "AmazonSeller",
     "How to protect your brand registry from false IP infringement claims from counterfeit hijackers",
     "Had our top ASIN suppressed for 4 days over an automated competitor bot report. Here is the step-by-step escalations process that got us reinstated.",
     "FBA_Veteran", "https://www.reddit.com/r/AmazonSeller/new/", 66, "E-Commerce & Retail",
     "amazon fba, brand registry, asin reinstatement, seller support", "ecom,amazon", None, "general", 0, None, 0),

    # =========================================================================
    # --- 6. STARTUPS & SAAS FOUNDERS ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-saas-001", "SaaS",
     "Looking to hire technical co-founder / lead developer to rebuild MVP in Next.js + Supabase ($5,000 + equity)",
     "We have 1,200 waitlist signups for a B2B recruiting workflow tool. Current Bubble prototype is too slow. Looking for a full-stack engineer.",
     "RecruitTechFounder", "https://www.reddit.com/r/SaaS/new/", 98, "Startups & SaaS",
     "rebuild mvp, next.js, supabase, hire developer, budget", "saas,startup", "$5,000 + Equity", "verified", 0, None, 0),

    ("reddit", "lead-saas-002", "startups",
     "Need a fractional Head of Growth / Outbound Sales lead to take us from $10k to $50k MRR ($4,000/mo)",
     "B2B devtools SaaS with product-market fit. Need a proven outbound strategist to build our cold email & LinkedIn outbound engines.",
     "DevToolsFounder", "https://www.reddit.com/r/startups/new/", 96, "Startups & SaaS",
     "fractional growth, outbound sales, mrr, retainer", "saas,growth", "$4,000 / Month", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-saas-001", "SaaS",
     "Crossed $12,000 MRR after 9 months of zero traction — the 3 mindset shifts that changed everything",
     "We stopped building random features and started calling every single churned user within 15 minutes. Here's what we learned about onboarding friction.",
     "BootstrappedKev", "https://www.reddit.com/r/SaaS/new/", 71, "Startups & SaaS",
     "mrr milestone, churn reduction, customer interviews, bootstrapped", "saas,bootstrapped", None, "general", 0, None, 0),

    ("reddit", "disc-saas-002", "SideProject",
     "Launched my micro-SaaS on ProductHunt yesterday — breakdown of traffic, signups, and 14 paying customers",
     "Got #4 Product of the Day with 640 upvotes. Resulted in 3,200 unique visitors, 142 trial accounts, and $420 in immediate MRR.",
     "IndieMakerSam", "https://www.reddit.com/r/SideProject/new/", 65, "Startups & SaaS",
     "producthunt launch, conversion metrics, micro saas", "saas,launch", None, "general", 0, None, 0),

    # =========================================================================
    # --- 7. TECH & WEB DEVELOPMENT ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-web-001", "webdev",
     "Looking to hire a frontend specialist to optimize Core Web Vitals (LCP/INP) and fix layout shifts ($90-$120/hr)",
     "Our B2B platform has 50k monthly traffic but Google PageSpeed score is 42 on mobile. Need an expert to profile, optimize bundle size, and improve performance.",
     "TechLeadDan", "https://www.reddit.com/r/webdev/new/", 95, "Tech & Dev",
     "hire specialist, optimize, performance, lcp, inp, hourly rate", "webdev,agency", "$90 - $120/hr", "verified", 0, None, 0),

    ("reddit", "lead-web-002", "reactjs",
     "Need a senior React / TypeScript contractor to implement complex draggable dashboard canvas ($4,000)",
     "We are adding customizable drag-and-drop dashboard canvas to our enterprise software. 3-week milestone project.",
     "EnterpriseFrontend", "https://www.reddit.com/r/reactjs/new/", 94, "Tech & Dev",
     "react, typescript, canvas, drag and drop, budget", "webdev,react", "$4,000 Gig", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-web-001", "webdev",
     "The death of client-side bloated SPAs in favor of lightweight SSR & Server Components — are we finally back to sanity?",
     "Shipping 2MB JavaScript bundles to show a marketing landing page was absurd. Transitioning to server rendered islands cut our server response times in half.",
     "SeniorDev_Alex", "https://www.reddit.com/r/webdev/new/", 68, "Tech & Dev",
     "spa vs ssr, server components, bundle size, web performance", "webdev,architecture", None, "general", 0, None, 0),

    ("reddit", "disc-web-002", "python",
     "FastAPI vs Go for high-throughput microservices in 2026 — where does Python hit the ceiling?",
     "Running 15,000 async requests/sec with Uvicorn and uvloop. The bottleneck is almost always database I/O rather than Python runtime itself.",
     "PyArchitect", "https://www.reddit.com/r/Python/new/", 63, "Tech & Dev",
     "fastapi, python async, uvloop, microservices, performance", "webdev,python", None, "general", 0, None, 0),

    # =========================================================================
    # --- 8. MOBILE APP DEVELOPMENT ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-mob-001", "FlutterDev",
     "Hiring Flutter developer to build cross-platform fintech wallet (iOS + Android) ($5,000)",
     "Looking for an experienced Flutter engineer with Riverpod and clean architecture experience. Biometrics auth, Plaid integration, and Stripe payments required.",
     "FintechLabsCEO", "https://www.reddit.com/r/FlutterDev/new/", 95, "Mobile Apps",
     "flutter, riverpod, fintech, stripe, plaid, budget", "mobile,flutter", "$5,000 Budget", "verified", 0, None, 0),

    ("reddit", "lead-mob-002", "reactnative",
     "Looking for React Native expert to upgrade legacy codebase from RN 0.68 to 0.74 New Architecture ($3,500)",
     "Need an expert in TurboModules and Fabric renderer to resolve native dependency conflicts. 2-week contract, budget $3,500.",
     "MobileLeadKiran", "https://www.reddit.com/r/reactnative/new/", 93, "Mobile Apps",
     "react native, upgrade, turbomodules, fabric, budget", "mobile,reactnative", "$3,500", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-mob-001", "iOSProgramming",
     "SwiftUI NavigationStack vs Coordinator Pattern in large enterprise apps with 40+ dynamic deep links",
     "How are teams managing nested tab bars and authentication state transitions cleanly without memory retention cycles in iOS 18?",
     "AppleDevLead", "https://www.reddit.com/r/iOSProgramming/new/", 65, "Mobile Apps",
     "swiftui, navigationstack, coordinator pattern, ios architecture", "mobile,ios", None, "general", 0, None, 0),

    ("reddit", "disc-mob-002", "FlutterDev",
     "Flutter Impeller engine benchmarks on Android: Is the shader compilation jank completely gone?",
     "Tested complex 120fps list animations on mid-range Snapdragon devices. Impeller renders buttery smooth compared to old Skia pipeline.",
     "DartHacker", "https://www.reddit.com/r/FlutterDev/new/", 62, "Mobile Apps",
     "flutter, impeller, android performance, 120fps", "mobile,flutter", None, "general", 0, None, 0),

    # =========================================================================
    # --- 9. DEVOPS, CLOUD & INFRASTRUCTURE ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-devops-001", "devops",
     "Looking for a Kubernetes / AWS architect to migrate our monolithic stack to EKS ($80-$120/hr)",
     "We are migrating from single EC2 to multi-region EKS with Terraform and ArgoCD. Need a DevOps contractor for 3 weeks.",
     "DevOpsLeadCloud", "https://www.reddit.com/r/devops/new/", 96, "DevOps & Cloud",
     "kubernetes, aws, eks, terraform, argocd, hourly rate", "devops,cloud", "$80 - $120/hr", "verified", 0, None, 0),

    ("reddit", "lead-devops-002", "aws",
     "Need AWS cost optimization audit for ECS / RDS cluster running $12k/month bill ($2,500 fixed)",
     "Looking for an AWS certified consultant to identify idle resources, setup Graviton instances and savings plans. Paying 15% of first-year savings or $2,500 fixed.",
     "ScaleUpCFO", "https://www.reddit.com/r/aws/new/", 94, "DevOps & Cloud",
     "aws, cost optimization, rds, ecs, savings plan, budget", "devops,aws", "$2,500 Fixed", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-devops-001", "docker",
     "Multi-stage Docker builds with Alpine vs Distroless images — shrinking container sizes from 1.2GB to 48MB",
     "Here is the exact Dockerfile pattern we use for Node.js and Python microservices to pass zero-vulnerability security scans.",
     "ContainerNinja", "https://www.reddit.com/r/docker/new/", 67, "DevOps & Cloud",
     "docker, distroless, multi-stage, container security, alpine", "devops,docker", None, "general", 0, None, 0),

    ("reddit", "disc-devops-002", "devops",
     "Terraform vs OpenTofu in 2026: Has the BSL license fork changed your enterprise migration roadmap?",
     "Our infrastructure team recently evaluated OpenTofu with AWS S3 state backends. Compatibility is seamless with 0 syntax changes.",
     "InfraArchitect", "https://www.reddit.com/r/devops/new/", 64, "DevOps & Cloud",
     "opentofu, terraform, iac, cloud infrastructure", "devops,opentofu", None, "general", 0, None, 0),

    # =========================================================================
    # --- 10. LOCAL BUSINESS & FINANCE ---
    # =========================================================================
    # Box 1: Verified Buyer Leads
    ("reddit", "lead-local-001", "smallbusiness",
     "Looking for QuickBooks / Bookkeeping specialist to clean up 2025 messy tax records for multi-location cafe ($2,000)",
     "Need a certified ProAdvisor to reconcile Stripe deposits, payroll, and inventory accounts before tax deadline. Fixed budget $2,000.",
     "CafeOwnerJoe", "https://www.reddit.com/r/smallbusiness/new/", 95, "Local Biz & Finance",
     "quickbooks, bookkeeping, tax cleanup, reconciliation, budget", "local,finance", "$2,000 Fixed", "verified", 0, None, 0),

    ("reddit", "lead-local-002", "RealEstate",
     "Need custom lead intake CRM setup for commercial real estate brokerage ($3,500)",
     "Looking for an agency or consultant to integrate GoHighLevel CRM with our website property listings and SMS follow-ups.",
     "BrokeragePartner", "https://www.reddit.com/r/RealEstate/new/", 94, "Local Biz & Finance",
     "crm setup, gohighlevel, real estate, lead intake, budget", "local,crm", "$3,500", "verified", 0, None, 0),

    # Box 2: Casual Discussions
    ("reddit", "disc-local-001", "smallbusiness",
     "How local service businesses (HVAC, Plumbing, Dental) are getting 60% of new calls from Google Local Services Ads (LSA)",
     "Traditional SEO is taking too long for service businesses. The Google Guaranteed badge with pay-per-lead is giving our clients 5x better ROI.",
     "LocalGrowthGuru", "https://www.reddit.com/r/smallbusiness/new/", 69, "Local Biz & Finance",
     "google lsa, local seo, google guaranteed, small business growth", "local,growth", None, "general", 0, None, 0),

    ("reddit", "disc-local-002", "Accounting",
     "Cash vs Accrual accounting for fast-growing SaaS agencies: When is the exact right time to make the switch?",
     "Many founders delay moving to accrual until they hit $1M ARR, but it makes investor due diligence painful. Here is the threshold checklist.",
     "CPA_Adviser", "https://www.reddit.com/r/Accounting/new/", 62, "Local Biz & Finance",
     "accrual accounting, revenue recognition, agency finance, arr", "local,finance", None, "general", 0, None, 0)
]

print(f"[*] Seeding {len(ALL_SEED_DATA)} multi-industry verified leads and casual discussions across all 10 fields...")

for item in ALL_SEED_DATA:
    cursor.execute("""
    INSERT OR REPLACE INTO leads (
        platform, platform_id, community, title, body, author, url,
        intent_score, intent_category, matched_keywords, niche_tags, budget_detected,
        lead_box, is_spam, spam_reason, spam_confidence
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, item)

conn.commit()

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 0 AND (lead_box = 'verified' OR (lead_box IS NULL AND intent_score >= 70))")
v_count = cursor.fetchone()[0]

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 0 AND lead_box = 'general'")
g_count = cursor.fetchone()[0]

cursor.execute("SELECT count(*) FROM leads WHERE is_spam = 1 OR lead_box = 'spam'")
s_count = cursor.fetchone()[0]

print(f"[✓] Seeder complete! Verified: {v_count}, General: {g_count}, Spam: {s_count}, Total: {v_count + g_count + s_count}")
conn.close()
