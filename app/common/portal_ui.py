"""Custom Developer Portal (`/`), Botanical Swagger UI (`/docs`), and Scalar Reference (`/scalar`)."""
from __future__ import annotations

import json

from app.core.config import settings

# ==============================================================================
# 1. SWAGGER UI ("/docs") — Botanical Dark Theme (No AI Slop)
# ==============================================================================
SWAGGER_BOTANICAL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --bg: #09090b; --surface: #111113; --elevated: #18181b;
  --border: #27272a; --text: #f4f4f5; --muted: #71717a;
  --accent: #10b981; --get: #38bdf8; --post: #34d399; --put: #fbbf24; --del: #f87171;
}
html, body { background: var(--bg) !important; color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important; margin: 0; -webkit-font-smoothing: antialiased; }
.swagger-ui { color: var(--text) !important; font-family: 'Plus Jakarta Sans', sans-serif !important; }
.swagger-ui .topbar { display: none !important; }
.swagger-ui .wrapper { max-width: 1360px !important; padding: 20px 28px 64px !important; }
.swagger-ui .info { margin: 16px 0 20px !important; }
.swagger-ui .info .title { color: var(--text) !important; font-weight: 700 !important; font-size: 22px !important; letter-spacing: -0.02em !important; }
.swagger-ui .info .title small { background: rgba(16,185,129,.1) !important; border: 1px solid rgba(16,185,129,.3) !important; border-radius: 4px !important; padding: 2px 8px !important; }
.swagger-ui .info .title small pre { color: var(--accent) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; }
.swagger-ui .info p, .swagger-ui .markdown p { color: var(--muted) !important; font-size: 13px !important; }
.swagger-ui .scheme-container { background: var(--surface) !important; border: 1px solid var(--border) !important; box-shadow: none !important; border-radius: 6px !important; padding: 12px 16px !important; margin: 0 0 20px !important; }
.swagger-ui .opblock-tag { color: var(--text) !important; font-weight: 600 !important; font-size: 14px !important; letter-spacing: -0.015em !important; border-bottom: 1px solid var(--border) !important; padding: 12px 4px !important; margin: 0 !important; }
.swagger-ui .opblock { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; box-shadow: none !important; margin: 6px 0 !important; }
.swagger-ui .opblock .opblock-summary { border-bottom: 1px solid transparent !important; padding: 8px 12px !important; }
.swagger-ui .opblock.is-open .opblock-summary { border-bottom-color: var(--border) !important; }
.swagger-ui .opblock .opblock-summary-method { font-family: 'JetBrains Mono', monospace !important; font-size: 10px !important; font-weight: 700 !important; min-width: 56px !important; padding: 3px 8px !important; border-radius: 4px !important; text-shadow: none !important; }
.swagger-ui .opblock.opblock-get .opblock-summary-method { background: rgba(56,189,248,.1) !important; color: var(--get) !important; border: 1px solid rgba(56,189,248,.3) !important; }
.swagger-ui .opblock.opblock-post .opblock-summary-method { background: rgba(52,211,153,.1) !important; color: var(--post) !important; border: 1px solid rgba(52,211,153,.3) !important; }
.swagger-ui .opblock.opblock-put .opblock-summary-method, .swagger-ui .opblock.opblock-patch .opblock-summary-method { background: rgba(251,191,36,.1) !important; color: var(--put) !important; border: 1px solid rgba(251,191,36,.3) !important; }
.swagger-ui .opblock.opblock-delete .opblock-summary-method { background: rgba(248,113,113,.1) !important; color: var(--del) !important; border: 1px solid rgba(248,113,113,.3) !important; }
.swagger-ui .opblock .opblock-summary-path { color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important; }
.swagger-ui .opblock-section-header { background: var(--elevated) !important; box-shadow: none !important; border-top: 1px solid var(--border) !important; border-bottom: 1px solid var(--border) !important; }
.swagger-ui table thead tr th, .swagger-ui table thead tr td { color: var(--muted) !important; border-bottom: 1px solid var(--border) !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.04em; }
.swagger-ui .parameter__name { color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important; }
.swagger-ui .parameter__type, .swagger-ui .prop-type { color: var(--accent) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 11px !important; }
.swagger-ui input[type=text], .swagger-ui input[type=password], .swagger-ui textarea, .swagger-ui select { background: var(--bg) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
.swagger-ui input:focus, .swagger-ui textarea:focus { border-color: var(--accent) !important; outline: none !important; }
.swagger-ui .btn { background: var(--elevated) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 4px !important; box-shadow: none !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-size: 12px !important; }
.swagger-ui .btn.execute { background: var(--accent) !important; color: #022c22 !important; border-color: var(--accent) !important; font-weight: 700 !important; }
.swagger-ui .btn.authorize { color: var(--accent) !important; border-color: rgba(16,185,129,.4) !important; background: rgba(16,185,129,.08) !important; }
.swagger-ui .btn.authorize svg { fill: var(--accent) !important; }
.swagger-ui pre.microlight, .swagger-ui .highlight-code pre { background: var(--bg) !important; border: 1px solid var(--border) !important; border-radius: 5px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
.swagger-ui section.models { border: 1px solid var(--border) !important; background: var(--surface) !important; border-radius: 6px !important; }
.swagger-ui .model-box, .swagger-ui .model { background: var(--bg) !important; color: var(--text) !important; font-family: 'JetBrains Mono', monospace !important; }
.swagger-ui .dialog-ux .modal-ux { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; box-shadow: none !important; }
.swagger-ui svg.arrow { fill: var(--muted) !important; }

/* Nav Bar */
.bp-bar { position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 52px; padding: 0 20px; background: rgba(9,9,11,.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); }
.bp-brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 13px; letter-spacing: -0.015em; color: var(--text); }
.bp-logo { width: 26px; height: 26px; background: #f4f4f5; color: #09090b; border-radius: 5px; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 700; }
.bp-right { display: flex; align-items: center; gap: 8px; }
.bp-seg { display: inline-flex; align-items: center; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 2px; gap: 2px; }
.bp-seg-lbl { padding: 0 8px; font-size: 11px; color: var(--muted); font-family: 'JetBrains Mono', monospace; }
.bp-seg button { background: transparent; border: 1px solid transparent; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 4px; cursor: pointer; }
.bp-seg button:hover { color: var(--text); }
.bp-seg button.on { background: rgba(16,185,129,.12); color: #34d399; border-color: rgba(16,185,129,.35); }
.bp-auth { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--muted); display: flex; align-items: center; gap: 6px; }
.bp-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--muted); }
.bp-dot.ok { background: #34d399; }
.bp-link { display: flex; align-items: center; height: 28px; padding: 0 10px; background: var(--surface); border: 1px solid var(--border); border-radius: 4px; color: var(--muted); text-decoration: none; font-size: 11px; font-family: 'JetBrains Mono', monospace; }
.bp-link:hover { color: var(--text); border-color: var(--accent); }
"""


def render_swagger_html(openapi_url: str, title: str) -> str:
    cfg = {
        "owner_user": settings.SEED_OWNER_USERNAME,
        "owner_pass": settings.SEED_OWNER_PASSWORD,
        "karyawan_user": settings.SEED_KARYAWAN_USERNAME,
        "karyawan_pass": settings.SEED_KARYAWAN_PASSWORD,
        "login_url": f"{settings.API_V1_PREFIX}/auth/login",
    }
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — Swagger UI</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <style>{SWAGGER_BOTANICAL_CSS}</style>
</head>
<body>
  <header class="bp-bar">
    <div class="bp-brand">
      <div class="bp-logo">HS</div>
      {settings.APP_NAME}
      <span style="color:#71717a;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:400;">/ Swagger</span>
    </div>
    <div class="bp-right">
      <div class="bp-auth"><span class="bp-dot" id="dot"></span><span id="auth-lbl">NO TOKEN</span></div>
      <div class="bp-seg">
        <span class="bp-seg-lbl">Role:</span>
        <button id="b-owner"    onclick="bpSwitch('owner')">OWNER</button>
        <button id="b-karyawan" onclick="bpSwitch('karyawan')">KARYAWAN</button>
        <button onclick="bpClear()">Clear</button>
      </div>
      <a class="bp-link" href="/">Portal</a>
      <a class="bp-link" href="/docs" style="color:#f4f4f5;border-color:#34d399;">/docs</a>
      <a class="bp-link" href="/scalar">/scalar</a>
    </div>
  </header>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    const C = {json.dumps(cfg)};
    const ui = SwaggerUIBundle({{
      url: {json.dumps(openapi_url)}, dom_id: '#swagger-ui',
      deepLinking: true, docExpansion: 'none', filter: true,
      displayRequestDuration: true, persistAuthorization: true, tryItOutEnabled: true,
      onComplete: () => {{ const t = localStorage.getItem('bp_token'), r = localStorage.getItem('bp_role'); if (t) apply(t, r); }}
    }});
    function apply(t, r) {{
      try {{ ui.preauthorizeApiKey('JWT Bearer', t); }} catch(_) {{}}
      document.getElementById('auth-lbl').textContent = 'JWT: ' + (r||'active').toUpperCase();
      document.getElementById('auth-lbl').style.color = '#34d399';
      document.getElementById('dot').className = 'bp-dot ok';
      document.getElementById('b-owner').classList.toggle('on', r==='owner');
      document.getElementById('b-karyawan').classList.toggle('on', r==='karyawan');
    }}
    async function bpSwitch(role) {{
      const r = await fetch(C.login_url, {{method:'POST',headers:{{'Content-Type':'application/json'}},
        body:JSON.stringify({{username:role==='owner'?C.owner_user:C.karyawan_user,password:role==='owner'?C.owner_pass:C.karyawan_pass}})}});
      const b = await r.json();
      if (b?.data?.access_token) {{ localStorage.setItem('bp_token',b.data.access_token); localStorage.setItem('bp_role',b.data.role); apply(b.data.access_token,b.data.role); }}
    }}
    function bpClear() {{
      localStorage.removeItem('bp_token'); localStorage.removeItem('bp_role');
      try {{ ui.authActions.logout(['JWT Bearer']); }} catch(_) {{}}
      document.getElementById('auth-lbl').textContent='NO TOKEN'; document.getElementById('auth-lbl').style.color='';
      document.getElementById('dot').className='bp-dot';
      document.getElementById('b-owner').classList.remove('on'); document.getElementById('b-karyawan').classList.remove('on');
    }}
  </script>
</body>
</html>"""


# ==============================================================================
# 2. SCALAR API REFERENCE ("/scalar")
# ==============================================================================
def render_scalar_html(openapi_url: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title} — Scalar</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
    body{{background:#09090b;color:#f4f4f5;font-family:'Plus Jakarta Sans',sans-serif;}}
    :root,.dark-mode{{
      --scalar-font:'Plus Jakarta Sans',-apple-system,sans-serif!important;
      --scalar-font-code:'JetBrains Mono',monospace!important;
      --scalar-background-1:#09090b!important;--scalar-background-2:#111113!important;
      --scalar-background-3:#18181b!important;--scalar-background-accent:rgba(16,185,129,.1)!important;
      --scalar-color-1:#f4f4f5!important;--scalar-color-2:#a1a1aa!important;--scalar-color-3:#71717a!important;
      --scalar-color-accent:#10b981!important;--scalar-border-color:#27272a!important;
      --scalar-color-green:#34d399!important;--scalar-color-blue:#38bdf8!important;
      --scalar-color-orange:#fbbf24!important;--scalar-color-red:#f87171!important;
      --scalar-radius:5px!important;
    }}
    .bar{{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;height:48px;padding:0 20px;background:rgba(9,9,11,.95);backdrop-filter:blur(10px);border-bottom:1px solid #27272a;}}
    .bar-brand{{display:flex;align-items:center;gap:10px;font-weight:700;font-size:13px;letter-spacing:-0.015em;color:#f4f4f5;}}
    .bar-logo{{width:24px;height:24px;background:#f4f4f5;color:#09090b;border-radius:4px;display:flex;align-items:center;justify-content:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;}}
    .bar-nav{{display:flex;gap:4px;}}
    .bar-nav a{{color:#71717a;text-decoration:none;padding:4px 10px;border:1px solid #27272a;border-radius:4px;background:#111113;font-family:'JetBrains Mono',monospace;font-size:11px;}}
    .bar-nav a:hover,.bar-nav a.cur{{color:#f4f4f5;border-color:#10b981;}}
  </style>
</head>
<body>
  <div class="bar">
    <div class="bar-brand"><div class="bar-logo">HS</div>{settings.APP_NAME}<span style="color:#71717a;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:400;">/ Scalar</span></div>
    <nav class="bar-nav"><a href="/">Portal</a><a href="/docs">/docs</a><a href="/scalar" class="cur">/scalar</a></nav>
  </div>
  <script id="api-reference" data-url={json.dumps(openapi_url)}></script>
  <script>
    document.getElementById('api-reference').dataset.configuration=JSON.stringify({{
      theme:'none',darkMode:true,layout:'modern',
      defaultHttpClient:{{targetKey:'shell',clientKey:'curl'}},
      authentication:{{preferredSecurityScheme:'JWT Bearer',http:{{bearer:{{token:localStorage.getItem('bp_token')||''}}}}}}
    }});
  </script>
  <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>"""


# ==============================================================================
# 3. DEVELOPER PORTAL ("/") — Interactive No-AI-Slop 3-Pane Workspace
# ==============================================================================
def render_portal_html() -> str:
    cfg = {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "api_prefix": settings.API_V1_PREFIX,
        "owner_user": settings.SEED_OWNER_USERNAME,
        "owner_pass": settings.SEED_OWNER_PASSWORD,
        "karyawan_user": settings.SEED_KARYAWAN_USERNAME,
        "karyawan_pass": settings.SEED_KARYAWAN_PASSWORD,
    }
    return PORTAL_TEMPLATE.replace("__CFG__", json.dumps(cfg))


PORTAL_TEMPLATE = r"""<!DOCTYPE html>
<html lang="id" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Developer Portal — Hidroponik Selada API</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts: Plus Jakarta Sans & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>

    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        zinc: {
                            850: '#1f1f23',
                            925: '#121215',
                            950: '#09090b',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(161, 161, 170, 0.25); }
        ::-webkit-scrollbar-thumb:hover { background: rgba(161, 161, 170, 0.45); }
        .json-key { color: #0284c7; } .dark .json-key { color: #e4e4e7; }
        .json-str { color: #15803d; } .dark .json-str { color: #4ade80; }
        .json-num { color: #b45309; } .dark .json-num { color: #fbbf24; }
        .json-bool { color: #7e22ce; } .dark .json-bool { color: #c084fc; }
        .json-null { color: #71717a; }
    </style>
</head>
<body class="bg-white text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100 font-sans antialiased selection:bg-zinc-900 selection:text-white dark:selection:bg-zinc-100 dark:selection:text-zinc-900 overflow-hidden h-screen flex flex-col">

    <!-- ═══════════════════════════════════════════════
         TOP BAR (Crisp 1px Grid Border, No Slop)
    ════════════════════════════════════════════════ -->
    <header class="h-14 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 z-30 flex items-center justify-between px-4 lg:px-5 shrink-0">
        <!-- Left: Brand Identity & Spec Metadata -->
        <div class="flex items-center gap-3">
            <button id="mobileMenuBtn" type="button" class="lg:hidden p-1.5 rounded text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900 cursor-pointer">
                <i data-lucide="menu" class="w-4 h-4"></i>
            </button>
            <div class="flex items-center gap-3">
                <div class="w-7 h-7 rounded bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 flex items-center justify-center font-mono font-bold text-xs tracking-tighter">
                    HS
                </div>
                <div class="flex items-center gap-2">
                    <span id="topbar-name" class="font-semibold text-sm tracking-tight">Lettuce Management API</span>
                    <span class="text-zinc-300 dark:text-zinc-700">/</span>
                    <span class="font-mono text-xs text-zinc-500 dark:text-zinc-400">Dev Portal</span>
                    <span id="topbar-ver" class="hidden sm:inline-block text-[11px] font-mono px-1.5 py-0.5 rounded bg-zinc-100 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 border border-zinc-200 dark:border-zinc-800">v1.0.0</span>
                    <span id="topbar-env" class="hidden md:inline-block text-[11px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">OAS 3.1</span>
                </div>
            </div>
        </div>

        <!-- Center: Command Search Input -->
        <div class="flex-1 max-w-sm mx-4 hidden md:block">
            <div class="relative flex items-center">
                <i data-lucide="search" class="w-3.5 h-3.5 absolute left-3 text-zinc-400 pointer-events-none"></i>
                <input 
                    type="text" 
                    id="searchInput" 
                    placeholder="Filter 20 endpoints, path, atau tag..." 
                    class="w-full pl-8 pr-8 py-1.5 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 placeholder:text-zinc-400 dark:placeholder:text-zinc-500 focus:outline-none focus:border-zinc-400 dark:focus:border-zinc-600 transition-colors"
                >
                <kbd class="absolute right-2 text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-200/70 dark:bg-zinc-800 text-zinc-500 dark:text-zinc-400">/</kbd>
            </div>
        </div>

        <!-- Right: Telemetry, Role Quick-Switch, Spec Loader & Theme -->
        <div class="flex items-center gap-2">
            <!-- Live Telemetry Indicators -->
            <div class="hidden xl:flex items-center gap-1.5">
                <button type="button" onclick="refreshHealth()" title="Klik untuk test /health" class="flex items-center gap-1.5 px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-xs font-mono cursor-pointer hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors">
                    <span id="dot-db" class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
                    <span class="text-zinc-500">DB</span>
                    <span id="val-db" class="font-semibold text-zinc-700 dark:text-zinc-300">OK</span>
                </button>
                <button type="button" onclick="selectEndpoint('POST /api/v1/diagnosis/predict')" title="Lompat ke AI Diagnosis Kesehatan Selada" class="flex items-center gap-1.5 px-2.5 py-1 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-xs font-mono cursor-pointer hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors">
                    <span id="dot-ai" class="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0"></span>
                    <span class="text-zinc-500">AI</span>
                    <span id="val-ai" class="font-semibold text-zinc-700 dark:text-zinc-300">MODEL_READY</span>
                </button>
                <span id="val-ms" class="text-[11px] font-mono text-zinc-400 px-1">18 ms</span>
            </div>

            <!-- Role Segmented Switcher (like Swagger/Portal bar) -->
            <div class="hidden sm:flex items-center bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded p-0.5 gap-0.5">
                <span class="px-2 text-[10px] font-mono uppercase text-zinc-400">Role:</span>
                <button type="button" id="topRoleOwner" onclick="quickLogin('owner')" class="px-2 py-1 rounded text-[11px] font-mono font-semibold transition-colors cursor-pointer text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100">
                    OWNER
                </button>
                <button type="button" id="topRoleKaryawan" onclick="quickLogin('karyawan')" class="px-2 py-1 rounded text-[11px] font-mono font-semibold transition-colors cursor-pointer text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100">
                    KARYAWAN
                </button>
            </div>

            <!-- Authorize Modal Button -->
            <button type="button" id="authModalBtn" onclick="toggleAuthModal(true)" class="flex items-center gap-2 px-3 py-1.5 rounded text-xs font-mono font-medium border transition-colors bg-zinc-50 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 cursor-pointer">
                <span id="authStatusDot" class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                <i data-lucide="key" class="w-3.5 h-3.5 text-zinc-500"></i>
                <span id="authStatusText">Auth: OWNER</span>
            </button>

            <!-- Fetch / Load OpenAPI Spec Button -->
            <button type="button" onclick="toggleSpecModal(true)" title="Fetch /openapi.json atau muat spesifikasi OpenAPI" class="hidden md:flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors cursor-pointer">
                <i data-lucide="file-json" class="w-3.5 h-3.5"></i>
                <span>/openapi.json</span>
            </button>

            <!-- Docs Links -->
            <a href="/docs" class="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors">
                /docs
            </a>
            <a href="/scalar" class="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded text-xs font-mono border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:border-zinc-400 dark:hover:border-zinc-600 transition-colors">
                /scalar
            </a>

            <!-- Theme Switcher -->
            <button type="button" id="themeToggleBtn" onclick="toggleTheme()" class="p-1.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer" title="Toggle Dark/Light Mode">
                <i data-lucide="sun" class="w-3.5 h-3.5 hidden dark:block"></i>
                <i data-lucide="moon" class="w-3.5 h-3.5 block dark:hidden"></i>
            </button>
        </div>
    </header>

    <!-- ═══════════════════════════════════════════════
         MAIN WORKSPACE (Sidebar + Center Doc + Right Runner)
    ════════════════════════════════════════════════ -->
    <div class="flex-1 flex overflow-hidden relative">

        <!-- Sidebar Backdrop (Mobile) -->
        <div id="sidebarOverlay" class="fixed inset-0 bg-black/60 z-20 hidden lg:hidden"></div>

        <!-- Left Pane: High-Density Endpoint Directory -->
        <aside id="sidebar" class="w-64 border-r border-zinc-200 dark:border-zinc-800 bg-zinc-50/60 dark:bg-zinc-950 flex flex-col z-20 fixed lg:static inset-y-0 left-0 -translate-x-full lg:translate-x-0 transition-transform duration-200 shrink-0">
            <!-- Mobile Search -->
            <div class="p-2.5 border-b border-zinc-200 dark:border-zinc-800 md:hidden">
                <input type="text" id="mobileSearchInput" placeholder="Filter endpoints..." class="w-full px-2.5 py-1.5 text-xs font-mono rounded bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 focus:outline-none">
            </div>

            <!-- Directory Tree -->
            <div id="sidebarNav" class="flex-1 overflow-y-auto py-3.5 px-2.5 space-y-5">
                <!-- Populated dynamically from OAS -->
            </div>

            <!-- Spec Footer -->
            <div class="p-3 border-t border-zinc-200 dark:border-zinc-800 flex items-center justify-between text-[11px] font-mono text-zinc-500">
                <span id="sidebarEndpointCount">20 Endpoints</span>
                <button type="button" onclick="downloadSpec()" class="text-zinc-800 dark:text-zinc-200 hover:underline flex items-center gap-1 cursor-pointer">
                    <i data-lucide="arrow-down-to-line" class="w-3 h-3"></i>
                    openapi.json
                </button>
            </div>
        </aside>

        <!-- Center & Right Panes -->
        <main class="flex-1 flex flex-col lg:flex-row overflow-y-auto lg:overflow-hidden">
            
            <!-- Center Pane: Specification & Interactive Schema Table -->
            <div id="docPanel" class="flex-1 lg:overflow-y-auto px-5 py-7 sm:px-8 lg:px-11 max-w-3xl mx-auto w-full space-y-8">
                <!-- Dynamically rendered by JS -->
            </div>

            <!-- Right Pane: Request Console & Live Inspector -->
            <div class="w-full lg:w-[460px] xl:w-[520px] border-t lg:border-t-0 lg:border-l border-zinc-200 dark:border-zinc-800 bg-zinc-50/80 dark:bg-zinc-925 lg:overflow-y-auto flex flex-col shrink-0 divide-y divide-zinc-200 dark:divide-zinc-800">
                
                <!-- Section 1: Request Runner Bar -->
                <div class="p-4 sm:p-5 space-y-3 bg-white dark:bg-zinc-950">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-mono uppercase tracking-wider text-zinc-400">Request Runner</span>
                        <div class="flex items-center gap-2">
                            <span id="securityBadge" class="text-[11px] font-mono text-zinc-500">Authorization: Bearer</span>
                        </div>
                    </div>

                    <!-- Endpoint Target Bar -->
                    <div class="flex items-stretch border border-zinc-200 dark:border-zinc-800 rounded overflow-hidden bg-zinc-50 dark:bg-zinc-900">
                        <span id="consoleMethodBadge" class="px-2.5 py-2 text-[11px] font-mono font-semibold uppercase flex items-center border-r border-zinc-200 dark:border-zinc-800 shrink-0 text-emerald-600 dark:text-emerald-400">POST</span>
                        <code id="consoleUrlPreview" class="px-3 py-2 text-xs font-mono text-zinc-700 dark:text-zinc-300 truncate select-all flex-1 flex items-center">/api/v1/auth/login</code>
                        <button type="button" id="sendRequestBtn" onclick="executeApiRequest()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 dark:bg-emerald-500 dark:hover:bg-emerald-400 text-white dark:text-zinc-950 font-mono text-xs font-semibold flex items-center gap-1.5 transition-colors shrink-0 cursor-pointer">
                            <span>Send</span>
                            <i data-lucide="corner-down-left" class="w-3 h-3"></i>
                        </button>
                    </div>
                </div>

                <!-- Section 2: Client Code Generator -->
                <div class="flex flex-col bg-white dark:bg-zinc-950">
                    <div class="px-4 py-2 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/70 dark:bg-zinc-900/50">
                        <div class="flex items-center gap-1" id="langTabs">
                            <button type="button" onclick="switchCodeLang('curl')" data-lang="curl" class="lang-tab px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors bg-zinc-200/80 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 cursor-pointer">cURL</button>
                            <button type="button" onclick="switchCodeLang('js')" data-lang="js" class="lang-tab px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 cursor-pointer">Fetch</button>
                            <button type="button" onclick="switchCodeLang('python')" data-lang="python" class="lang-tab px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 cursor-pointer">Python (httpx)</button>
                            <button type="button" onclick="switchCodeLang('laravel')" data-lang="laravel" class="lang-tab px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 cursor-pointer">Laravel Http</button>
                        </div>
                        <button type="button" onclick="copyCodeSnippet()" class="text-[11px] font-mono text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 flex items-center gap-1 px-2 py-1 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer">
                            <i data-lucide="copy" class="w-3 h-3"></i>
                            <span>Copy</span>
                        </button>
                    </div>
                    <pre id="codeSnippetBox" class="p-4 text-xs font-mono leading-relaxed overflow-x-auto text-zinc-800 dark:text-zinc-300 max-h-60 whitespace-pre"></pre>
                </div>

                <!-- Section 3: HTTP Response Inspector -->
                <div class="flex-1 flex flex-col bg-white dark:bg-zinc-950 min-h-0">
                    <div class="px-4 py-2.5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between bg-zinc-50/70 dark:bg-zinc-900/50">
                        <div class="flex items-center gap-2.5">
                            <span class="text-[11px] font-mono uppercase tracking-wider text-zinc-400">Response</span>
                            <div id="responseMeta" class="flex items-center gap-2"></div>
                        </div>
                        <div class="flex items-center gap-1.5">
                            <select id="mockStatusSelect" onchange="previewSchemaByStatus(this.value)" class="text-[11px] font-mono bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded px-2 py-1 text-zinc-700 dark:text-zinc-300 focus:outline-none cursor-pointer" title="Preview Response Schema">
                            </select>
                            <button type="button" onclick="copyResponseJson()" class="p-1 text-zinc-400 hover:text-zinc-800 dark:hover:text-zinc-200 rounded hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors cursor-pointer" title="Copy Response JSON">
                                <i data-lucide="clipboard" class="w-3.5 h-3.5"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Request In-Flight State -->
                    <div id="responseLoading" class="hidden py-16 flex-col items-center justify-center gap-2 text-zinc-400">
                        <div class="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                        <span class="text-[11px] font-mono">Executing HTTP request...</span>
                    </div>

                    <!-- Formatted JSON Output -->
                    <pre id="responseJsonBox" class="p-4 text-xs font-mono leading-relaxed overflow-auto flex-1 min-h-0"></pre>
                </div>

            </div>
        </main>
    </div>

    <!-- ═══════════════════════════════════════════════
         AUTH MODAL (Quick Role Login + Custom JWT)
    ════════════════════════════════════════════════ -->
    <div id="authModal" class="fixed inset-0 bg-black/70 z-50 hidden items-center justify-center p-4">
        <div class="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-md max-w-md w-full p-5 shadow-2xl space-y-4">
            <div class="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
                <div>
                    <h3 class="font-semibold text-sm">Authentication Credentials</h3>
                    <p class="text-xs text-zinc-500 font-mono mt-0.5">Scheme: HTTP Bearer (JWT) · Tabel `users`</p>
                </div>
                <button type="button" onclick="toggleAuthModal(false)" class="p-1 rounded text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 cursor-pointer">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>

            <div class="space-y-3">
                <p class="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    Login langsung dengan akun dari tabel <code class="font-mono px-1 py-0.5 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-[11px]">users</code> via <code class="font-mono px-1 py-0.5 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded text-[11px]">POST /api/v1/auth/login</code>:
                </p>

                <!-- Direct DB Credential Form -->
                <div class="space-y-2 p-3 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50/70 dark:bg-zinc-900/50">
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-zinc-500 mb-1">Username</label>
                            <input type="text" id="authUsernameInput" placeholder="owner / karyawan" class="w-full px-2.5 py-1.5 text-xs font-mono rounded bg-white dark:bg-zinc-950 border border-zinc-300 dark:border-zinc-800 focus:outline-none focus:border-emerald-500">
                        </div>
                        <div>
                            <label class="block text-[10px] font-mono uppercase tracking-wider text-zinc-500 mb-1">Password</label>
                            <input type="password" id="authPasswordInput" placeholder="••••••••" onkeydown="if(event.key==='Enter'){event.preventDefault();loginWithCredentials();}" class="w-full px-2.5 py-1.5 text-xs font-mono rounded bg-white dark:bg-zinc-950 border border-zinc-300 dark:border-zinc-800 focus:outline-none focus:border-emerald-500">
                        </div>
                    </div>
                    <p id="authModalError" class="hidden text-[11px] font-mono text-rose-500"></p>
                    <button type="button" onclick="loginWithCredentials()" class="w-full py-2 rounded text-xs font-mono font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors cursor-pointer">
                        Login ke Database (/api/v1/auth/login)
                    </button>
                </div>

                <!-- Quick role login buttons -->
                <div class="grid grid-cols-2 gap-2">
                    <button type="button" onclick="quickLogin('owner')" id="qbtn-owner" class="flex items-center justify-center gap-2 py-2.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 hover:border-amber-500/60 hover:bg-amber-500/5 transition-colors cursor-pointer">
                        <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                        Quick OWNER
                    </button>
                    <button type="button" onclick="quickLogin('karyawan')" id="qbtn-karyawan" class="flex items-center justify-center gap-2 py-2.5 rounded border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 text-xs font-mono font-semibold text-zinc-700 dark:text-zinc-300 hover:border-emerald-500/60 hover:bg-emerald-500/5 transition-colors cursor-pointer">
                        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                        Quick KARYAWAN
                    </button>
                </div>

                <div class="flex items-center gap-2 text-[11px] font-mono text-zinc-400">
                    <div class="flex-1 h-px bg-zinc-200 dark:bg-zinc-800"></div>
                    <span>atau token JWT manual</span>
                    <div class="flex-1 h-px bg-zinc-200 dark:bg-zinc-800"></div>
                </div>

                <div>
                    <label class="block text-[11px] font-mono uppercase tracking-wider text-zinc-500 mb-1.5">Bearer Token</label>
                    <input 
                        type="text" 
                        id="bearerTokenInput" 
                        placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
                        class="w-full px-3 py-2 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-300 dark:border-zinc-800 focus:outline-none focus:border-zinc-500"
                    >
                </div>
            </div>

            <div class="flex items-center justify-end gap-2 pt-2 border-t border-zinc-200 dark:border-zinc-800">
                <button type="button" onclick="clearAuthToken()" class="px-3 py-1.5 rounded text-xs font-mono text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 transition-colors cursor-pointer">
                    Revoke Token
                </button>
                <button type="button" onclick="saveAuthToken()" class="px-3.5 py-1.5 rounded text-xs font-mono font-medium bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 hover:opacity-90 transition-opacity cursor-pointer">
                    Save Credentials
                </button>
            </div>
        </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         OPENAPI.JSON LOADER MODAL
    ════════════════════════════════════════════════ -->
    <div id="specModal" class="fixed inset-0 bg-black/70 z-50 hidden items-center justify-center p-4">
        <div class="bg-white dark:bg-zinc-950 border border-zinc-200 dark:border-zinc-800 rounded-md max-w-lg w-full p-5 shadow-2xl space-y-4">
            <div class="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
                <div>
                    <h3 class="font-semibold text-sm">OpenAPI 3.1 Specification Source</h3>
                    <p class="text-xs text-zinc-500 font-mono mt-0.5">Fetch dari URL `/openapi.json` atau tempel JSON</p>
                </div>
                <button type="button" onclick="toggleSpecModal(false)" class="p-1 rounded text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200 cursor-pointer">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>

            <div class="space-y-3">
                <div>
                    <label class="block text-[11px] font-mono uppercase tracking-wider text-zinc-500 mb-1.5">Fetch dari Endpoint URL</label>
                    <div class="flex gap-2">
                        <input type="text" id="specUrlInput" value="/openapi.json" placeholder="https://.../openapi.json" class="flex-1 px-3 py-1.5 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 focus:outline-none focus:border-zinc-500">
                        <button type="button" onclick="fetchSpecFromUrl()" class="px-3 py-1.5 rounded text-xs font-mono font-semibold bg-emerald-600 text-white hover:bg-emerald-500 transition-colors cursor-pointer">
                            Fetch URL
                        </button>
                    </div>
                </div>

                <div>
                    <label class="block text-[11px] font-mono uppercase tracking-wider text-zinc-500 mb-1.5">Atau Paste Isi File openapi.json</label>
                    <textarea id="rawSpecTextarea" rows="6" placeholder='{"openapi": "3.1.0", "info": {...}, "paths": {...}}' class="w-full p-2.5 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 focus:outline-none focus:border-zinc-500"></textarea>
                </div>
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-zinc-200 dark:border-zinc-800">
                <button type="button" onclick="resetToEmbeddedSpec()" class="px-3 py-1.5 rounded text-xs font-mono text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200 cursor-pointer">
                    Reset ke Default Lettuce API
                </button>
                <button type="button" onclick="loadPastedSpec()" class="px-3.5 py-1.5 rounded text-xs font-mono font-medium bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 hover:opacity-90 transition-opacity cursor-pointer">
                    Parse JSON Spec
                </button>
            </div>
        </div>
    </div>

    <!-- Minimal Status Toast -->
    <div id="toast" class="fixed bottom-4 right-4 z-50 hidden items-center gap-2 px-3.5 py-2 rounded bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-950 text-xs font-mono shadow-lg border border-zinc-800 dark:border-zinc-300">
        <span id="toastMessage">OK</span>
    </div>

    <script>
        // ==========================================
        // 1. PORTAL CONFIG & EMBEDDED /OPENAPI.JSON
        // ==========================================
        const CFG = __CFG__;

        // Full OpenAPI 3.1.0 Spec from openapi.json (Used automatically if fetch('/openapi.json') is offline/preview)
        const EMBEDDED_OAS = {
            "openapi": "3.1.0",
            "info": {
                "title": "Lettuce Management API",
                "description": "REST API Sistem Diagnosis Kesehatan Selada Hidroponik (mengikuti ERD hidroponik_selada).",
                "version": "1.0.0"
            },
            "paths": {
                "/api/v1/auth/login": {
                    "post": {
                        "tags": ["A. Authentication"],
                        "summary": "Login (JSON) - untuk Frontend Laravel",
                        "description": "Login dengan `username` & `password`. Mengembalikan JWT Access Token dan role user (`owner` atau `karyawan`).",
                        "operationId": "login_api_v1_auth_login_post",
                        "requestBody": { "content": { "application/json": { "schema": { "$ref": "#/components/schemas/LoginRequest" } } }, "required": true },
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_TokenResponse_" } } } },
                            "401": { "description": "Tidak terautentikasi / token tidak valid", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIErrorResponse" } } } },
                            "422": { "description": "Validation Error", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/HTTPValidationError" } } } }
                        }
                    }
                },
                "/api/v1/auth/token": {
                    "post": {
                        "tags": ["A. Authentication"],
                        "summary": "Login (form OAuth2) - dipakai tombol Authorize di Swagger UI",
                        "description": "Endpoint khusus Swagger UI (format OAuth2 standar `application/x-www-form-urlencoded`). Frontend Laravel gunakan `POST /auth/login`.",
                        "operationId": "login_oauth2_form_api_v1_auth_token_post",
                        "requestBody": { "content": { "application/x-www-form-urlencoded": { "schema": { "$ref": "#/components/schemas/Body_login_oauth2_form_api_v1_auth_token_post" } } }, "required": true },
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/OAuth2TokenResponse" } } } },
                            "422": { "description": "Validation Error", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/HTTPValidationError" } } } }
                        }
                    }
                },
                "/api/v1/auth/logout": {
                    "post": {
                        "tags": ["A. Authentication"],
                        "summary": "Logout (blacklist token)",
                        "description": "Memasukkan JWT token aktif ke daftar blacklist sehingga tidak dapat digunakan kembali.",
                        "operationId": "logout_api_v1_auth_logout_post",
                        "security": [{ "JWT Bearer": [] }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_NoneType_" } } } },
                            "401": { "description": "Tidak terautentikasi / token tidak valid", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIErrorResponse" } } } }
                        }
                    }
                },
                "/api/v1/auth/me": {
                    "get": {
                        "tags": ["A. Authentication"],
                        "summary": "Profil user yang sedang login",
                        "description": "Mengambil profil lengkap user (`id`, `nama`, `username`, `role`) berdasarkan token Bearer yang dikirim.",
                        "operationId": "me_api_v1_auth_me_get",
                        "security": [{ "JWT Bearer": [] }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_UserOut_" } } } },
                            "401": { "description": "Tidak terautentikasi / token tidak valid", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIErrorResponse" } } } }
                        }
                    }
                },
                "/api/v1/employees": {
                    "post": {
                        "tags": ["B. Manajemen Karyawan (OWNER)"],
                        "summary": "Tambah akun karyawan baru",
                        "description": "Menambahkan user baru ke tabel `users` (Khusus role **OWNER**).",
                        "operationId": "create_employee_api_v1_employees_post",
                        "security": [{ "JWT Bearer": [] }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/EmployeeCreate" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_UserOut_" } } } },
                            "401": { "description": "Tidak terautentikasi / token tidak valid" },
                            "403": { "description": "Role tidak memiliki akses (Owner Only)" }
                        }
                    },
                    "get": {
                        "tags": ["B. Manajemen Karyawan (OWNER)"],
                        "summary": "Daftar semua akun karyawan",
                        "description": "Mengambil daftar akun karyawan dengan dukungan filter pencarian dan paginasi (Khusus role **OWNER**).",
                        "operationId": "list_employees_api_v1_employees_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [
                            { "name": "page", "in": "query", "required": false, "schema": { "type": "integer", "default": 1 } },
                            { "name": "per_page", "in": "query", "required": false, "schema": { "type": "integer", "default": 10 } },
                            { "name": "search", "in": "query", "required": false, "schema": { "type": "string" }, "description": "Cari nama / username" },
                            { "name": "role", "in": "query", "required": false, "schema": { "type": "string", "default": "karyawan" }, "description": "Filter role (default: karyawan)" }
                        ],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_UserOut__" } } } },
                            "403": { "description": "Role tidak memiliki akses (Owner Only)" }
                        }
                    }
                },
                "/api/v1/employees/{employee_id}": {
                    "get": {
                        "tags": ["B. Manajemen Karyawan (OWNER)"],
                        "summary": "Detail akun karyawan",
                        "operationId": "get_employee_api_v1_employees__employee_id__get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "employee_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 2 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_UserOut_" } } } },
                            "403": { "description": "Role tidak memiliki akses" }
                        }
                    },
                    "put": {
                        "tags": ["B. Manajemen Karyawan (OWNER)"],
                        "summary": "Edit akun karyawan (nama, username, role, reset password)",
                        "operationId": "update_employee_api_v1_employees__employee_id__put",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "employee_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 2 } }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/EmployeeUpdate" } } } },
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_UserOut_" } } } },
                            "403": { "description": "Role tidak memiliki akses" }
                        }
                    }
                },
                "/api/v1/stocks/planted-overview": {
                    "get": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Ringkasan tanaman selada yang sedang ditanam",
                        "description": "Menampilkan total tanaman aktif, distribusi status, varietas, jadwal panen 7 hari ke depan, serta ringkasan stok inventaris.",
                        "operationId": "planted_overview_api_v1_stocks_planted_overview_get",
                        "security": [{ "JWT Bearer": [] }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_PlantedOverviewOut_" } } } },
                            "403": { "description": "Role tidak memiliki akses" }
                        }
                    }
                },
                "/api/v1/stocks": {
                    "post": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Tambah stok barang inventaris (`bibit` / `nutrisi` / `lainnya`)",
                        "description": "Tambah barang inventaris (`inventory_items`). Bila `jumlah_stok > 0`, otomatis tercatat pergerakan `masuk` di `stock_movements`.",
                        "operationId": "create_stock_api_v1_stocks_post",
                        "security": [{ "JWT Bearer": [] }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/StockCreate" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_StockOut_" } } } },
                            "403": { "description": "Role tidak memiliki akses" }
                        }
                    },
                    "get": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Lihat stok barang yang tersedia",
                        "operationId": "list_stocks_api_v1_stocks_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [
                            { "name": "page", "in": "query", "required": false, "schema": { "type": "integer", "default": 1 } },
                            { "name": "per_page", "in": "query", "required": false, "schema": { "type": "integer", "default": 20 } },
                            { "name": "jenis", "in": "query", "required": false, "schema": { "type": "string" }, "description": "Filter: bibit | nutrisi | lainnya" },
                            { "name": "search", "in": "query", "required": false, "schema": { "type": "string" }, "description": "Cari nama_barang / keterangan" },
                            { "name": "low_stock_only", "in": "query", "required": false, "schema": { "type": "boolean", "default": false }, "description": "Hanya stok yang <= stok_minimum" },
                            { "name": "available_only", "in": "query", "required": false, "schema": { "type": "boolean", "default": false }, "description": "Hanya stok dengan jumlah_stok > 0" }
                        ],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_StockOut__" } } } },
                            "403": { "description": "Role tidak memiliki akses" }
                        }
                    }
                },
                "/api/v1/stocks/{stock_id}": {
                    "get": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Detail barang inventaris + riwayat pergerakan (`stock_movements`)",
                        "operationId": "get_stock_api_v1_stocks__stock_id__get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "stock_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_StockDetailOut_" } } } }
                        }
                    },
                    "put": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Edit barang inventaris & catat pergerakan stok (`masuk` / `keluar`)",
                        "operationId": "update_stock_api_v1_stocks__stock_id__put",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "stock_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/StockUpdate" } } } },
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_StockDetailOut_" } } } }
                        }
                    }
                },
                "/api/v1/stocks/{stock_id}/movements": {
                    "post": {
                        "tags": ["C. Manajemen Stok Bibit & Nutrisi (OWNER)"],
                        "summary": "Catat pergerakan stok (`masuk` / `keluar`)",
                        "operationId": "add_movement_api_v1_stocks__stock_id__movements_post",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "stock_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/StockMovementCreate" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_StockMovementOut_" } } } }
                        }
                    }
                },
                "/api/v1/plants": {
                    "get": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Lihat semua data tanaman selada",
                        "operationId": "list_plants_api_v1_plants_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [
                            { "name": "page", "in": "query", "required": false, "schema": { "type": "integer", "default": 1 } },
                            { "name": "per_page", "in": "query", "required": false, "schema": { "type": "integer", "default": 10 } },
                            { "name": "status", "in": "query", "required": false, "schema": { "type": "string" }, "description": "pembibitan | pertumbuhan | siap_panen | dipanen | mati" },
                            { "name": "search", "in": "query", "required": false, "schema": { "type": "string" }, "description": "Cari kode_tanaman / nama / varietas / keterangan" }
                        ],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_PlantOut__" } } } }
                        }
                    },
                    "post": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Tambah data tanaman baru (`plants`)",
                        "operationId": "create_plant_api_v1_plants_post",
                        "security": [{ "JWT Bearer": [] }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/PlantCreate" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_PlantOut_" } } } }
                        }
                    }
                },
                "/api/v1/plants/{plant_id}": {
                    "get": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Detail tanaman",
                        "operationId": "get_plant_api_v1_plants__plant_id__get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_PlantDetailOut_" } } } }
                        }
                    },
                    "put": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Update data tanaman",
                        "operationId": "update_plant_api_v1_plants__plant_id__put",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/PlantUpdate" } } } },
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_PlantOut_" } } } }
                        }
                    },
                    "delete": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Hapus data tanaman",
                        "operationId": "delete_plant_api_v1_plants__plant_id__delete",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_NoneType_" } } } }
                        }
                    }
                },
                "/api/v1/plants/{plant_id}/growth-records": {
                    "post": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Tambah catatan pertumbuhan (`growth_records`)",
                        "operationId": "add_growth_record_api_v1_plants__plant_id__growth_records_post",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "requestBody": { "required": true, "content": { "application/json": { "schema": { "$ref": "#/components/schemas/GrowthRecordCreate" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_GrowthRecordOut_" } } } }
                        }
                    }
                },
                "/api/v1/plants/{plant_id}/growth-history": {
                    "get": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Riwayat catatan pertumbuhan (`growth_records`) secara kronologis",
                        "operationId": "growth_history_api_v1_plants__plant_id__growth_history_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_GrowthRecordOut__" } } } }
                        }
                    }
                },
                "/api/v1/plants/{plant_id}/growth-chart": {
                    "get": {
                        "tags": ["D. Manajemen Tanaman & Grafik Pertumbuhan (KARYAWAN & OWNER)"],
                        "summary": "Data time-series untuk Growth Chart (Chart.js / ApexCharts)",
                        "operationId": "growth_chart_api_v1_plants__plant_id__growth_chart_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [
                            { "name": "plant_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } },
                            { "name": "label_mode", "in": "query", "required": false, "schema": { "type": "string", "default": "day" }, "description": "day = 'HST n', date = tanggal" },
                            { "name": "include_reference", "in": "query", "required": false, "schema": { "type": "boolean", "default": true }, "description": "Sertakan kurva tinggi ideal sebagai pembanding" }
                        ],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_GrowthChartOut_" } } } }
                        }
                    }
                },
                "/api/v1/diagnosis/predict": {
                    "post": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Upload foto selada & simpan diagnosis ke `diagnosis_records`",
                        "description": "Menerima unggahan citra daun selada (`multipart/form-data`) dan mengklasifikasikan penyakit (`Bacterial`, `Downy_mildew`, `Lettuce Mosaic Virus`, `Powdery_mildew`, `Septoria_Blight`) menggunakan model **YOLO + Temperature Scaling**.",
                        "operationId": "predict_api_v1_diagnosis_predict_post",
                        "security": [{ "JWT Bearer": [] }],
                        "requestBody": { "required": true, "content": { "multipart/form-data": { "schema": { "$ref": "#/components/schemas/Body_predict_api_v1_diagnosis_predict_post" } } } },
                        "responses": {
                            "201": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_DiagnosisOut_" } } } }
                        }
                    }
                },
                "/api/v1/diagnosis/history": {
                    "get": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Riwayat diagnosis (`diagnosis_records`)",
                        "operationId": "history_api_v1_diagnosis_history_get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [
                            { "name": "page", "in": "query", "required": false, "schema": { "type": "integer", "default": 1 } },
                            { "name": "per_page", "in": "query", "required": false, "schema": { "type": "integer", "default": 10 } },
                            { "name": "plant_id", "in": "query", "required": false, "schema": { "type": "integer" } },
                            { "name": "diagnosis_label", "in": "query", "required": false, "schema": { "type": "string" }, "description": "Filter kelas penyakit" },
                            { "name": "mine_only", "in": "query", "required": false, "schema": { "type": "boolean", "default": false }, "description": "Hanya diagnosis yang saya buat" }
                        ],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_DiagnosisListItem__" } } } }
                        }
                    }
                },
                "/api/v1/diagnosis/diseases": {
                    "get": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Basis pengetahuan penyakit (`disease_infos`)",
                        "operationId": "list_diseases_api_v1_diagnosis_diseases_get",
                        "security": [{ "JWT Bearer": [] }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_DiseaseInfoOut__" } } } }
                        }
                    }
                },
                "/api/v1/diagnosis/nutrition-conditions": {
                    "get": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Basis pengetahuan kondisi nutrisi (`nutrition_conditions`)",
                        "operationId": "list_nutrition_conditions_api_v1_diagnosis_nutrition_conditions_get",
                        "security": [{ "JWT Bearer": [] }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_list_NutritionConditionOut__" } } } }
                        }
                    }
                },
                "/api/v1/diagnosis/{diagnosis_id}": {
                    "get": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Detail hasil diagnosis",
                        "operationId": "detail_api_v1_diagnosis__diagnosis_id__get",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "diagnosis_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_DiagnosisOut_" } } } }
                        }
                    },
                    "delete": {
                        "tags": ["E. AI Diagnosis Kesehatan Selada (KARYAWAN)"],
                        "summary": "Hapus hasil diagnosis",
                        "operationId": "delete_api_v1_diagnosis__diagnosis_id__delete",
                        "security": [{ "JWT Bearer": [] }],
                        "parameters": [{ "name": "diagnosis_id", "in": "path", "required": true, "schema": { "type": "integer", "default": 1 } }],
                        "responses": {
                            "200": { "description": "Successful Response", "content": { "application/json": { "schema": { "$ref": "#/components/schemas/APIResponse_NoneType_" } } } }
                        }
                    }
                },
                "/health": {
                    "get": {
                        "tags": ["System"],
                        "summary": "Live Telemetry & Health Check",
                        "description": "Mengecek status koneksi database MySQL/SQLite serta kesiapan model AI Diagnosis.",
                        "operationId": "health_health_get",
                        "responses": {
                            "200": { "description": "Successful Response" }
                        }
                    }
                }
            },
            "components": {
                "schemas": {
                    "LoginRequest": {
                        "type": "object",
                        "required": ["password"],
                        "properties": {
                            "username": { "type": "string", "description": "Username pada tabel `users` (`owner` / `karyawan`)", "examples": ["owner"] },
                            "email": { "type": "string", "description": "Alias opsional (jika diisi `owner@mitra.com` otomatis diambil `owner`)" },
                            "password": { "type": "string", "description": "Password akun", "examples": ["owner123"] }
                        }
                    },
                    "Body_login_oauth2_form_api_v1_auth_token_post": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "grant_type": { "type": "string", "default": "password", "description": "OAuth2 password grant" },
                            "username": { "type": "string", "default": "owner", "description": "Username (`owner` / `karyawan`)" },
                            "password": { "type": "string", "default": "owner123", "description": "Password user" },
                            "scope": { "type": "string", "default": "" }
                        }
                    },
                    "EmployeeCreate": {
                        "type": "object",
                        "required": ["username", "password"],
                        "properties": {
                            "nama": { "type": "string", "description": "Nama lengkap karyawan", "examples": ["Staf Kebun"] },
                            "username": { "type": "string", "description": "Username unik (3-50 karakter)", "examples": ["staf_kebun"] },
                            "password": { "type": "string", "description": "Password minimal 6 karakter", "examples": ["password123"] },
                            "role": { "type": "string", "default": "karyawan", "description": "Role user: `karyawan` atau `owner`" }
                        }
                    },
                    "EmployeeUpdate": {
                        "type": "object",
                        "properties": {
                            "nama": { "type": "string", "description": "Nama baru karyawan" },
                            "username": { "type": "string", "description": "Username baru" },
                            "role": { "type": "string", "description": "Role: `karyawan` | `owner`" },
                            "password": { "type": "string", "description": "Isi untuk mereset password" }
                        }
                    },
                    "StockCreate": {
                        "type": "object",
                        "required": ["nama_barang", "jenis", "satuan"],
                        "properties": {
                            "nama_barang": { "type": "string", "description": "Nama item inventaris", "examples": ["Bibit Selada Butterhead"] },
                            "jenis": { "type": "string", "description": "Kategori: `bibit` | `nutrisi` | `lainnya`", "examples": ["bibit"] },
                            "satuan": { "type": "string", "description": "Satuan ukur (`biji`, `liter`, `kg`, `pak`)", "examples": ["biji"] },
                            "jumlah_stok": { "type": "number", "default": 400, "description": "Stok awal (otomatis mencatat mutasi masuk)" },
                            "stok_minimum": { "type": "number", "default": 100, "description": "Batas peringatan stok menipis (`is_low_stock`)" },
                            "keterangan": { "type": "string", "description": "Catatan barang" }
                        }
                    },
                    "StockUpdate": {
                        "type": "object",
                        "properties": {
                            "nama_barang": { "type": "string", "description": "Nama barang inventaris" },
                            "stok_minimum": { "type": "number", "description": "Batas minimum stok" },
                            "jenis_pergerakan": { "type": "string", "description": "`masuk` atau `keluar`" },
                            "jumlah": { "type": "number", "description": "Jumlah mutasi stok (> 0)" },
                            "keterangan_pergerakan": { "type": "string", "description": "Catatan pada `stock_movements`" }
                        }
                    },
                    "StockMovementCreate": {
                        "type": "object",
                        "required": ["jenis_pergerakan", "jumlah"],
                        "properties": {
                            "jenis_pergerakan": { "type": "string", "description": "Tipe mutasi: `masuk` atau `keluar`" },
                            "jumlah": { "type": "number", "description": "Jumlah unit barang (> 0)" },
                            "keterangan": { "type": "string", "description": "Keterangan mutasi stok" }
                        }
                    },
                    "PlantCreate": {
                        "type": "object",
                        "properties": {
                            "kode_tanaman": { "type": "string", "description": "Kosongkan untuk generate otomatis (SLD-YYYYMMDD-XXXX)" },
                            "nama": { "type": "string", "default": "Selada Keriting", "description": "Nama tanaman" },
                            "varietas": { "type": "string", "description": "Varietas selada (`Grand Rapids`, `Romaine`, `Butterhead`)" },
                            "tanggal_tanam": { "type": "string", "description": "Tanggal tanam (YYYY-MM-DD)" },
                            "status": { "type": "string", "default": "pembibitan", "description": "`pembibitan` | `pertumbuhan` | `siap_panen` | `dipanen` | `mati`" },
                            "keterangan": { "type": "string", "description": "Lokasi instalasi / modul hidroponik" },
                            "bibit_inventory_id": { "type": "integer", "description": "Opsional: ID `inventory_items` bibit yang digunakan" },
                            "jumlah_bibit_dipakai": { "type": "number", "description": "Opsional: otomatis memotong stok bibit" }
                        }
                    },
                    "PlantUpdate": {
                        "type": "object",
                        "properties": {
                            "status": { "type": "string", "description": "`pembibitan` | `pertumbuhan` | `siap_panen` | `dipanen` | `mati`" },
                            "tanggal_panen": { "type": "string", "description": "Tanggal panen aktual/estimasi (YYYY-MM-DD)" },
                            "keterangan": { "type": "string", "description": "Catatan pembaruan" }
                        }
                    },
                    "GrowthRecordCreate": {
                        "type": "object",
                        "properties": {
                            "tinggi_cm": { "type": "number", "description": "Tinggi tanaman (cm)" },
                            "jumlah_daun": { "type": "integer", "description": "Jumlah helai daun" },
                            "berat_gram": { "type": "number", "description": "Berat sampel (gram)" },
                            "ph_air": { "type": "number", "description": "Derajat keasaman air nutrisi (0-14)" },
                            "suhu_air": { "type": "number", "description": "Suhu larutan nutrisi (°C)" },
                            "ec": { "type": "number", "description": "Electrical Conductivity (mS/cm)" },
                            "suhu_c": { "type": "number", "description": "Suhu udara greenhouse (°C)" },
                            "kelembapan_persen": { "type": "number", "description": "Kelembapan relatif (%)" },
                            "intensitas_cahaya": { "type": "number", "description": "Intensitas cahaya (Lux)" },
                            "catatan": { "type": "string", "description": "Catatan pengamatan fisik" }
                        }
                    },
                    "Body_predict_api_v1_diagnosis_predict_post": {
                        "type": "object",
                        "required": ["file"],
                        "properties": {
                            "file": { "type": "string", "format": "binary", "description": "Foto tanaman selada (.jpg / .jpeg / .png, maks 5 MB)" },
                            "plant_id": { "type": "integer", "default": 1, "description": "ID tanaman pada `plants` (kosongkan untuk tanaman terbaru)" },
                            "plant_part": { "type": "string", "default": "daun", "description": "Bagian tanaman: `daun` | `akar` | `seluruh_tanaman`" },
                            "sumber_data": { "type": "string", "default": "upload_aplikasi", "description": "Asal gambar / dataset" },
                            "keterangan": { "type": "string", "default": "Pengamatan bercak tepi daun", "description": "Catatan tambahan (opsional)" }
                        }
                    }
                }
            }
        };

        // Sample Request Payloads
        const SAMPLE_BODIES = {
            'POST /api/v1/auth/login': { username: CFG.owner_user, password: CFG.owner_pass },
            'POST /api/v1/employees': { nama: 'Staf Kebun', username: 'staf_kebun', password: 'password123', role: 'karyawan' },
            'PUT /api/v1/employees/{employee_id}': { nama: 'Staf Kebun Senior', role: 'karyawan' },
            'POST /api/v1/stocks': { nama_barang: 'Bibit Selada Butterhead', jenis: 'bibit', satuan: 'biji', jumlah_stok: 400, stok_minimum: 100, keterangan: 'Kemasan kaleng import' },
            'PUT /api/v1/stocks/{stock_id}': { jenis_pergerakan: 'masuk', jumlah: 150, keterangan_pergerakan: 'Restock nutrisi AB Mix' },
            'POST /api/v1/stocks/{stock_id}/movements': { jenis_pergerakan: 'masuk', jumlah: 50, keterangan: 'Restock mingguan' },
            'POST /api/v1/plants': { nama: 'Selada Keriting', varietas: 'Grand Rapids', tanggal_tanam: '2026-10-18', status: 'pertumbuhan', keterangan: 'Greenhouse A - Rak 1' },
            'PUT /api/v1/plants/{plant_id}': { status: 'pertumbuhan', keterangan: 'Pindah ke modul NFT dewasa' },
            'POST /api/v1/plants/{plant_id}/growth-records': { tinggi_cm: 11.5, jumlah_daun: 8, berat_gram: 48.0, ph_air: 6.0, suhu_air: 22.0, ec: 1.25, suhu_c: 25.0, kelembapan_persen: 70.0, intensitas_cahaya: 15000.0, catatan: 'Daun segar hijau merata' }
        };

        const MODULE_LABELS = [
            { match: 'A. Auth',           name: 'A · Authentication' },
            { match: 'B. Manajemen Kar',  name: 'B · Employees (OWNER)' },
            { match: 'C. Manajemen Stok', name: 'C · Stocks & Inventory (OWNER)' },
            { match: 'D. Manajemen Tan',  name: 'D · Plants & Growth Chart' },
            { match: 'E. AI Diagnosis',   name: 'E · AI Diagnosis (YOLO)' },
            { match: 'System',            name: 'System & Telemetry' }
        ];

        // ==========================================
        // 2. APPLICATION STATE
        // ==========================================
        let OAS = null;
        let apiCategories = [];
        let currentEndpoint = null;
        let currentCodeLang = 'curl';
        let currentStatusKey = '200';
        let bearerToken = localStorage.getItem('bp_token') || '';
        let currentRole = localStorage.getItem('bp_role') || '';
        let liveParamValues = { path: {}, query: {}, body: {}, form: {} };

        const methodTokens = {
            GET:    { text: 'text-sky-600 dark:text-sky-400',     pill: 'bg-sky-500/10 text-sky-700 dark:text-sky-400 border border-sky-500/20' },
            POST:   { text: 'text-emerald-600 dark:text-emerald-400', pill: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border border-emerald-500/20' },
            PUT:    { text: 'text-amber-600 dark:text-amber-400',  pill: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20' },
            PATCH:  { text: 'text-amber-600 dark:text-amber-400',  pill: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border border-amber-500/20' },
            DELETE: { text: 'text-rose-600 dark:text-rose-400',   pill: 'bg-rose-500/10 text-rose-700 dark:text-rose-400 border border-rose-500/20' }
        };

        // ==========================================
        // 3. OPENAPI PARSER & LOADER
        // ==========================================
        function tagToCategory(tag) {
            for (const m of MODULE_LABELS) {
                if ((tag || '').startsWith(m.match)) return m.name;
            }
            return tag || 'General';
        }

        function resolveSchema(schema) {
            if (!schema) return {};
            if (schema.$ref) {
                const name = schema.$ref.split('/').pop();
                return OAS?.components?.schemas?.[name] || {};
            }
            return schema;
        }

        function buildDefaultBody(epId, schema) {
            if (SAMPLE_BODIES[epId]) return JSON.parse(JSON.stringify(SAMPLE_BODIES[epId]));
            const props = schema?.properties || {};
            const out = {};
            for (const [k, v] of Object.entries(props)) {
                if (v.examples?.length && v.examples[0] !== null) out[k] = v.examples[0];
                else if (v.default !== undefined) out[k] = v.default;
                else if (v.type === 'integer' || v.type === 'number') out[k] = 1;
                else if (v.type === 'boolean') out[k] = true;
                else out[k] = '';
            }
            return out;
        }

        async function loadOpenAPISpec(customSpecObj = null) {
            if (customSpecObj) {
                OAS = customSpecObj;
            } else {
                try {
                    const r = await fetch('/openapi.json');
                    if (r.ok) {
                        OAS = await r.json();
                        showToast('Loaded live /openapi.json');
                    } else {
                        OAS = EMBEDDED_OAS;
                    }
                } catch (_) {
                    OAS = EMBEDDED_OAS;
                }
            }

            parseOASIntoCategories();
        }

        function parseOASIntoCategories() {
            if (!OAS) return;
            document.getElementById('topbar-name').textContent = OAS.info?.title || CFG.app_name;
            document.getElementById('topbar-ver').textContent = 'v' + (OAS.info?.version || CFG.version);

            const catMap = new Map();
            MODULE_LABELS.forEach(m => catMap.set(m.name, []));

            let totalCount = 0;

            for (const [path, methods] of Object.entries(OAS.paths || {})) {
                for (const [method, op] of Object.entries(methods)) {
                    const m = method.toUpperCase();
                    if (!['GET', 'POST', 'PUT', 'PATCH', 'DELETE'].includes(m)) continue;

                    totalCount++;
                    const tag = op.tags?.[0] || 'System';
                    const catName = tagToCategory(tag);
                    const epId = `${m} ${path}`;
                    const ownerOnly = tag.includes('OWNER') && !tag.includes('KARYAWAN');

                    const pathParams = (op.parameters || [])
                        .filter(p => p.in === 'path')
                        .map(p => {
                            const sc = p.schema || {};
                            return {
                                name: p.name,
                                type: sc.type || 'integer',
                                required: !!p.required,
                                default: String(sc.default !== undefined ? sc.default : '1'),
                                desc: p.description || `ID unik pada path ${p.name}`
                            };
                        });

                    const queryParams = (op.parameters || [])
                        .filter(p => p.in === 'query')
                        .map(p => {
                            const sc = p.schema || {};
                            const t = sc.type || (sc.anyOf?.[0]?.type) || 'string';
                            return {
                                name: p.name,
                                type: t,
                                required: !!p.required,
                                default: String(sc.default !== undefined ? sc.default : ''),
                                desc: p.description || sc.description || ''
                            };
                        });

                    let bodyParams = [];
                    let bodyKind = null;
                    let bodySchema = null;

                    if (op.requestBody?.content) {
                        const c = op.requestBody.content;
                        if (c['application/json']) {
                            bodyKind = 'json';
                            bodySchema = resolveSchema(c['application/json'].schema);
                        } else if (c['multipart/form-data']) {
                            bodyKind = 'multipart';
                            bodySchema = resolveSchema(c['multipart/form-data'].schema);
                        } else if (c['application/x-www-form-urlencoded']) {
                            bodyKind = 'form';
                            bodySchema = resolveSchema(c['application/x-www-form-urlencoded'].schema);
                        }

                        if (bodySchema?.properties) {
                            const reqSet = new Set(bodySchema.required || []);
                            bodyParams = Object.entries(bodySchema.properties).map(([name, prop]) => {
                                const t = prop.type || prop.anyOf?.[0]?.type || 'string';
                                const isFile = prop.format === 'binary' || prop.contentMediaType === 'application/octet-stream';
                                return {
                                    name,
                                    type: isFile ? 'file (binary)' : t,
                                    required: reqSet.has(name),
                                    default: isFile ? '' : String(prop.default !== undefined ? prop.default : (prop.examples?.[0] ?? '')),
                                    desc: prop.description || ''
                                };
                            });
                        }
                    }

                    const authRequired = !!(op.security && op.security.length > 0);
                    const responses = {};
                    for (const [code, resp] of Object.entries(op.responses || {})) {
                        responses[code] = { statusText: `${code} ${getHttpStatusLabel(code)}`, desc: resp.description || '' };
                    }

                    if (!catMap.has(catName)) catMap.set(catName, []);
                    catMap.get(catName).push({
                        id: epId,
                        method: m,
                        path,
                        tag,
                        ownerOnly,
                        summary: op.summary || path,
                        description: op.description || '',
                        authRequired,
                        pathParams,
                        queryParams,
                        bodyParams,
                        bodyKind,
                        bodySchema,
                        responses
                    });
                }
            }

            apiCategories = [];
            catMap.forEach((eps, name) => {
                if (eps.length > 0) apiCategories.push({ name, endpoints: eps });
            });

            document.getElementById('sidebarEndpointCount').textContent = `${totalCount} Endpoints`;
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.placeholder = `Filter ${totalCount} endpoints, path, atau tag...`;
            }
            renderSidebar('');

            // Select default endpoint (AI Diagnosis or first available)
            const defaultTarget = apiCategories.flatMap(c => c.endpoints).find(e => e.id === 'POST /api/v1/diagnosis/predict')
                || apiCategories[0]?.endpoints[0];
            if (defaultTarget) selectEndpoint(defaultTarget.id);
        }

        function getHttpStatusLabel(code) {
            const labels = { '200': 'OK', '201': 'Created', '401': 'Unauthorized', '403': 'Forbidden', '404': 'Not Found', '422': 'Unprocessable Entity' };
            return labels[code] || 'Response';
        }

        function escapeAttr(str) {
            return String(str ?? '')
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }

        // ==========================================
        // 4. SIDEBAR & CENTER DOCUMENTATION RENDERING
        // ==========================================
        function renderSidebar(filterText = '') {
            const q = (filterText || '').toLowerCase().trim();
            const nav = document.getElementById('sidebarNav');
            if (!nav) return;

            let html = '';

            apiCategories.forEach(cat => {
                const matched = cat.endpoints.filter(ep =>
                    ep.path.toLowerCase().includes(q) ||
                    ep.summary.toLowerCase().includes(q) ||
                    ep.method.toLowerCase().includes(q) ||
                    cat.name.toLowerCase().includes(q)
                );
                if (!matched.length) return;

                html += `
                    <div class="space-y-1">
                        <div class="px-2 py-1 text-[10px] font-mono uppercase tracking-wider text-zinc-400 dark:text-zinc-500 font-semibold">
                            ${escapeAttr(cat.name)}
                        </div>
                        <div class="space-y-0.5">
                            ${matched.map(ep => {
                                const isActive = currentEndpoint?.id === ep.id;
                                const rowStyle = isActive
                                    ? 'bg-zinc-200/80 dark:bg-zinc-900 text-zinc-950 dark:text-zinc-100 font-medium'
                                    : 'text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-900/50 hover:text-zinc-900 dark:hover:text-zinc-200';
                                const cls = methodTokens[ep.method] || methodTokens.GET;
                                return `
                                    <button type="button" data-ep-id="${escapeAttr(ep.id)}" class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left text-xs transition-colors cursor-pointer ${rowStyle}">
                                        <span class="w-10 font-mono text-[10px] font-semibold uppercase shrink-0 ${cls.text}">${ep.method}</span>
                                        <span class="truncate flex-1" title="${escapeAttr(ep.summary)}">${escapeAttr(ep.summary)}</span>
                                    </button>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });

            nav.innerHTML = html || `<div class="px-3 py-8 text-center text-xs font-mono text-zinc-400">Tidak ada endpoint untuk "${escapeAttr(filterText)}"</div>`;
            lucide.createIcons();
        }

        function selectEndpoint(epId) {
            let found = null;
            for (const cat of apiCategories) {
                found = cat.endpoints.find(e => e.id === epId);
                if (found) break;
            }
            if (!found) return;
            currentEndpoint = found;

            liveParamValues = { path: {}, query: {}, body: {}, form: {} };
            currentEndpoint.pathParams.forEach(p => liveParamValues.path[p.name] = p.default);
            currentEndpoint.queryParams.forEach(p => liveParamValues.query[p.name] = p.default);

            if (currentEndpoint.bodyKind === 'json') {
                liveParamValues.body = buildDefaultBody(currentEndpoint.id, currentEndpoint.bodySchema);
            } else if (currentEndpoint.bodyKind === 'multipart' || currentEndpoint.bodyKind === 'form') {
                currentEndpoint.bodyParams.forEach(p => {
                    if (!p.type.includes('file')) {
                        liveParamValues.form[p.name] = p.default;
                    }
                });
            }

            currentStatusKey = Object.keys(currentEndpoint.responses)[0] || '200';

            const currentFilter = document.getElementById('searchInput')?.value || document.getElementById('mobileSearchInput')?.value || '';
            renderSidebar(currentFilter);
            renderCenterDocumentation();
            updatePlaygroundConsole();
            previewSchemaByStatus(currentStatusKey);
            toggleMobileSidebar(false);

            const docPanel = document.getElementById('docPanel');
            if (docPanel) docPanel.scrollTop = 0;
        }

        function renderCenterDocumentation() {
            const ep = currentEndpoint;
            const docPanel = document.getElementById('docPanel');
            const cls = methodTokens[ep.method] || methodTokens.GET;

            const renderParamSection = (params, groupType, title) => {
                if (!params?.length) return '';
                return `
                    <section class="space-y-3">
                        <div class="border-b border-zinc-200 dark:border-zinc-800 pb-2 flex items-center justify-between">
                            <h3 class="text-xs font-mono uppercase tracking-wider text-zinc-500 dark:text-zinc-400">${title}</h3>
                        </div>
                        <div class="divide-y divide-zinc-200 dark:divide-zinc-800 border-b border-zinc-200 dark:border-zinc-800">
                            ${params.map(p => `
                                <div class="py-3.5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                                    <div class="space-y-1 flex-1">
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <span class="font-mono text-xs font-semibold text-zinc-900 dark:text-zinc-100">${p.name}</span>
                                            <span class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400">${p.type}</span>
                                            ${p.required
                                                ? `<span class="text-[10px] font-mono text-rose-600 dark:text-rose-400">required</span>`
                                                : `<span class="text-[10px] font-mono text-zinc-400">optional</span>`}
                                        </div>
                                        <p class="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">${p.desc || '—'}</p>
                                    </div>
                                    <div class="sm:w-52 shrink-0">
                                        <input 
                                            type="text" 
                                            value="${escapeAttr(liveParamValues[groupType]?.[p.name] ?? p.default)}"
                                            oninput="updateLiveParam('${groupType}', '${p.name}', this.value)"
                                            placeholder="${escapeAttr(p.name)}"
                                            class="w-full px-2.5 py-1.5 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 focus:outline-none focus:border-emerald-500"
                                        >
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </section>
                `;
            };

            const renderBodySection = () => {
                if (!ep.bodyParams?.length) return '';

                if (ep.bodyKind === 'json') {
                    const jsonStr = JSON.stringify(liveParamValues.body, null, 2);
                    return `
                        <section class="space-y-4">
                            <div class="border-b border-zinc-200 dark:border-zinc-800 pb-2 flex items-center justify-between">
                                <h3 class="text-xs font-mono uppercase tracking-wider text-zinc-500 dark:text-zinc-400">Body Parameters</h3>
                                <span class="text-[11px] font-mono text-zinc-400">application/json</span>
                            </div>
                            <div class="divide-y divide-zinc-200 dark:divide-zinc-800 border-b border-zinc-200 dark:border-zinc-800">
                                ${ep.bodyParams.map(p => `
                                    <div class="py-3 space-y-1">
                                        <div class="flex items-center gap-2 flex-wrap">
                                            <span class="font-mono text-xs font-semibold text-zinc-900 dark:text-zinc-100">${p.name}</span>
                                            <span class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400">${p.type}</span>
                                            ${p.required
                                                ? `<span class="text-[10px] font-mono text-rose-600 dark:text-rose-400">required</span>`
                                                : `<span class="text-[10px] font-mono text-zinc-400">optional</span>`}
                                        </div>
                                        <p class="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">${p.desc || '—'}</p>
                                    </div>
                                `).join('')}
                            </div>
                            <div class="space-y-1.5 pt-1">
                                <div class="flex items-center justify-between text-[11px] font-mono text-zinc-500">
                                    <span>JSON Request Payload (Editable)</span>
                                    <span id="jsonErrorBadge" class="hidden text-rose-500">Invalid JSON syntax</span>
                                </div>
                                <textarea 
                                    id="bodyJsonTextarea" 
                                    rows="7" 
                                    oninput="handleBodyJsonEdit(this.value)"
                                    class="w-full p-3.5 text-xs font-mono leading-relaxed rounded bg-zinc-50 dark:bg-zinc-900 text-zinc-800 dark:text-zinc-200 border border-zinc-200 dark:border-zinc-800 focus:outline-none focus:border-emerald-500 resize-y"
                                >${jsonStr}</textarea>
                            </div>
                        </section>
                    `;
                }

                // Multipart / Form-Urlencoded (e.g. POST /api/v1/diagnosis/predict or /api/v1/auth/token)
                return `
                    <section class="space-y-4">
                        <div class="border-b border-zinc-200 dark:border-zinc-800 pb-2 flex items-center justify-between">
                            <h3 class="text-xs font-mono uppercase tracking-wider text-zinc-500 dark:text-zinc-400">Body Parameters</h3>
                            <span class="text-[11px] font-mono text-zinc-400">${ep.bodyKind === 'multipart' ? 'multipart/form-data' : 'application/x-www-form-urlencoded'}</span>
                        </div>
                        <div class="divide-y divide-zinc-200 dark:divide-zinc-800 border-b border-zinc-200 dark:border-zinc-800">
                            ${ep.bodyParams.map(p => {
                                const isFile = p.type.includes('file');
                                return `
                                    <div class="py-3.5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                                        <div class="space-y-1 flex-1">
                                            <div class="flex items-center gap-2 flex-wrap">
                                                <span class="font-mono text-xs font-semibold text-zinc-900 dark:text-zinc-100">${p.name}</span>
                                                <span class="text-[11px] font-mono text-emerald-600 dark:text-emerald-400">${p.type}</span>
                                                ${p.required
                                                    ? `<span class="text-[10px] font-mono text-rose-600 dark:text-rose-400">required</span>`
                                                    : `<span class="text-[10px] font-mono text-zinc-400">optional</span>`}
                                            </div>
                                            <p class="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed">${p.desc || '—'}</p>
                                        </div>
                                        <div class="sm:w-56 shrink-0">
                                            ${isFile
                                                ? `<input type="file" id="ff-${p.name}" data-form-file="${p.name}" accept=".jpg,.jpeg,.png" onchange="updatePlaygroundConsole()" class="text-xs font-mono text-zinc-500 w-full file:mr-2 file:py-1 file:px-2.5 file:rounded file:border file:border-zinc-300 dark:file:border-zinc-700 file:text-xs file:font-mono file:bg-zinc-100 dark:file:bg-zinc-800 file:text-zinc-700 dark:file:text-zinc-200 cursor-pointer" />`
                                                : `<input type="text" value="${escapeAttr(liveParamValues.form?.[p.name] ?? p.default)}" data-form-field="${p.name}" oninput="updateFormParam('${p.name}', this.value)" class="w-full px-2.5 py-1.5 text-xs font-mono rounded bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 text-zinc-800 dark:text-zinc-200 focus:outline-none focus:border-emerald-500" />`
                                            }
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </section>
                `;
            };

            const renderResponsesList = () => {
                const codes = Object.keys(ep.responses);
                if (!codes.length) return '';
                return `
                    <section class="space-y-3">
                        <div class="border-b border-zinc-200 dark:border-zinc-800 pb-2 flex items-center justify-between">
                            <h3 class="text-xs font-mono uppercase tracking-wider text-zinc-500 dark:text-zinc-400">Status Codes</h3>
                            <span class="text-[11px] font-mono text-zinc-400">Klik untuk preview schema</span>
                        </div>
                        <div class="flex flex-wrap gap-2">
                            ${codes.map(code => {
                                const ok = code.startsWith('2');
                                const active = code === currentStatusKey
                                    ? 'border-zinc-900 dark:border-zinc-200 bg-zinc-100 dark:bg-zinc-900'
                                    : 'border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:bg-zinc-50 dark:hover:bg-zinc-900/60';
                                return `
                                    <button type="button" onclick="previewSchemaByStatus('${code}')" class="px-3 py-2 rounded border ${active} flex items-center gap-2 text-xs font-mono transition-colors cursor-pointer">
                                        <span class="w-1.5 h-1.5 rounded-full ${ok ? 'bg-emerald-500' : 'bg-rose-500'}"></span>
                                        <span class="font-semibold ${ok ? 'text-emerald-700 dark:text-emerald-400' : 'text-rose-700 dark:text-rose-400'}">${code}</span>
                                        <span class="text-zinc-500">${ep.responses[code].desc || (ok ? 'Success' : 'Error')}</span>
                                    </button>
                                `;
                            }).join('')}
                        </div>
                    </section>
                `;
            };

            docPanel.innerHTML = `
                <!-- Endpoint Header -->
                <div class="space-y-3 pb-6 border-b border-zinc-200 dark:border-zinc-800">
                    <div class="flex items-center justify-between gap-2 flex-wrap">
                        <div class="flex items-center gap-2 flex-wrap">
                            <span class="px-2 py-0.5 rounded font-mono text-xs font-semibold uppercase ${cls.pill}">${ep.method}</span>
                            <code class="text-sm font-mono text-zinc-800 dark:text-zinc-200">${ep.path}</code>
                        </div>
                        <div class="flex items-center gap-2">
                            ${ep.ownerOnly ? `<span class="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20">OWNER ONLY</span>` : ''}
                            <span class="text-[11px] font-mono text-zinc-500">${ep.authRequired ? 'Auth: JWT Bearer' : 'Auth: Public'}</span>
                        </div>
                    </div>
                    <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">${ep.summary}</h1>
                    ${ep.description ? `<p class="text-sm text-zinc-600 dark:text-zinc-400 leading-relaxed">${ep.description}</p>` : ''}
                </div>

                ${renderParamSection(ep.pathParams, 'path', 'Path Parameters')}
                ${renderParamSection(ep.queryParams, 'query', 'Query Parameters')}
                ${renderBodySection()}
                ${renderResponsesList()}
            `;

            lucide.createIcons();
        }

        // ==========================================
        // 5. URL BUILDER, CODE GENERATOR & LIVE CONSOLE
        // ==========================================
        function buildFullRequestUrl() {
            if (!currentEndpoint) return window.location.origin;
            let path = currentEndpoint.path;
            Object.keys(liveParamValues.path).forEach(k => {
                path = path.replace(`{${k}}`, encodeURIComponent(liveParamValues.path[k] || '1'));
            });
            const qs = new URLSearchParams();
            Object.keys(liveParamValues.query).forEach(k => {
                if (liveParamValues.query[k] !== undefined && liveParamValues.query[k] !== '') {
                    qs.set(k, liveParamValues.query[k]);
                }
            });
            const q = qs.toString();
            const origin = window.location.origin && window.location.origin !== 'null' ? window.location.origin : 'http://localhost:8000';
            return origin + path + (q ? '?' + q : '');
        }

        function updateLiveParam(group, name, val) {
            liveParamValues[group][name] = val;
            updatePlaygroundConsole();
        }

        function updateFormParam(name, val) {
            liveParamValues.form[name] = val;
            updatePlaygroundConsole();
        }

        function handleBodyJsonEdit(raw) {
            const badge = document.getElementById('jsonErrorBadge');
            try {
                liveParamValues.body = JSON.parse(raw);
                badge?.classList.add('hidden');
                updatePlaygroundConsole();
            } catch (_) {
                badge?.classList.remove('hidden');
            }
        }

        function updatePlaygroundConsole() {
            if (!currentEndpoint) return;
            const ep = currentEndpoint;
            const fullUrl = buildFullRequestUrl();
            const cls = methodTokens[ep.method] || methodTokens.GET;

            const badge = document.getElementById('consoleMethodBadge');
            badge.textContent = ep.method;
            badge.className = `px-2.5 py-2 text-[11px] font-mono font-semibold uppercase flex items-center border-r border-zinc-200 dark:border-zinc-800 shrink-0 ${cls.text}`;

            document.getElementById('consoleUrlPreview').textContent = fullUrl;
            document.getElementById('securityBadge').textContent = ep.authRequired
                ? `Authorization: Bearer (${(currentRole || 'TOKEN').toUpperCase()})`
                : 'Public Endpoint';

            const statusSelect = document.getElementById('mockStatusSelect');
            statusSelect.innerHTML = Object.keys(ep.responses).map(code =>
                `<option value="${code}" ${code === currentStatusKey ? 'selected' : ''}>${ep.responses[code].statusText}</option>`
            ).join('');

            renderCodeSnippet(fullUrl);
            lucide.createIcons();
        }

        function renderCodeSnippet(fullUrl) {
            const ep = currentEndpoint;
            if (!ep) return;
            const hasJsonBody = ['POST', 'PUT', 'PATCH'].includes(ep.method) && ep.bodyKind === 'json' && Object.keys(liveParamValues.body).length > 0;
            const bodyJson = JSON.stringify(liveParamValues.body, null, 2);
            const authHdr = `Bearer ${bearerToken || 'YOUR_JWT_TOKEN'}`;
            let snippet = '';

            if (currentCodeLang === 'curl') {
                snippet = `curl -X ${ep.method} "${fullUrl}" \\\n  -H "Accept: application/json"`;
                if (ep.authRequired) snippet += ` \\\n  -H "Authorization: ${authHdr}"`;
                if (hasJsonBody) {
                    snippet += ` \\\n  -H "Content-Type: application/json" \\\n  -d '${bodyJson}'`;
                } else if (ep.bodyKind === 'multipart') {
                    const fileInput = document.querySelector('[data-form-file]');
                    const fileName = fileInput?.files?.[0]?.name || 'selada_leaf.jpg';
                    snippet += ` \\\n  -F "file=@${fileName}"`;
                    Object.entries(liveParamValues.form).forEach(([k, v]) => {
                        if (v !== '') snippet += ` \\\n  -F "${k}=${v}"`;
                    });
                } else if (ep.bodyKind === 'form') {
                    const pairs = Object.entries(liveParamValues.form).filter(([, v]) => v !== '').map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`).join('&');
                    snippet += ` \\\n  -H "Content-Type: application/x-www-form-urlencoded" \\\n  -d "${pairs}"`;
                }
            } else if (currentCodeLang === 'js') {
                const headers = { Accept: 'application/json' };
                if (ep.authRequired) headers['Authorization'] = authHdr;
                if (hasJsonBody) headers['Content-Type'] = 'application/json';
                snippet = `const response = await fetch("${fullUrl}", {\n  method: "${ep.method}",\n  headers: ${JSON.stringify(headers, null, 4).replace(/\n/g, '\n  ')}${hasJsonBody ? `,\n  body: JSON.stringify(${bodyJson.replace(/\n/g, '\n  ')})` : ''}\n});\n\nconst result = await response.json();\nconsole.log(result.status, result.data);`;
            } else if (currentCodeLang === 'python') {
                snippet = `import httpx\n\nurl = "${fullUrl}"\nheaders = {\n    "Accept": "application/json"${ep.authRequired ? `,\n    "Authorization": "${authHdr}"` : ''}\n}\n`;
                if (hasJsonBody) {
                    snippet += `payload = ${bodyJson}\n\nwith httpx.Client() as client:\n    res = client.request("${ep.method}", url, json=payload, headers=headers)\n    print(res.status_code, res.json())`;
                } else {
                    snippet += `\nwith httpx.Client() as client:\n    res = client.request("${ep.method}", url, headers=headers)\n    print(res.status_code, res.json())`;
                }
            } else if (currentCodeLang === 'laravel') {
                snippet = `use Illuminate\\Support\\Facades\\Http;\n\n$response = Http::acceptJson()${ep.authRequired ? `\n    ->withToken('${bearerToken || 'YOUR_JWT_TOKEN'}')` : ''}\n    ->${ep.method.toLowerCase()}('${fullUrl}'${hasJsonBody ? `, ${bodyJson.replace(/\n/g, '\n    ')}` : ''});\n\n$data = $response->json('data');`;
            }

            document.getElementById('codeSnippetBox').textContent = snippet;
        }

        function switchCodeLang(lang) {
            currentCodeLang = lang;
            document.querySelectorAll('.lang-tab').forEach(btn => {
                const on = btn.dataset.lang === lang;
                btn.className = `lang-tab px-2 py-1 rounded text-[11px] font-mono font-medium transition-colors cursor-pointer ${on ? 'bg-zinc-200/80 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100' : 'text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-200'}`;
            });
            updatePlaygroundConsole();
        }

        // ==========================================
        // 6. REAL HTTP EXECUTION + SMART MOCK FALLBACK
        // ==========================================
        function buildRealisticMockResponse(ep, statusKey) {
            if (statusKey === '401') {
                return { status: "error", message: "Tidak terautentikasi / token Bearer tidak valid atau kedaluwarsa.", data: null, errors: null };
            }
            if (statusKey === '403') {
                return { status: "error", message: "Akses ditolak: Endpoint ini hanya dapat diakses oleh role OWNER.", data: null, errors: null };
            }
            if (statusKey === '422') {
                return { status: "error", message: "Validasi input gagal", data: null, errors: [{ field: "body", message: "Field wajib belum lengkap", type: "value_error" }] };
            }

            const p = ep.path;
            const m = ep.method;

            if (p === '/health') {
                return { status: "success", message: "System healthy", data: { database: "ok", ai_diagnosis: "AI_MODEL:yolo", environment: CFG.env } };
            }
            if (p === '/api/v1/auth/login') {
                const uname = liveParamValues.body?.username || 'owner';
                const role = uname.includes('karyawan') ? 'karyawan' : 'owner';
                return {
                    status: "success",
                    message: "Login berhasil",
                    data: {
                        access_token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIke3VuYW1lfSIsInJvbGUiOiIke3JvbGV9In0.sig_${Date.now()}`,
                        token_type: "bearer",
                        expires_in: 86400,
                        expires_at: "2026-11-05T19:48:00Z",
                        role: role,
                        user: { id: role === 'owner' ? 1 : 2, nama: role === 'owner' ? "Pemilik Kebun Hidroponik" : "Staf Kebun Hidroponik", username: uname, role: role }
                    }
                };
            }
            if (p === '/api/v1/auth/me') {
                const r = currentRole || 'owner';
                return {
                    status: "success",
                    message: "Berhasil mengambil profil user",
                    data: { id: r === 'owner' ? 1 : 2, nama: r === 'owner' ? "Pemilik Kebun Hidroponik" : "Staf Kebun Hidroponik", username: r, role: r, created_at: "2026-10-01T08:00:00Z" }
                };
            }
            if (p.includes('/diagnosis/predict') && m === 'POST') {
                const fileInput = document.querySelector('[data-form-file]');
                const uploadedName = fileInput?.files?.[0]?.name || 'selada_sample_leaf.jpg';
                return {
                    status: "success",
                    message: "Diagnosis citra selada selesai",
                    data: {
                        id: 19,
                        plant_id: Number(liveParamValues.form.plant_id || 1),
                        kode_tanaman: "SLD-20261018-0001",
                        diagnosed_by: 2,
                        diagnosed_by_nama: "Staf Kebun Hidroponik",
                        tanggal_diagnosis: new Date().toISOString(),
                        image_path: `uploads/diagnosis/${uploadedName}`,
                        image_url: `/static/uploads/diagnosis/${uploadedName}`,
                        plant_part: liveParamValues.form.plant_part || "daun",
                        kelas_diagnosis: "Tip Burn",
                        confidence: 0.942,
                        model: "SVM-RBF + ColorTextureDescriptor",
                        versi_model: "v1.4.0",
                        diagnosis_result: "Tip Burn (Terbakar Ujung Daun)",
                        nutrient_condition: "Defisiensi Kalsium (Ca) / Transpirasi Tinggi",
                        disease_info: "Bukan infeksi patogen menular; disebabkan terhambatnya transpor kalsium ke tepi daun muda.",
                        plant_condition_summary: "Terdeteksi gejala Tip Burn dengan tingkat keyakinan 94.2%. Disarankan menaikkan sirkulasi udara kipas greenhouse dan menjaga suhu air nutrisi di bawah 24°C.",
                        rekomendasi: "1. Periksa aliran pompa NFT. 2. Turunkan suhu larutan nutrisi. 3. Semprot foliar CaCl2 dosis rendah bila diperlukan."
                    }
                };
            }
            if (p.includes('/growth-chart')) {
                return {
                    status: "success",
                    message: "Berhasil mengambil data grafik pertumbuhan",
                    data: {
                        plant_id: Number(liveParamValues.path.plant_id || 1),
                        kode_tanaman: "SLD-20261018-0001",
                        varietas: "Grand Rapids",
                        tanggal_tanam: "2026-10-18",
                        label_mode: liveParamValues.query.label_mode || "day",
                        labels: ["HST 7", "HST 14", "HST 21", "HST 28"],
                        days_after_planting: [7, 14, 21, 28],
                        series: {
                            tinggi_cm: [4.2, 8.5, 13.8, 18.4],
                            jumlah_daun: [4, 7, 11, 15],
                            berat_gram: [12.0, 38.5, 89.0, 148.0],
                            ph_air: [6.0, 6.1, 5.9, 6.0],
                            ec: [1.0, 1.2, 1.35, 1.4]
                        }
                    }
                };
            }
            if (p.includes('/planted-overview')) {
                return {
                    status: "success",
                    message: "Berhasil",
                    data: {
                        total_active_plants: 12,
                        by_status: { pembibitan: 3, pertumbuhan: 6, siap_panen: 3 },
                        by_varietas: { "Grand Rapids": 7, "Romaine": 3, "Butterhead": 2 },
                        stock_summary: { bibit: 1450, nutrisi: 24, lainnya: 8 }
                    }
                };
            }
            if (p.includes('/stocks')) {
                return {
                    status: "success",
                    message: "Berhasil",
                    data: m === 'GET' && !p.includes('{stock_id}')
                        ? [
                            { id: 1, nama_barang: "Bibit Selada Grand Rapids", jenis: "bibit", satuan: "biji", jumlah_stok: 850, stok_minimum: 200, is_low_stock: false },
                            { id: 2, nama_barang: "Nutrisi AB Mix Sayur Daun", jenis: "nutrisi", satuan: "liter", jumlah_stok: 15, stok_minimum: 10, is_low_stock: false }
                        ]
                        : { id: 1, nama_barang: liveParamValues.body?.nama_barang || "Bibit Selada Grand Rapids", jenis: liveParamValues.body?.jenis || "bibit", satuan: liveParamValues.body?.satuan || "biji", jumlah_stok: liveParamValues.body?.jumlah_stok || 850, stok_minimum: 100, is_low_stock: false }
                };
            }
            if (p.includes('/plants')) {
                return {
                    status: "success",
                    message: "Berhasil",
                    data: m === 'GET' && !p.includes('{plant_id}')
                        ? [
                            { id: 1, kode_tanaman: "SLD-20261018-0001", nama: "Selada Keriting", varietas: "Grand Rapids", tanggal_tanam: "2026-10-18", status: "pertumbuhan", umur_hari: 17, hari_menuju_panen: 18 },
                            { id: 2, kode_tanaman: "SLD-20261010-0002", nama: "Selada Romaine", varietas: "Cos Romaine", tanggal_tanam: "2026-10-10", status: "siap_panen", umur_hari: 25, hari_menuju_panen: 5 }
                        ]
                        : { id: Number(liveParamValues.path.plant_id || 1), kode_tanaman: "SLD-20261018-0001", nama: liveParamValues.body?.nama || "Selada Keriting", varietas: liveParamValues.body?.varietas || "Grand Rapids", tanggal_tanam: "2026-10-18", status: liveParamValues.body?.status || "pertumbuhan", umur_hari: 17, hari_menuju_panen: 18 }
                };
            }
            if (p.includes('/employees')) {
                return {
                    status: "success",
                    message: "Berhasil",
                    data: m === 'GET' && !p.includes('{employee_id}')
                        ? [
                            { id: 1, nama: "Pemilik Kebun", username: "owner", role: "owner" },
                            { id: 2, nama: "Staf Kebun Hidroponik", username: "karyawan", role: "karyawan" }
                        ]
                        : { id: 3, nama: liveParamValues.body?.nama || "Staf Kebun", username: liveParamValues.body?.username || "staf_kebun", role: liveParamValues.body?.role || "karyawan" }
                };
            }

            return {
                status: "success",
                message: "Berhasil",
                data: { endpoint: `${m} ${p}`, timestamp: new Date().toISOString(), role: currentRole || "public" }
            };
        }

        function previewSchemaByStatus(statusKey) {
            currentStatusKey = statusKey;
            renderCenterDocumentation();
            updatePlaygroundConsole();

            const mockData = buildRealisticMockResponse(currentEndpoint, statusKey);
            const ok = statusKey.startsWith('2');
            document.getElementById('responseMeta').innerHTML = `
                <span class="text-xs font-mono font-semibold ${ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
                    ${currentEndpoint.responses[statusKey]?.statusText || statusKey}
                </span>
                <span class="text-zinc-300 dark:text-zinc-700">•</span>
                <span class="text-[11px] font-mono text-zinc-400">Schema Preview</span>
            `;
            document.getElementById('responseJsonBox').innerHTML = syntaxHighlightJson(mockData);
        }

        async function executeApiRequest() {
            if (!currentEndpoint) return;
            const ep = currentEndpoint;
            const fullUrl = buildFullRequestUrl();
            const parsedUrl = new URL(fullUrl);
            const relPath = parsedUrl.pathname + parsedUrl.search;

            const loadEl = document.getElementById('responseLoading');
            const jsonBox = document.getElementById('responseJsonBox');
            const sendBtn = document.getElementById('sendRequestBtn');

            loadEl.classList.remove('hidden');
            loadEl.classList.add('flex');
            jsonBox.classList.add('hidden');
            sendBtn.disabled = true;

            const headers = { Accept: 'application/json' };
            if (bearerToken) headers['Authorization'] = 'Bearer ' + bearerToken;

            let body;
            if (ep.bodyKind === 'json') {
                headers['Content-Type'] = 'application/json';
                const ta = document.getElementById('bodyJsonTextarea');
                body = ta ? ta.value : JSON.stringify(liveParamValues.body);
            } else if (ep.bodyKind === 'multipart') {
                const fd = new FormData();
                document.querySelectorAll('[data-form-file]').forEach(inp => {
                    if (inp.files?.[0]) fd.append(inp.dataset.formFile, inp.files[0]);
                });
                document.querySelectorAll('[data-form-field]').forEach(inp => {
                    if (inp.value) fd.append(inp.dataset.formField, inp.value);
                });
                body = fd;
            } else if (ep.bodyKind === 'form') {
                const p = new URLSearchParams();
                document.querySelectorAll('[data-form-field]').forEach(inp => {
                    if (inp.value) p.set(inp.dataset.formField, inp.value);
                });
                headers['Content-Type'] = 'application/x-www-form-urlencoded';
                body = p.toString();
            }

            const t0 = performance.now();
            try {
                const res = await fetch(relPath, { method: ep.method, headers, body });
                const contentType = res.headers.get('content-type') || '';
                if (!contentType.includes('application/json')) {
                    throw new Error('Offline / Preview Mode');
                }
                const ms = Math.round(performance.now() - t0);
                const data = await res.json();
                const ok = res.status >= 200 && res.status < 300;

                // Auto-save token if login succeeded
                if (ep.path.endsWith('/auth/login') && ok && data?.data?.access_token) {
                    bearerToken = data.data.access_token;
                    currentRole = data.data.role || '';
                    localStorage.setItem('bp_token', bearerToken);
                    localStorage.setItem('bp_role', currentRole);
                    document.getElementById('bearerTokenInput').value = bearerToken;
                    updateAuthBadgeUI();
                }

                loadEl.classList.add('hidden');
                loadEl.classList.remove('flex');
                jsonBox.classList.remove('hidden');
                sendBtn.disabled = false;
                jsonBox.innerHTML = syntaxHighlightJson(data);

                document.getElementById('responseMeta').innerHTML = `
                    <span class="text-xs font-mono font-semibold ${ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${res.status} ${res.statusText}</span>
                    <span class="text-zinc-300 dark:text-zinc-700">•</span>
                    <span class="text-[11px] font-mono text-zinc-400">${ms} ms (Live)</span>
                `;
                showToast(`${res.status} ${res.statusText} · ${ms} ms`);
            } catch (_) {
                // Interactive Mock Execution for Preview / Sandbox Environment
                setTimeout(() => {
                    loadEl.classList.add('hidden');
                    loadEl.classList.remove('flex');
                    jsonBox.classList.remove('hidden');
                    sendBtn.disabled = false;

                    const ms = Math.floor(Math.random() * 45) + 18;
                    let simStatus = Object.keys(ep.responses)[0] || '200';

                    if (ep.authRequired && !bearerToken) {
                        simStatus = '401';
                    } else if (ep.ownerOnly && currentRole === 'karyawan') {
                        simStatus = '403';
                    }

                    const simData = buildRealisticMockResponse(ep, simStatus);
                    const ok = simStatus.startsWith('2');

                    // Auto-save token if testing POST /api/v1/auth/login
                    if (ep.path === '/api/v1/auth/login' && ok && simData?.data?.access_token) {
                        bearerToken = simData.data.access_token;
                        currentRole = simData.data.role;
                        localStorage.setItem('bp_token', bearerToken);
                        localStorage.setItem('bp_role', currentRole);
                        document.getElementById('bearerTokenInput').value = bearerToken;
                        updateAuthBadgeUI();
                    }

                    document.getElementById('responseMeta').innerHTML = `
                        <span class="text-xs font-mono font-semibold ${ok ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${simStatus} ${getHttpStatusLabel(simStatus)}</span>
                        <span class="text-zinc-300 dark:text-zinc-700">•</span>
                        <span class="text-[11px] font-mono text-zinc-400">${ms} ms</span>
                    `;
                    jsonBox.innerHTML = syntaxHighlightJson(simData);
                    showToast(`HTTP ${simStatus} ${getHttpStatusLabel(simStatus)} (${ms} ms)`);
                }, 240);
            }
        }

        // ==========================================
        // 7. AUTH, TELEMETRY & SPEC MODAL HELPERS
        // ==========================================
        async function _performPortalLogin(username, password) {
            const errEl = document.getElementById('authModalError');
            if (errEl) { errEl.classList.add('hidden'); errEl.textContent = ''; }

            try {
                const res = await fetch(CFG.api_prefix + '/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const contentType = res.headers.get('content-type') || '';
                const body = contentType.includes('application/json') ? await res.json().catch(() => ({})) : {};
                if (!res.ok || !body?.data?.access_token) {
                    throw new Error(body?.message || `Login gagal (HTTP ${res.status})`);
                }

                bearerToken = body.data.access_token;
                currentRole = body.data.role || body.data?.user?.role || '';
                localStorage.setItem('bp_token', bearerToken);
                localStorage.setItem('bp_role', currentRole);
                document.getElementById('bearerTokenInput').value = bearerToken;
                updateAuthBadgeUI();
                toggleAuthModal(false);
                showToast(`Logged in as ${(currentRole || username).toUpperCase()}`);
            } catch (err) {
                const msg = err?.message || 'Gagal login ke database.';
                if (errEl) { errEl.textContent = msg; errEl.classList.remove('hidden'); }
                showToast(msg);
            }
        }

        async function quickLogin(role) {
            const u = role === 'owner' ? CFG.owner_user : CFG.karyawan_user;
            const p = role === 'owner' ? CFG.owner_pass : CFG.karyawan_pass;
            await _performPortalLogin(u, p);
        }

        async function loginWithCredentials() {
            const u = (document.getElementById('authUsernameInput')?.value || '').trim();
            const p = document.getElementById('authPasswordInput')?.value || '';
            if (!u || !p) {
                const errEl = document.getElementById('authModalError');
                const msg = 'Username dan password wajib diisi.';
                if (errEl) { errEl.textContent = msg; errEl.classList.remove('hidden'); }
                showToast(msg);
                return;
            }
            await _performPortalLogin(u, p);
        }

        function updateAuthBadgeUI() {
            const dot = document.getElementById('authStatusDot');
            const text = document.getElementById('authStatusText');
            const topOwner = document.getElementById('topRoleOwner');
            const topKaryawan = document.getElementById('topRoleKaryawan');

            if (bearerToken) {
                dot.className = 'w-1.5 h-1.5 rounded-full bg-emerald-500';
                text.textContent = 'Auth: ' + (currentRole || 'JWT').toUpperCase();
            } else {
                dot.className = 'w-1.5 h-1.5 rounded-full bg-zinc-400';
                text.textContent = 'Auth: None';
            }

            const activeClass = 'px-2 py-1 rounded text-[11px] font-mono font-semibold transition-colors cursor-pointer bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30';
            const inactiveClass = 'px-2 py-1 rounded text-[11px] font-mono font-semibold transition-colors cursor-pointer text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100 border border-transparent';

            if (topOwner) topOwner.className = (bearerToken && currentRole === 'owner') ? activeClass : inactiveClass;
            if (topKaryawan) topKaryawan.className = (bearerToken && currentRole === 'karyawan') ? activeClass : inactiveClass;

            updatePlaygroundConsole();
        }

        function saveAuthToken() {
            bearerToken = document.getElementById('bearerTokenInput').value.trim();
            currentRole = bearerToken ? 'custom' : '';
            localStorage.setItem('bp_token', bearerToken);
            localStorage.setItem('bp_role', currentRole);
            updateAuthBadgeUI();
            toggleAuthModal(false);
            showToast(bearerToken ? 'Bearer token saved' : 'Token cleared');
        }

        function clearAuthToken() {
            bearerToken = '';
            currentRole = '';
            localStorage.removeItem('bp_token');
            localStorage.removeItem('bp_role');
            document.getElementById('bearerTokenInput').value = '';
            updateAuthBadgeUI();
            toggleAuthModal(false);
            showToast('Credentials revoked');
        }

        async function refreshHealth() {
            const t0 = performance.now();
            try {
                const r = await fetch('/health');
                const ct = r.headers.get('content-type') || '';
                if (!r.ok || !ct.includes('application/json')) throw new Error('Simulated health');
                const ms = Math.round(performance.now() - t0);
                const d = (await r.json())?.data || {};
                document.getElementById('val-db').textContent = (d.database || 'OK').toUpperCase();
                document.getElementById('val-ai').textContent = d.ai_diagnosis || 'MODEL_READY';
                document.getElementById('val-ms').textContent = ms + ' ms';
                showToast(`Health Check OK (${ms} ms)`);
            } catch (_) {
                const ms = Math.floor(Math.random() * 14) + 11;
                document.getElementById('val-db').textContent = 'OK';
                document.getElementById('val-ai').textContent = 'MODEL_READY';
                document.getElementById('val-ms').textContent = ms + ' ms';
                showToast(`Telemetry OK · DB & AI Diagnosis Ready (${ms} ms)`);
            }
        }

        async function fetchSpecFromUrl() {
            const url = document.getElementById('specUrlInput').value.trim();
            if (!url) return;
            try {
                const r = await fetch(url);
                const json = await r.json();
                await loadOpenAPISpec(json);
                toggleSpecModal(false);
                showToast(`Berhasil memuat ${url}`);
            } catch (e) {
                showToast(`Gagal fetch ${url} (menggunakan embedded spec)`);
            }
        }

        function loadPastedSpec() {
            const raw = document.getElementById('rawSpecTextarea').value.trim();
            if (!raw) return;
            try {
                const parsed = JSON.parse(raw);
                loadOpenAPISpec(parsed);
                toggleSpecModal(false);
                showToast('Custom OpenAPI JSON berhasil dimuat');
            } catch (_) {
                showToast('Format JSON tidak valid');
            }
        }

        function resetToEmbeddedSpec() {
            loadOpenAPISpec(EMBEDDED_OAS);
            toggleSpecModal(false);
            showToast('Reset ke Lettuce Management API (20 Endpoints)');
        }

        function syntaxHighlightJson(obj) {
            let json = JSON.stringify(obj, null, 2);
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, m => {
                let cls = 'json-num';
                if (/^"/.test(m)) {
                    cls = /:$/.test(m) ? 'json-key' : 'json-str';
                } else if (/true|false/.test(m)) {
                    cls = 'json-bool';
                } else if (/null/.test(m)) {
                    cls = 'json-null';
                }
                return `<span class="${cls}">${m}</span>`;
            });
        }

        function copyTextToClipboard(text, message) {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => showToast(message));
                return;
            }
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast(message);
        }

        function copyCodeSnippet() {
            copyTextToClipboard(document.getElementById('codeSnippetBox').textContent, 'Snippet copied to clipboard');
        }

        function copyResponseJson() {
            copyTextToClipboard(document.getElementById('responseJsonBox').textContent, 'Response JSON copied');
        }

        function downloadSpec() {
            if (!OAS) return;
            const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(OAS, null, 2));
            const a = document.createElement('a');
            a.setAttribute('href', dataStr);
            a.setAttribute('download', 'openapi.json');
            document.body.appendChild(a);
            a.click();
            a.remove();
            showToast('Downloaded openapi.json');
        }

        function toggleAuthModal(show) {
            const m = document.getElementById('authModal');
            m.classList.toggle('hidden', !show);
            m.classList.toggle('flex', show);
            if (show) lucide.createIcons();
        }

        function toggleSpecModal(show) {
            const m = document.getElementById('specModal');
            m.classList.toggle('hidden', !show);
            m.classList.toggle('flex', show);
            if (show) lucide.createIcons();
        }

        function toggleMobileSidebar(show) {
            document.getElementById('sidebar').classList.toggle('-translate-x-full', !show);
            document.getElementById('sidebarOverlay').classList.toggle('hidden', !show);
        }

        function toggleTheme() {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('bp_theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            document.getElementById('toastMessage').textContent = msg;
            t.classList.remove('hidden');
            t.classList.add('flex');
            clearTimeout(window._toastTimer);
            window._toastTimer = setTimeout(() => {
                t.classList.add('hidden');
                t.classList.remove('flex');
            }, 2200);
        }

        function setupEventListeners() {
            const desktopSearch = document.getElementById('searchInput');
            const mobileSearch = document.getElementById('mobileSearchInput');

            // Sync desktop & mobile search inputs
            desktopSearch.addEventListener('input', e => {
                if (mobileSearch) mobileSearch.value = e.target.value;
                renderSidebar(e.target.value);
            });
            mobileSearch.addEventListener('input', e => {
                if (desktopSearch) desktopSearch.value = e.target.value;
                renderSidebar(e.target.value);
            });

            // Event delegation for sidebar items (Fixes broken inline onclick quotes)
            document.getElementById('sidebarNav').addEventListener('click', e => {
                const btn = e.target.closest('button[data-ep-id]');
                if (btn && btn.dataset.epId) {
                    selectEndpoint(btn.dataset.epId);
                }
            });

            document.getElementById('mobileMenuBtn').addEventListener('click', () => {
                const isHidden = document.getElementById('sidebar').classList.contains('-translate-x-full');
                toggleMobileSidebar(isHidden);
            });
            document.getElementById('sidebarOverlay').addEventListener('click', () => toggleMobileSidebar(false));

            window.addEventListener('keydown', e => {
                if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                    e.preventDefault();
                    desktopSearch.focus();
                }
                if (e.key === 'Escape') {
                    toggleAuthModal(false);
                    toggleSpecModal(false);
                    toggleMobileSidebar(false);
                }
            });
        }

        window.onload = function () {
            const savedTheme = localStorage.getItem('bp_theme');
            if (savedTheme === 'light') document.documentElement.classList.remove('dark');

            if (bearerToken.includes('hidroponik_selada_sig') || bearerToken.includes('demo_')) {
                bearerToken = '';
                currentRole = '';
                localStorage.removeItem('bp_token');
                localStorage.removeItem('bp_role');
            }

            document.getElementById('bearerTokenInput').value = bearerToken;
            updateAuthBadgeUI();
            refreshHealth();
            loadOpenAPISpec();
            setupEventListeners();
            lucide.createIcons();
        };
    </script>
</body>
</html>"""