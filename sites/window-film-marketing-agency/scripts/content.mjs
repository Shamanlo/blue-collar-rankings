// All site copy lives here. build.mjs turns it into pages.

export const site = {
  name: "Window Film Marketing Agency",
  domain: "windowfilmmarketingagency.com",
  url: "https://windowfilmmarketingagency.com",
  email: "info@windowfilmmarketingagency.com",
  // Free key from https://web3forms.com (enter the inbox that should receive leads).
  // Left empty, the forms open the visitor's email app addressed to site.email instead.
  web3formsKey: "",
  year: 2026,
  tagline: "Marketing, AI search and web design built only for window film companies.",
};

// ---------- Marketing services ----------
export const services = [
  {
    slug: "ai-search-optimization",
    nav: "AI Search Optimization",
    icon: "spark",
    card: "Get named when buyers ask ChatGPT, Gemini or Google's AI Overviews who installs security film, solar film or home tint near them.",
    title: "AI Search Optimization for Window Film Companies",
    metaTitle: "AI Search Optimization (AEO) for Window Film Companies",
    metaDesc: "Get your window tinting company recommended by ChatGPT, Gemini, Perplexity and Google AI Overviews. AEO built for residential, commercial and security film installers.",
    eyebrow: "AEO · GEO · AI SEO",
    lead: "Property managers and homeowners now ask an AI assistant, \"Who installs anti-graffiti film on storefronts in Long Beach?\" and get two or three names back. We make sure one of them is yours.",
    intro: {
      h: "AI only recommends the film companies it can verify",
      p: [
        "An AI assistant doesn't browse ten pages of results. It pulls facts from your website, your Google Business Profile, directory listings, manufacturer dealer locators and reviews, then names the companies it is most confident about.",
        "If your site says \"window tinting\" on one page and nothing else, the AI can't tell whether you do 14 mil security film, skylight tinting or decorative frost. Competitors with clear, specific pages win the answer, even if your installs are better.",
      ],
    },
    points: {
      h: "What we do",
      items: [
        { t: "AI visibility audit", d: "We ask five AI assistants the questions your buyers actually ask (by film type and city) and record exactly who gets recommended today." },
        { t: "Entity and listing cleanup", d: "One name, address, phone, service area and film lineup everywhere: Google, Bing, Apple Maps, Yelp, BBB, IWFA directory and your manufacturer dealer locator." },
        { t: "Answer-ready service pages", d: "Pages that answer the real question in plain English: what security film does and doesn't stop, what VLT to pick for a west-facing office, how long anti-graffiti film lasts." },
        { t: "Structured data", d: "LocalBusiness, Service, FAQPage and Review schema so machines can read your film types, service area, warranties and certifications without guessing." },
        { t: "Citations and reviews", d: "Reviews that name the film and the result (\"the 3M Prestige cut the heat in our sunroom\") and mentions on trusted local and industry sites." },
        { t: "Monthly re-testing", d: "We re-run the same questions every month so you can see where AI names you, and where it still names a competitor." },
      ],
    },
    asks: {
      h: "Questions your buyers are asking AI right now",
      items: [
        "Who installs security window film for retail storefronts near me?",
        "Best company for home window tinting to stop hardwood floors fading?",
        "Is window film safe on dual-pane low-e windows, and who warranties it?",
        "Who can frost our conference room glass this week?",
        "How much does commercial solar window film cost per square foot?",
        "Which tint shop near me is a certified 3M or LLumar dealer?",
      ],
    },
    faq: [
      { q: "Is AI search replacing Google for window film leads?", a: "Not replacing, adding to. Google's own results now open with an AI Overview for many \"best window tinting near me\" style searches, and more commercial buyers ask ChatGPT for a shortlist before they call. The good news: the same work (clear service pages, consistent listings, specific reviews) helps both." },
      { q: "How long before AI starts recommending us?", a: "Listing and schema fixes are often picked up in a few weeks. New service pages and reviews usually take one to three months to show up consistently in answers. We re-test monthly so you can see it happen." },
      { q: "Do we still need regular SEO?", a: "Yes. AI assistants lean heavily on the same sources Google ranks. We run AEO and local SEO together so you are not paying twice for overlapping work." },
    ],
  },
  {
    slug: "local-seo",
    nav: "Local SEO",
    icon: "pin",
    card: "Rank in the map pack and organic results for \"window tinting near me\", \"commercial window film\" and every film type you install, in every city you serve.",
    title: "Local SEO for Window Tinting and Film Companies",
    metaTitle: "Local SEO for Window Tinting Companies | Window Film Marketing Agency",
    metaDesc: "Local SEO for window film installers: map pack rankings, film-specific service pages and service-area pages for residential, commercial and security window film.",
    eyebrow: "Local SEO",
    lead: "Window film is a local, high-ticket, high-intent search. We get you into the map pack and the top organic spots for the film types that pay best, in the towns you actually want to drive to.",
    intro: {
      h: "One \"Services\" page can't rank for seven different films",
      p: [
        "Someone searching \"skylight tinting\" and someone searching \"smash-and-grab security film\" are different buyers with different budgets. Most tint shop websites send both to the same generic page, and neither ranks.",
        "We build a page for every film you install and every core city you serve, then support them with Google Business Profile work, citations and links from local and industry sources.",
      ],
    },
    points: {
      h: "What's included",
      items: [
        { t: "Keyword map by film type", d: "Residential tint, commercial solar film, security and safety film, anti-graffiti, decorative and frosted film, skylight tinting, auto tint and PPF, each mapped to the searches that convert." },
        { t: "Service-area pages", d: "Real pages for the cities you serve, with local projects, building types and climate details, not copy-paste pages with the town name swapped." },
        { t: "On-page and technical SEO", d: "Titles, headings, internal links, image alt text, Core Web Vitals, crawl errors and indexing fixed and kept fixed." },
        { t: "Citations and NAP consistency", d: "Your name, address and phone matched across 40+ directories, home service platforms and manufacturer dealer locators." },
        { t: "Links that make sense", d: "Local business associations, chambers, builders and designers you work with, manufacturer dealer pages and industry directories." },
        { t: "Call and form tracking", d: "Every call and estimate request tagged by page and keyword, so you can see which film types are actually producing jobs." },
      ],
    },
    asks: {
      h: "Searches we target",
      items: [
        "window tinting near me / home window tinting [city]",
        "commercial window film [city] / office window tinting",
        "security window film / safety film for glass doors",
        "anti-graffiti film for storefronts",
        "frosted window film / privacy film for bathroom windows",
        "skylight tinting / solar film for sunrooms",
      ],
    },
    faq: [
      { q: "We serve a whole metro. How many city pages do we need?", a: "Start with the five to ten cities that bring your best jobs, not every suburb. Each page needs real substance: local projects, building types, HOA or historic district notes. We add more as those pages earn rankings." },
      { q: "Can you help if our shop address is outside the city we want to rank in?", a: "Yes, within limits. Map pack rankings lean on proximity, so we focus organic service-area pages and reviews on the cities you want, and make sure your Google Business Profile service area is set correctly." },
    ],
  },
  {
    slug: "google-business-profile",
    nav: "Google Business Profile",
    icon: "store",
    card: "Categories, services, photos, posts and Q&A set up for a film installer, so you show up in Maps for the jobs you want.",
    title: "Google Business Profile Management for Window Film Companies",
    metaTitle: "Google Business Profile Management for Window Tinting Companies",
    metaDesc: "Google Business Profile optimization for window film installers: categories, services by film type, before-and-after photos, posts, Q&A and review responses.",
    eyebrow: "Google Business Profile",
    lead: "Your Google Business Profile is the first thing most buyers see, and the source AI assistants trust most. We run it like the storefront it is.",
    intro: {
      h: "Most tint shop profiles are missing half the signals Google uses",
      p: [
        "Wrong primary category, no services listed, three photos from 2019 and unanswered reviews. That's the profile most window film companies are working with.",
        "We set it up for how Google and AI actually read it: every film type as a service, a photo stream of real installs, weekly posts and replies that mention the work.",
      ],
    },
    points: {
      h: "What we manage",
      items: [
        { t: "Categories and services", d: "\"Window tinting service\" as the right primary category, the right secondary categories, and every film you install listed as a service with a description." },
        { t: "Project photos", d: "Before-and-after, inside-out glare shots, frosted glass in conference rooms, storefront security film, geotagged and named properly." },
        { t: "Weekly posts", d: "Recent installs, seasonal offers (summer heat, holiday break-in season), and manufacturer warranty reminders." },
        { t: "Q&A seeded with real questions", d: "Will film void my window warranty? Can you see out at night? How long does it take to cure? Answered before buyers have to call." },
        { t: "Review responses", d: "Fast, specific replies that mention the film and the job, written in your voice." },
        { t: "Spam and competitor edits", d: "We watch for suggested edits, duplicate listings and fake competitor profiles and get them dealt with." },
      ],
    },
    faq: [
      { q: "Do you need access to our profile?", a: "Yes, we ask to be added as a manager. You stay the owner, and you can remove us anytime." },
      { q: "We're a service-area business with no storefront. Does that matter?", a: "It changes the setup (hidden address, service area instead) but not the strategy. Most mobile installers and many auto tint shops run this way." },
    ],
  },
  {
    slug: "google-ads",
    nav: "Google Ads",
    icon: "target",
    card: "Search campaigns split by film type and buyer, with call tracking, so you pay for commercial and security film leads, not DIY tint kit shoppers.",
    title: "Google Ads for Window Film Companies",
    metaTitle: "Google Ads and PPC for Window Tinting Companies",
    metaDesc: "Google Ads for window film installers: campaigns by film type, negative keywords that block DIY and auto searches, landing pages and tracking by booked estimate.",
    eyebrow: "Paid search",
    lead: "Window film ads burn money fast when \"window tint\" matches car tint, DIY film kits and tint law questions. We build campaigns that only pay for the buyers you want.",
    intro: {
      h: "\"Window tint\" is three different markets in one keyword",
      p: [
        "A homeowner with a hot bonus room, a facilities manager with a glass curtain wall and a teenager looking up legal tint for a Civic all type almost the same words. Broad campaigns pay for all three.",
        "We split campaigns by film type and buyer, send each to a matching landing page, and judge everything by booked estimates instead of clicks.",
      ],
    },
    points: {
      h: "How we run it",
      items: [
        { t: "Campaigns by film type", d: "Residential, commercial solar, security and safety, anti-graffiti, decorative. Separate budgets so the high-value work isn't starved." },
        { t: "Negative keyword lists", d: "Built from years of tint search terms: DIY, Amazon, static cling, car tint laws, tint percentage charts, jobs and careers." },
        { t: "Dedicated landing pages", d: "One page per campaign with the film, the benefit, photos of real installs and a short estimate form." },
        { t: "Local Services Ads where eligible", d: "We check whether your category and market qualify and set up Google Guaranteed when it makes sense." },
        { t: "Call tracking and recordings", d: "Know which keyword produced the 6,000 sq ft office building call, and which produced a wrong number." },
        { t: "Monthly report by booked job", d: "Spend, leads, estimates booked and jobs won, by film type. Not a 30-page click report." },
      ],
    },
    faq: [
      { q: "What should we budget?", a: "It depends on the market and the film types. We'll give you a number after looking at search volume and cost per click in your service area. We'd rather start focused on your best-margin film than spread thin." },
      { q: "Do you mark up ad spend?", a: "No. Ad spend is billed by Google to your card. Our management fee is separate and flat." },
    ],
  },
  {
    slug: "reviews-reputation",
    nav: "Reviews & Reputation",
    icon: "star",
    card: "A simple system that gets customers to leave reviews naming the film and the result: less heat, no glare, privacy, safer glass.",
    title: "Reviews and Reputation for Window Film Companies",
    metaTitle: "Review Generation for Window Tinting Companies",
    metaDesc: "Get more Google reviews that mention the film you installed and the result. Review requests, responses and reputation monitoring for window film companies.",
    eyebrow: "Reviews",
    lead: "\"Great job, 5 stars\" helps a little. \"They installed security film on our storefront and it held up to a break-in attempt\" helps a lot, with buyers and with AI.",
    intro: {
      h: "Specific reviews sell film, and AI reads every word",
      p: [
        "Buyers want proof from someone with their problem: the hot west-facing living room, the office with glare on every monitor, the storefront that keeps getting tagged.",
        "AI assistants quote the same details. A review that mentions \"anti-graffiti film\" and \"Pasadena\" is a reason to recommend you for exactly that question.",
      ],
    },
    points: {
      h: "What we set up",
      items: [
        { t: "Automatic review requests", d: "Text and email a day or two after the install, with a direct link. Follow-up once, never pushy." },
        { t: "Prompts that draw out detail", d: "We ask what changed: room temperature, glare, privacy, how the crew left the space. Customers write better reviews when asked better questions." },
        { t: "Photo reviews", d: "Customers can add their own after shots, which do more than any stock photo." },
        { t: "Responses in your voice", d: "Every review answered within a couple of days, naming the film and thanking them for the specifics." },
        { t: "Multi-platform", d: "Google first, then the sites that matter in your market: Yelp, Nextdoor, BBB, Houzz, Facebook." },
        { t: "Alerts for unhappy customers", d: "A private feedback step catches problems (a bubble, a missed edge) so you can fix them before they become a public review." },
      ],
    },
    faq: [
      { q: "Is it okay to ask for reviews?", a: "Yes, as long as you ask every customer and don't offer anything in exchange. We don't gate reviews or filter who gets asked." },
      { q: "Do you write fake reviews?", a: "Never. It violates Google's and the FTC's rules, and it's exactly the kind of signal that gets profiles suspended." },
    ],
  },
];

// ---------- Web design ----------
export const webDesignIndex = {
  title: "Window Film Website Design",
  metaTitle: "Website Design for Window Film and Tinting Companies",
  metaDesc: "Fast, custom websites for window film companies: a page for every film type, project galleries, estimate forms and service-area pages built to rank and convert.",
  eyebrow: "Web design",
  lead: "A window film website has one job: turn a search for \"commercial window tinting\" or \"frosted privacy film\" into a booked estimate. We design every page around that.",
};

export const webDesign = [
  {
    slug: "custom-websites",
    nav: "Custom Window Film Websites",
    icon: "layout",
    card: "A full site built around the films you install: residential, commercial, security, decorative, solar and skylight, each with its own page.",
    title: "Custom Websites for Window Film Companies",
    metaTitle: "Custom Website Design for Window Tinting Companies",
    metaDesc: "Custom website design for window film installers. Service pages for every film type, galleries, estimate forms, schema and hosting, built to rank and book estimates.",
    eyebrow: "Custom websites",
    lead: "Not a template with your logo dropped in. A site structured like your business: commercial and residential divisions, every film you install, the cities you serve and the projects that prove it.",
    intro: {
      h: "Built the way buyers shop for film",
      p: [
        "A commercial buyer wants heat rejection numbers, a warranty, a project list and a way to request a site survey. A homeowner wants to know if they'll still see the view and whether film voids their window warranty. Your site should answer both without making either dig.",
        "Every site we build splits residential and commercial, gives each film type its own page, and keeps the estimate button one tap away on every screen.",
      ],
    },
    sitemap: {
      h: "A typical window film site map",
      groups: [
        { t: "Commercial window film", items: ["Commercial window tinting", "Solar window film", "Security and safety film", "Anti-graffiti window film", "Frosted privacy glass", "Skylight tinting"] },
        { t: "Residential window film", items: ["Home window tinting", "Residential security film", "Decorative and privacy film", "UV and fade protection"] },
        { t: "Proof", items: ["Projects and case studies", "Reviews", "Manufacturer certifications", "Warranty information"] },
        { t: "Local", items: ["Service area hub", "One page per core city", "Free estimate / site survey"] },
      ],
    },
    points: {
      h: "On every site we build",
      items: [
        { t: "Mobile-first and fast", d: "Most film searches happen on a phone. Pages load in about a second, with tap-to-call and the estimate form always in reach." },
        { t: "Film-specific service pages", d: "Benefits, specs that matter (VLT, heat rejection, UV, mil thickness), applications, FAQs and photos for each film." },
        { t: "Manufacturer and warranty proof", d: "Certified dealer badges, warranty terms and film brand pages, without letting the manufacturer's site steal your traffic." },
        { t: "Estimate form that qualifies", d: "Property type, rough window count or square footage, goal (heat, glare, privacy, security), glass type and photo upload." },
        { t: "Schema and AI-readable structure", d: "LocalBusiness, Service, FAQPage and BreadcrumbList markup so search engines and AI assistants understand exactly what you do." },
        { t: "You own it", d: "Your domain, your content, your analytics. No hostage contracts." },
      ],
    },
    faq: [
      { q: "How long does a new site take?", a: "Most window film sites launch in four to six weeks: about a week of discovery and content, two to three weeks of design and build, and a week of review and launch." },
      { q: "Can we keep our current domain and rankings?", a: "Yes. We map every old URL to its new page with 301 redirects so you keep the rankings and links you've already earned." },
      { q: "Do you write the content?", a: "Yes. We interview you about your films, crews, warranties and best jobs, then write it. You approve everything before launch." },
    ],
  },
  {
    slug: "website-redesign",
    nav: "Website Redesign",
    icon: "refresh",
    card: "Rebuild a dated or slow tint shop site without losing the rankings you already have.",
    title: "Website Redesign for Window Tinting Companies",
    metaTitle: "Window Tinting Website Redesign | Keep Your Rankings",
    metaDesc: "Redesign your window film company website without losing rankings: URL mapping, 301 redirects, faster pages, better estimate forms and film-specific service pages.",
    eyebrow: "Redesign",
    lead: "Your site was fine in 2017. Now it's slow on phones, half the film brands are out of date and the contact form goes to an inbox nobody checks. Let's fix it without starting from zero.",
    intro: {
      h: "Redesigns go wrong when rankings get thrown away",
      p: [
        "Most redesign disasters come from changing every URL and deleting pages that were quietly bringing in leads. We start by measuring what's working, then keep it.",
      ],
    },
    points: {
      h: "How we redesign safely",
      items: [
        { t: "Traffic and ranking audit", d: "We find the pages, keywords and backlinks that already bring estimate requests before we touch anything." },
        { t: "URL map and 301 redirects", d: "Every old page points to its new home. Nothing that ranks gets orphaned." },
        { t: "Content upgrade", d: "Old pages rewritten with current film lineups, real specs and better answers, not just new paint." },
        { t: "Speed and mobile fixes", d: "Compressed images, no bloated page builders, and layouts built for a thumb." },
        { t: "Form and call tracking", d: "Every lead source tracked from launch day so you can compare before and after." },
        { t: "Post-launch monitoring", d: "We watch Search Console for 60 days after launch and fix any crawl or ranking issues fast." },
      ],
    },
    faq: [
      { q: "Will our rankings drop after the redesign?", a: "A small wobble for a week or two is normal while Google recrawls. With proper redirects and kept content, rankings usually recover quickly and then improve because the new pages are better." },
    ],
  },
  {
    slug: "service-area-pages",
    nav: "Service & Service-Area Pages",
    icon: "map",
    card: "A page for every film you install and every city you serve, written with real local detail.",
    title: "Service Pages and Service-Area Pages for Window Film Companies",
    metaTitle: "Service-Area Pages for Window Tinting Companies",
    metaDesc: "Film-specific service pages and city service-area pages for window film installers, with local projects, building types and FAQs. Built to rank, not to spam.",
    eyebrow: "Service pages",
    lead: "Search engines and AI rank pages, not companies. If you want to show up for \"security window film in Glendale\", you need a page that's genuinely about that.",
    intro: {
      h: "Specific pages win specific searches",
      p: [
        "The best-ranking window film companies have a page for each film type (security film, anti-graffiti film, solar film, frosted privacy glass, skylight tinting) and a hub of city pages linking to them.",
        "The trick is making each page worth reading. Thin pages with the city name swapped get ignored by Google and AI alike.",
      ],
    },
    points: {
      h: "What goes on each page",
      items: [
        { t: "The problem it solves", d: "Heat and hot spots, glare on screens, fading, break-ins and smash-and-grab, graffiti and scratchiti, privacy." },
        { t: "Film options and specs", d: "Ceramic, spectrally selective, dual-reflective, neutral, 4 to 14 mil security, sacrificial anti-graffiti, dusted crystal and gradient decorative." },
        { t: "Local proof", d: "Projects in that city, building types you see there, HOA or historic district notes, climate details." },
        { t: "FAQs with real answers", d: "Cost range, install time, cure time, cleaning, warranty, glass compatibility." },
        { t: "Internal links", d: "Each city page links to the film pages and back, so authority flows where it should." },
        { t: "Schema", d: "Service and FAQPage markup on every page, tied to your business entity." },
      ],
    },
    faq: [
      { q: "Aren't city pages considered spam?", a: "Duplicate pages with only the city name changed are. Pages with real local projects, photos and answers are some of the best-performing pages on a film installer's site." },
    ],
  },
  {
    slug: "project-galleries",
    nav: "Project Galleries & Case Studies",
    icon: "image",
    card: "Before-and-after galleries and short case studies that show the building, the film and the result.",
    title: "Project Galleries and Case Studies for Window Film Companies",
    metaTitle: "Window Film Project Galleries and Case Studies",
    metaDesc: "Project pages and case studies for window tinting companies: before-and-after photos, film used, square footage and results. Proof that sells commercial jobs.",
    eyebrow: "Proof",
    lead: "Commercial buyers want to see that you've done a building like theirs. A good project page answers that in thirty seconds.",
    intro: {
      h: "Every install is a sales page waiting to be written",
      p: [
        "A college classroom that needed solar film to cut glare on projectors. A downtown storefront that kept getting tagged. A dental office that wanted frosted glass without losing daylight. Each of those is a page that ranks and closes the next similar job.",
      ],
    },
    points: {
      h: "What a project page includes",
      items: [
        { t: "The building and the problem", d: "Type of property, glass and orientation, and why the client called." },
        { t: "The film and the spec", d: "Brand and product, VLT, heat rejection or mil thickness, attachment system if security film." },
        { t: "Before and after photos", d: "Including the shots that matter: glare on screens, view out at dusk, frosted band height." },
        { t: "Scope and timeline", d: "Square footage, number of panes, after-hours work, how long the install took." },
        { t: "The result in the client's words", d: "A quote or review tied to the project." },
        { t: "Easy to add", d: "We set it up so your team can upload photos from the job site and we turn them into a page." },
      ],
    },
    faq: [
      { q: "We don't have great photos. Is that a problem?", a: "We'll show your crew how to shoot before-and-after on a phone in two minutes per job. Real, slightly imperfect photos beat stock images every time." },
    ],
  },
  {
    slug: "estimate-forms",
    nav: "Estimate Forms & Lead Capture",
    icon: "form",
    card: "Estimate and site survey forms that collect what you need to quote: property type, glass, square footage, goals and photos.",
    title: "Estimate Request Forms for Window Film Companies",
    metaTitle: "Estimate Forms and Lead Capture for Window Tinting Companies",
    metaDesc: "Estimate request forms built for window film installers: property type, glass type, window count, goals and photo upload. Fewer tire-kickers, faster quotes.",
    eyebrow: "Lead capture",
    lead: "\"Name, email, message\" makes you play phone tag for three days. A good estimate form gets you enough to quote, or at least to book the site visit, on the first call.",
    intro: {
      h: "Ask the questions you'd ask on the phone",
      p: [
        "Residential or commercial? Roughly how many windows or how many square feet? What's the goal: heat, glare, fading, privacy, security? Single pane or dual pane, low-e or not? A photo of the windows?",
        "Short enough that people finish it. Detailed enough that you can prioritize the 40-pane office building over the single bathroom window.",
      ],
    },
    points: {
      h: "Built into every form",
      items: [
        { t: "Two paths", d: "Residential and commercial forms ask different questions." },
        { t: "Photo upload", d: "Customers snap the windows from their phone." },
        { t: "Goal picker", d: "Heat rejection, glare reduction, UV and fade protection, daytime privacy, safety and security, decorative." },
        { t: "Instant routing", d: "Leads go to email and text, and to your CRM if you have one (Jobber, Housecall Pro, ServiceTitan, HubSpot)." },
        { t: "Source tracking", d: "Every lead tagged with the page and campaign it came from." },
        { t: "Spam filtering", d: "No more SEO spam and fake inquiries clogging the inbox." },
      ],
    },
    faq: [
      { q: "Will a longer form scare people off?", a: "A form that asks relevant questions with tap-to-select answers converts about as well as a short one, and the leads are much better. We test it after launch." },
    ],
  },
  {
    slug: "hosting-care",
    nav: "Hosting & Care Plans",
    icon: "shield",
    card: "Fast hosting, security updates, backups and small content edits, handled every month.",
    title: "Website Hosting and Care Plans for Window Film Companies",
    metaTitle: "Website Hosting and Maintenance for Window Tinting Companies",
    metaDesc: "Fast, secure hosting and monthly care for window film company websites: updates, backups, uptime monitoring and content edits included.",
    eyebrow: "Hosting & care",
    lead: "Your site should be the one thing you never have to think about. We host it on a global network, keep it secure and make changes when you need them.",
    intro: {
      h: "Fast, secure and always up",
      p: [
        "We host on Cloudflare's global network, so pages load fast for every visitor and stay up when traffic spikes. No plugin updates to babysit, no surprise hacks.",
      ],
    },
    points: {
      h: "Every care plan includes",
      items: [
        { t: "Global hosting and SSL", d: "Served from data centers close to your customers, with HTTPS on every page." },
        { t: "Backups and version history", d: "Every change is saved, so any mistake can be rolled back in minutes." },
        { t: "Uptime monitoring", d: "We know if your site has a problem before your customers do." },
        { t: "Monthly content edits", d: "New film lineup, a new city, an updated warranty, a seasonal promo. Send it over and we'll make the change." },
        { t: "New project pages", d: "Send photos from recent installs and we'll publish them." },
        { t: "Monthly report", d: "Traffic, calls, estimate requests and rankings in one short email." },
      ],
    },
    faq: [
      { q: "Can we host the site ourselves?", a: "Yes. You own the site and can move it anytime. Most clients keep it with us because it's one less thing to manage." },
    ],
  },
];

// ---------- Film specialties (who we serve) ----------
export const specialties = [
  {
    slug: "residential-window-tinting",
    nav: "Residential Window Tinting",
    icon: "home",
    card: "Home window tinting for heat, glare, fading and daytime privacy.",
    title: "Marketing for Residential Window Tinting Companies",
    metaTitle: "Marketing for Home Window Tinting Companies",
    metaDesc: "Marketing and websites for residential window tinting companies: reach homeowners searching for heat, glare, UV fade protection and privacy film.",
    eyebrow: "Residential window film",
    lead: "Homeowners don't search for \"spectrally selective film\". They search \"why is my upstairs so hot\" and \"how to stop sun fading hardwood floors\". We meet them there.",
    intro: {
      h: "Selling home tint means answering the worries first",
      p: [
        "Will it make the house dark? Will it look mirrored from the street? Does it void my window warranty? Will the HOA approve it? Homeowners who don't get those answers on your site simply don't call.",
        "We build pages and content around the problems (hot rooms, glare on the TV, faded furniture, nosy neighbors) and answer the objections up front, so the calls you get are ready to book.",
      ],
    },
    points: {
      h: "How we market residential tint",
      items: [
        { t: "Problem-first pages", d: "Hot bonus rooms and sunrooms, glare on TVs and home offices, UV fading of hardwood floors, furniture and art, daytime privacy." },
        { t: "Objection answers", d: "Neutral and spectrally selective films that keep the view, dual-pane and low-e glass compatibility, manufacturer warranty that covers seal failure, HOA approval." },
        { t: "Seasonal campaigns", d: "Heat in summer, glare in winter when the sun sits low, privacy for new construction." },
        { t: "Neighborhood proof", d: "Project photos and reviews from the subdivisions you work in most." },
        { t: "Showroom and sample visits", d: "Pages and ads that book in-home film sample consultations, not just phone quotes." },
        { t: "Referral and builder programs", d: "Landing pages for realtors, builders and interior designers who send you work." },
      ],
    },
    asks: {
      h: "What homeowners actually search",
      items: [
        "how to keep upstairs room cool in summer",
        "window film to stop furniture fading",
        "privacy window film you can see out of",
        "does window tint void window warranty",
        "home window tinting cost",
        "best window film for west facing windows",
      ],
    },
    jargon: [
      { t: "VLT", d: "Visible light transmission. How much daylight gets through. Homeowners usually want 35 to 70%." },
      { t: "TSER", d: "Total solar energy rejected. The headline heat number commercial and residential buyers compare." },
      { t: "Spectrally selective / ceramic", d: "Films that block infrared heat without darkening or mirroring the glass." },
      { t: "UV rejection", d: "Most quality films block 99% of UV, the main cause of fading." },
      { t: "Low-e compatibility", d: "Whether a film is approved for low-e dual-pane glass without risking thermal stress or the window warranty." },
    ],
    faq: [
      { q: "Do you work with residential-only tint companies?", a: "Yes. Many of our clients do mostly homes. We focus your budget on the neighborhoods and film types with the best margins." },
    ],
  },
  {
    slug: "commercial-window-film",
    nav: "Commercial Window Film",
    icon: "building",
    card: "Office, retail, school, healthcare and multifamily window film projects.",
    title: "Marketing for Commercial Window Film Companies",
    metaTitle: "Marketing for Commercial Window Tinting Companies",
    metaDesc: "Marketing for commercial window film installers: reach property managers, facilities directors and general contractors looking for solar, security and decorative film.",
    eyebrow: "Commercial window film",
    lead: "Commercial film is bought by property managers, facilities directors, architects and general contractors. They research, compare and ask for proof. We give them all three.",
    intro: {
      h: "Commercial buyers want proof before they request a survey",
      p: [
        "A facilities manager comparing three bids wants to see similar buildings, film specs, energy savings estimates, certificates of insurance and a manufacturer warranty. If your site is built for homeowners, they move on.",
        "We build a commercial division on your site and in your marketing: case studies by building type, spec sheets, energy and comfort results and a site survey request built for B2B.",
      ],
    },
    points: {
      h: "How we market commercial film",
      items: [
        { t: "Pages by building type", d: "Office buildings, retail storefronts, schools and universities, healthcare, hotels, multifamily, government and data centers." },
        { t: "Pages by problem", d: "Hot spots and HVAC load, glare on monitors, fading merchandise, privacy for conference rooms, safety and security." },
        { t: "Energy and ROI content", d: "Solar heat gain reduction, payback period, utility rebates and how film supports LEED and sustainability goals." },
        { t: "Case studies", d: "Square footage, film used, timeline, after-hours installation and the client's result." },
        { t: "LinkedIn and B2B outreach", d: "Reach property management companies, facility directors and GCs in your metro." },
        { t: "Bid and spec support", d: "Downloadable spec sheets and a fast site survey request form." },
      ],
    },
    asks: {
      h: "What commercial buyers search",
      items: [
        "commercial window tinting [city]",
        "office window film for glare",
        "solar window film energy savings",
        "window film for schools safety",
        "storefront window film",
        "conference room frosted glass film",
      ],
    },
    jargon: [
      { t: "SHGC", d: "Solar heat gain coefficient. Lower means less heat through the glass; used in energy modeling." },
      { t: "Heat rejection and hot spots", d: "Cutting the solar heat that makes perimeter offices unbearable and overworks HVAC." },
      { t: "Thermal stress analysis", d: "A glass-to-film check that confirms film won't overstress large or heat-strengthened panes." },
      { t: "Daylight-to-the-edge", d: "Install detail where film is cut tight to the frame for a cleaner look." },
      { t: "Manufacturer warranty", d: "Commercial warranties from 3M, LLumar, Solar Gard, Madico and others that buyers ask to see." },
    ],
    faq: [
      { q: "Can you help us win more bid work?", a: "We can make you easier to find and easier to shortlist: proof pages, spec sheets and visibility with property managers and GCs. Pricing and bid strategy stay with you." },
    ],
  },
  {
    slug: "security-safety-film",
    nav: "Security & Safety Film",
    icon: "lock",
    card: "Smash-and-grab, forced entry, school safety and blast mitigation film.",
    title: "Marketing for Security and Safety Window Film Installers",
    metaTitle: "Marketing for Security Window Film Companies",
    metaDesc: "Marketing for security window film installers: reach retailers, schools, homeowners and facilities looking for smash-and-grab, forced entry and safety film.",
    eyebrow: "Security & safety film",
    lead: "Security film is the highest-urgency, highest-ticket film you sell, and the most misunderstood. We position you as the installer who explains it honestly and installs it right.",
    intro: {
      h: "Buyers search right after something goes wrong",
      p: [
        "A jewelry store after a smash-and-grab. A school district after a lockdown drill. A homeowner after a neighbor's break-in. They search fast and call whoever looks credible first.",
        "We build security film pages that explain what film does (holds glass together, delays entry, reduces flying shards) and what it doesn't, and show the attachment systems, certifications and testing that set your installs apart.",
      ],
    },
    points: {
      h: "How we market security film",
      items: [
        { t: "Pages by threat and property", d: "Retail and storefront break-ins, schools and churches, homes and glass doors, government and healthcare, hurricane and storm-prone areas." },
        { t: "Honest explanations", d: "Delay versus prevent, why attachment systems matter, why thickness alone isn't the spec. This builds trust and filters bad-fit leads." },
        { t: "Certifications and dealer status", d: "Armorcoat, 3M Safety & Security, LLumar and other certified dealer credentials front and center." },
        { t: "Demo video content", d: "Break tests and attack demos are some of the most shared content in the industry. We help you use them on your site and YouTube." },
        { t: "Urgent-response campaigns", d: "Ads and landing pages that capture searches after local break-ins, with fast-response messaging." },
        { t: "School and municipal outreach", d: "Content and pages built for safety committees, grants and procurement teams." },
      ],
    },
    asks: {
      h: "What security buyers search",
      items: [
        "security window film for storefronts",
        "smash and grab protection film",
        "school window security film",
        "shatter resistant window film for home",
        "does security window film really work",
        "glass door break-in protection",
      ],
    },
    jargon: [
      { t: "Mil thickness", d: "Film thickness in thousandths of an inch. Safety films start around 4 mil; security films run 8, 14 mil and up." },
      { t: "Attachment systems", d: "Structural silicone (wet glaze) or mechanical frame attachments that anchor the film-glass to the frame." },
      { t: "Forced entry / smash-and-grab", d: "Film that holds broken glass in place so a burglar can't get in quickly." },
      { t: "Blast mitigation", d: "Films and attachment systems tested to standards like ASTM F1642 and GSA criteria to reduce flying glass." },
      { t: "Safety glazing", d: "Films that help existing glass meet impact safety requirements like ANSI Z97.1." },
    ],
    faq: [
      { q: "Can you market our security film without overpromising?", a: "That's the only way we'll do it. Clear, honest claims rank well, convert better and protect you from unhappy customers." },
    ],
  },
  {
    slug: "anti-graffiti-film",
    nav: "Anti-Graffiti Film",
    icon: "spray",
    card: "Sacrificial film for storefronts, transit, elevators and mirrors.",
    title: "Marketing for Anti-Graffiti Film Installers",
    metaTitle: "Marketing for Anti-Graffiti Window Film Companies",
    metaDesc: "Marketing for anti-graffiti film installers: reach property managers, retailers, transit and municipalities dealing with tagging, etching and scratchiti.",
    eyebrow: "Anti-graffiti film",
    lead: "Every property manager who has replaced a tagged storefront pane twice is a buyer. They just don't know sacrificial film exists. We put it in front of them.",
    intro: {
      h: "Sell the math, not just the film",
      p: [
        "Replacing etched glass is expensive and slow. Replacing a sheet of clear anti-graffiti film is quick and cheap. That simple comparison sells the product once buyers see it.",
        "We build pages and campaigns that target the people who pay for vandalism: property managers, retail chains, HOAs, transit agencies, parking structures and municipalities.",
      ],
    },
    points: {
      h: "How we market anti-graffiti film",
      items: [
        { t: "Cost-comparison content", d: "Glass replacement versus film replacement, with typical turnaround times." },
        { t: "Surface pages", d: "Storefront glass, elevator interiors, mirrors, stainless steel, bus shelters and signage." },
        { t: "Maintenance program pages", d: "Ongoing film replacement plans, a recurring-revenue offer worth promoting." },
        { t: "Targeted outreach", d: "Property management firms, business improvement districts and facilities teams in high-vandalism areas." },
        { t: "Before-and-after proof", d: "Tagged film peeled off to reveal clean glass. The most convincing image in the category." },
        { t: "Local search for urgent needs", d: "\"Graffiti removal from glass\" searchers often become anti-graffiti film buyers." },
      ],
    },
    asks: {
      h: "What anti-graffiti buyers search",
      items: [
        "anti graffiti film for windows",
        "how to remove etching from glass",
        "scratched storefront glass replacement cost",
        "graffiti protection for elevators",
        "sacrificial window film",
        "glass etching vandalism prevention",
      ],
    },
    jargon: [
      { t: "Sacrificial film", d: "A clear, replaceable layer that takes the damage so the glass doesn't have to." },
      { t: "Scratchiti and etching", d: "Graffiti scratched or acid-etched into glass, which can't be cleaned off." },
      { t: "Tagging", d: "Spray paint or marker graffiti that sits on the film surface." },
      { t: "Interior vs. exterior", d: "Exterior anti-graffiti film is designed to be swapped out when damaged; interior films last much longer." },
    ],
    faq: [
      { q: "Is anti-graffiti film a big enough market to market on its own?", a: "In dense metros, yes, especially paired with security film. Elsewhere we fold it into your commercial pages and outreach." },
    ],
  },
  {
    slug: "decorative-privacy-film",
    nav: "Decorative & Privacy Film",
    icon: "grid",
    card: "Frosted, dusted crystal, gradient and branded glass graphics.",
    title: "Marketing for Decorative and Privacy Window Film Companies",
    metaTitle: "Marketing for Decorative and Frosted Window Film Companies",
    metaDesc: "Marketing for decorative window film installers: frosted privacy glass, gradient film, logos and glass graphics for offices, healthcare and homes.",
    eyebrow: "Decorative & privacy film",
    lead: "Decorative film sells visually. Interior designers, office managers and homeowners need to see it before they buy it. We put your best glass in front of them.",
    intro: {
      h: "Show it, and it sells itself",
      p: [
        "A conference room with a frosted band and a cut logo. A dental office with gradient privacy film. A bathroom window that lets light in and keeps neighbors out. These are visual purchases.",
        "We build galleries and pages that show every style you offer, and target the people who choose it: office managers, designers, architects, healthcare and homeowners remodeling.",
      ],
    },
    points: {
      h: "How we market decorative film",
      items: [
        { t: "Style galleries", d: "Frosted, dusted crystal, gradient, patterned, colored, white and blackout, cut logos and printed graphics." },
        { t: "Space-based pages", d: "Conference rooms, offices, reception, healthcare exam rooms, bathrooms, front doors and sidelights, showers." },
        { t: "Designer and architect outreach", d: "Pages, swatch requests and content built for the people who specify decorative film." },
        { t: "Branding angle", d: "Logos and brand graphics on glass, sold to marketing and office managers, not just facilities." },
        { t: "Glass door safety markings", d: "Required visibility markings on large glass doors, a steady add-on worth ranking for." },
        { t: "Instagram and Pinterest", d: "The two platforms where decorative film actually gets discovered." },
      ],
    },
    asks: {
      h: "What decorative film buyers search",
      items: [
        "frosted window film for office",
        "conference room glass privacy film",
        "bathroom window privacy film",
        "logo on glass door",
        "gradient frosted film",
        "shower glass privacy frost",
      ],
    },
    jargon: [
      { t: "Frosted / dusted crystal", d: "Translucent films that block views but let daylight through." },
      { t: "Gradient", d: "Film that fades from frosted to clear, often used for privacy at eye level." },
      { t: "Cut vinyl and printed graphics", d: "Logos, patterns and custom designs cut or printed on film." },
      { t: "Switchable smart film", d: "Film that turns from clear to opaque at the flip of a switch, a premium upsell." },
    ],
    faq: [
      { q: "We do mostly decorative work. Is that a fit?", a: "Yes. Decorative-focused companies need more visual content and designer outreach and less local SEO. We adjust the plan." },
    ],
  },
  {
    slug: "solar-skylight-film",
    nav: "Solar & Skylight Film",
    icon: "sun",
    card: "Heat rejection, glare control, skylights, atriums and sunrooms.",
    title: "Marketing for Solar Window Film and Skylight Tinting Companies",
    metaTitle: "Marketing for Solar Window Film and Skylight Tinting",
    metaDesc: "Marketing for solar window film installers: reach buyers searching for heat rejection, glare control, skylight tinting and energy savings.",
    eyebrow: "Solar & skylight film",
    lead: "Solar film sells on comfort and cost: rooms that are actually usable in the afternoon and lower cooling bills. We turn those outcomes into search traffic and estimates.",
    intro: {
      h: "Heat is the problem buyers feel. Film is the answer they don't know about",
      p: [
        "Most people with a scorching sunroom, an atrium that bakes the lobby or a skylight that blinds the kitchen don't know window film solves it. They search the symptom.",
        "We build content around symptoms, then explain film options in plain language: ceramic and spectrally selective films that block heat without darkening, dual-reflective films for maximum rejection, and skylight-specific solutions.",
      ],
    },
    points: {
      h: "How we market solar film",
      items: [
        { t: "Symptom-first content", d: "Hot rooms, hot spots near windows, blinding glare, high cooling bills, faded floors." },
        { t: "Skylight and atrium pages", d: "A strong niche: few competitors rank well for skylight tinting." },
        { t: "Energy savings calculators", d: "Simple estimates of heat reduction and payback to move commercial buyers forward." },
        { t: "Rebate and incentive content", d: "Utility rebates and incentives in your area, where they exist." },
        { t: "Film comparison guides", d: "Ceramic vs. dyed vs. reflective, light vs. dark, interior vs. exterior film." },
        { t: "Seasonal ad timing", d: "Budgets that ramp with the heat in your climate." },
      ],
    },
    asks: {
      h: "What solar film buyers search",
      items: [
        "skylight tinting",
        "how to reduce heat from windows",
        "sunroom too hot",
        "window film energy savings",
        "glare on computer screens from windows",
        "heat rejection window film",
      ],
    },
    jargon: [
      { t: "IR rejection", d: "How much infrared (felt heat) a film blocks. Ceramic films are strong here." },
      { t: "Dual-reflective", d: "Films that are more reflective outside than inside, so the view at night stays clearer." },
      { t: "Glare reduction", d: "The percentage cut in visible glare, the number office buyers care about." },
      { t: "Exterior film", d: "Film installed on the outside surface, often used on skylights and glass that can't take interior film." },
    ],
    faq: [
      { q: "Can you show energy savings claims on our site?", a: "Yes, using manufacturer data and energy modeling where available, presented as estimates. We avoid guarantees that could cause trouble later." },
    ],
  },
  {
    slug: "automotive-tint-ppf",
    nav: "Auto Tint & PPF Shops",
    icon: "car",
    card: "Ceramic auto tint, paint protection film and ceramic coating shops.",
    title: "Marketing for Auto Tint and Paint Protection Film Shops",
    metaTitle: "Marketing for Auto Tint and PPF Shops",
    metaDesc: "Marketing for automotive tint and PPF shops: rank for ceramic tint, paint protection film and ceramic coating, and keep architectural leads separate.",
    eyebrow: "Auto tint & PPF",
    lead: "Many window film companies run an auto bay too. Auto tint and PPF searches are a different market, so we keep them on their own pages, ads and budget.",
    intro: {
      h: "Keep auto and architectural leads from cannibalizing each other",
      p: [
        "If \"window tinting near me\" sends a homeowner to your car tint page, or a Tesla owner to your commercial page, both bounce. We separate the two divisions on your site and in your ads so each lands where it should.",
      ],
    },
    points: {
      h: "How we market auto film",
      items: [
        { t: "Auto-specific pages", d: "Ceramic tint, windshield strips, full windshield, PPF (full front, track pack, full body), ceramic coating." },
        { t: "Tint law content", d: "Legal VLT limits in your state, a top-ranking and evergreen page." },
        { t: "Make and model pages", d: "Tesla, trucks, luxury brands: the vehicles your shop does most." },
        { t: "Instagram and TikTok", d: "Short install videos are the main discovery channel for auto film." },
        { t: "Online booking", d: "Package pricing and booking so customers can pick a slot without calling." },
        { t: "Dealer and fleet pages", d: "Landing pages for dealerships and fleet managers who send repeat work." },
      ],
    },
    asks: {
      h: "What auto film buyers search",
      items: [
        "ceramic tint near me",
        "ppf near me / paint protection film cost",
        "legal tint limit in [state]",
        "Tesla window tint",
        "windshield tint strip",
        "ceramic coating vs ppf",
      ],
    },
    jargon: [
      { t: "Ceramic tint", d: "Non-metallic films with strong heat rejection and no signal interference." },
      { t: "PPF", d: "Paint protection film, clear urethane that protects paint from rock chips." },
      { t: "Computer-cut patterns", d: "Plotter-cut film kits for a precise fit, a quality point buyers respond to." },
    ],
    faq: [
      { q: "We only do automotive. Do you work with auto-only shops?", a: "Our focus is architectural film companies, but we work with shops that do both. For auto-only shops, ask and we'll tell you honestly if we're the right fit." },
    ],
  },
];

// ---------- Home page ----------
export const home = {
  metaTitle: "Window Film Marketing Agency | Marketing & Web Design for Window Tinting Companies",
  metaDesc: "Marketing, AI search optimization and web design built only for window film companies. Get found for residential, commercial, security and decorative film.",
  badge: "Local SEO · AEO · Web Design · Google Ads",
  h1: ["Marketing Agency for ", "Window Film Companies"],
  lead: "We help window tinting and window film installers get found on Google, recommended by AI and booked for more residential, commercial and security film jobs. Websites included.",
  platforms: ["Google Maps", "Google AI Overviews", "ChatGPT", "Gemini", "Perplexity", "Bing & Copilot", "Apple Maps", "Yelp"],
  steps: [
    { t: "Audit", d: "We search your market the way buyers do, on Google and five AI assistants, for every film type you install, and record who shows up." },
    { t: "Fix the foundation", d: "Website, Google Business Profile, listings and schema cleaned up so every source tells the same, accurate story." },
    { t: "Build film-specific pages", d: "A page for every film and every core city, with real projects, specs and answers." },
    { t: "Grow and track", d: "Reviews, links, ads where they make sense, and a monthly report by booked estimate." },
  ],
  compare: {
    rows: [
      ["Knows the product", "Learns what \"window tinting\" means on your dime", "Knows VLT, TSER, mil thickness, attachment systems and sacrificial film"],
      ["Website structure", "Home, About, Services, Contact", "A page per film type, per building type and per city"],
      ["Keywords", "\"window tint\", which matches car tint and DIY kits", "Split by buyer: residential, commercial, security, decorative, auto"],
      ["Reviews", "Ask for stars", "Ask for the film and the result, which AI quotes back"],
      ["AI search", "Not on the radar", "Tested monthly across ChatGPT, Gemini, Perplexity, Claude and AI Overviews"],
      ["Reporting", "Clicks and impressions", "Calls, estimate requests and booked jobs by film type"],
    ],
  },
  faq: [
    { q: "Do you only work with window film companies?", a: "Yes. Window tinting and film installers (residential, commercial, security, decorative and auto) are the only businesses we market. That focus is the whole point." },
    { q: "Do you work with more than one company in the same market?", a: "We limit how many competing companies we work with in a market, so we're never splitting the same searches between clients. Ask us whether your area is open." },
    { q: "Do I need a new website?", a: "Not always. If your site is fast and well structured, we'll build on it. If it's slow, thin or built on a template that fights you, a rebuild is usually cheaper than patching it." },
    { q: "What is AI search optimization (AEO)?", a: "Making your business easy for AI assistants like ChatGPT, Gemini and Google's AI Overviews to understand and recommend: accurate listings, clear service pages, structured data and specific reviews." },
    { q: "How long until we see more leads?", a: "Fixes to your Google Business Profile and listings can help within weeks. New service pages and rankings usually build over three to six months. Ads can produce calls in days." },
    { q: "Are we locked into a long contract?", a: "No. Month-to-month after the initial setup. You own your website, content, listings and ad accounts." },
    { q: "Do you work with manufacturer dealers?", a: "Yes. We work with certified dealers of 3M, LLumar, Solar Gard, Armorcoat, Madico, Huper Optik, XPEL and other brands, and make sure your dealer status helps your marketing instead of sending traffic to the manufacturer." },
  ],
  sim: {
    questions: [
      { q: "Who installs security window film for retail storefronts in Phoenix?", city: "Phoenix", film: "security window film", review: "a store owner says the 8 mil security film held after an attempted smash-and-grab", site: "a storefront security film page lists mil thickness and attachment systems" },
      { q: "What's the best company for home window tinting to stop my hardwood floors fading in Austin?", city: "Austin", film: "residential UV film", review: "homeowners mention 99% UV rejection and floors that stopped fading", site: "a home tinting page answers low-e glass and warranty questions" },
      { q: "Who can frost our conference room glass with our logo in Denver?", city: "Denver", film: "decorative frosted film", review: "an office manager praises the frosted band and cut logo", site: "a gallery shows frosted, gradient and logo work in offices" },
      { q: "Is there a company in Los Angeles that installs anti-graffiti film on storefront windows?", city: "Los Angeles", film: "anti-graffiti film", review: "a property manager says tagged film was swapped in a day", site: "an anti-graffiti page explains sacrificial film and replacement" },
    ],
    channels: ["ChatGPT", "Gemini", "Perplexity", "Google AI Overviews", "Google Maps"],
    signals: [
      { key: "pages", t: "Film-specific service page", d: "A real page for this film type" },
      { key: "gbp", t: "Complete Google Business Profile", d: "Right category, services, photos" },
      { key: "reviews", t: "Reviews that name the film", d: "Specific, recent, local" },
      { key: "projects", t: "Project gallery with photos", d: "Proof of similar jobs" },
      { key: "listings", t: "Consistent listings + schema", d: "Same facts everywhere" },
    ],
  },
};

export const about = {
  metaTitle: "About | Window Film Marketing Agency",
  metaDesc: "Window Film Marketing Agency markets one kind of business: window tinting and window film companies. Learn how we work.",
  lead: "Window film is a specialized trade with its own buyers, products and vocabulary. Generic agencies spend months learning it on your budget. We start already knowing it.",
  why: [
    "Most marketing agencies treat a window film company like any other contractor. They build a five-page site, target \"window tint\" and wonder why the leads are car owners and DIY shoppers.",
    "Window film doesn't work that way. A homeowner worried about fading, a facilities manager fighting glare and heat, a retailer hit by a smash-and-grab and an interior designer specifying frosted glass are four completely different buyers. Each needs different pages, different words and different proof.",
    "Window Film Marketing Agency exists to market that difference. We build websites, local SEO, AI search visibility, ads and review systems for window film companies, and nothing else.",
  ],
  values: [
    { t: "We speak film", d: "VLT, TSER, SHGC, mil thickness, attachment systems, low-e compatibility, sacrificial film. You won't have to explain your product to us." },
    { t: "Booked jobs, not vanity metrics", d: "We report on calls, estimate requests and won jobs by film type. Traffic is only useful if it books." },
    { t: "Honest claims", d: "No overpromising on security film, no fake reviews, no spammy tactics that put your Google profile at risk." },
    { t: "You own everything", d: "Your domain, website, content, Google Business Profile and ad accounts stay yours. Month-to-month after setup." },
  ],
};
