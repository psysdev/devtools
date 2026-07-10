/* ── devtools — Web UI JavaScript ───────────────────────────
   psys.dev ecosystem design. Dark theme, purple accent, CRT scanlines.
*/

let tools = [];
let currentTool = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadTools();
});

async function loadTools() {
    try {
        const resp = await fetch('/api/tools');
        tools = await resp.json();
        renderSidebar();
        renderHome();
    } catch(e) {
        document.getElementById('tool-content').innerHTML = `
            <div style="display:flex;align-items:center;justify-content:center;height:300px;color:var(--text-dim)">
                <div style="text-align:center">
                    <div style="font-size:32px;color:var(--red)">✕</div>
                    <p style="margin-top:12px;font-family:var(--mono);font-size:14px">Connection lost</p>
                    <p style="font-family:var(--mono);font-size:12px;color:var(--text-dim)">Start the server: <span class="terminal-line">devtool --serve</span></p>
                </div>
            </div>`;
    }
}

function goHome() {
    currentTool = null;
    document.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
    renderHome();
}

function renderSidebar() {
    const sidebar = document.querySelector('.sidebar');
    // Home link at top
    const homeLink = document.createElement('div');
    homeLink.className = 'sidebar-header';
    homeLink.style.cursor = 'pointer';
    homeLink.onclick = goHome;
    homeLink.innerHTML = '<h1>devtools</h1><div class="subtitle">~ developer toolbox</div>';
    sidebar.appendChild(homeLink);

    const categories = ['utility', 'flagship'];
    const labels = { utility: 'Utilities', flagship: 'Flagship' };

    for (const cat of categories) {
        const catTools = tools.filter(t => t.category === cat);
        if (catTools.length === 0) continue;

        const header = document.createElement('div');
        header.className = 'sidebar-category';
        header.textContent = labels[cat];
        sidebar.appendChild(header);

        for (const tool of catTools) {
            const btn = document.createElement('button');
            btn.className = 'sidebar-item';
            btn.textContent = tool.name;
            btn.title = tool.description;
            btn.dataset.tool = tool.name;
            btn.onclick = () => selectTool(tool.name);
            sidebar.appendChild(btn);
        }
    }
}

function renderHome() {
    const container = document.getElementById('tool-content');
    const utilities = tools.filter(t => t.category === 'utility');
    const flagships = tools.filter(t => t.category === 'flagship');

    let html = `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px;cursor:pointer" onclick="goHome()">
            <div style="font-size:32px;line-height:1">⚡</div>
            <div>
                <h2 style="font-size:28px;font-weight:700;margin:0">devtools</h2>
                <p style="color:var(--text-muted);margin:0;font-size:14px">
                    ${tools.length} developer tools &middot; CLI + Web
                </p>
            </div>
        </div>
        <p style="font-family:var(--mono);font-size:13px;color:var(--text-dim);margin-bottom:24px">
            <span class="terminal-line" style="color:var(--green)">devtool --serve</span> &nbsp;|&nbsp; Pick a tool below or from the sidebar
        </p>
    `;

    if (flagships.length > 0) {
        html += `<h3 style="margin-top:24px;margin-bottom:8px;font-size:14px;font-weight:600;color:var(--accent);font-family:var(--mono)">✦ Flagship Tools</h3>`;
        html += '<div class="home-grid">';
        for (const t of flagships) {
            html += `
                <div class="home-card" onclick="selectTool('${t.name}')">
                    <h3>${t.name}</h3>
                    <p>${t.description}</p>
                    <span class="badge flagship">flagship</span>
                </div>
            `;
        }
        html += '</div>';
    }

    if (utilities.length > 0) {
        html += `<h3 style="margin-top:28px;margin-bottom:8px;font-size:14px;font-weight:600;color:var(--text-dim);font-family:var(--mono)">⚙ Utilities</h3>`;
        html += '<div class="home-grid">';
        for (const t of utilities) {
            html += `
                <div class="home-card" onclick="selectTool('${t.name}')">
                    <h3>${t.name}</h3>
                    <p>${t.description}</p>
                    <span class="badge">utility</span>
                </div>
            `;
        }
        html += '</div>';
    }

    container.innerHTML = html;
}

async function selectTool(name) {
    currentTool = name;
    document.querySelectorAll('.sidebar-item').forEach(el => {
        el.classList.toggle('active', el.dataset.tool === name);
    });

    const container = document.getElementById('tool-content');
    const toolInfo = tools.find(t => t.name === name);
    if (!toolInfo) return;

    container.innerHTML = `
        <div class="tool-content">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;cursor:pointer" onclick="goHome()">
                <span style="color:var(--accent);font-size:16px">←</span>
                <span style="color:var(--text-dim);font-size:13px;font-family:var(--mono)">home</span>
            </div>
            <h2>${name}</h2>
            <p>${toolInfo.description}</p>
            <div id="tool-body"></div>
        </div>`;

    const body = document.getElementById('tool-body');
    if (!body) return;

    const uiMap = {
        'json': () => renderJSON(body),
        'regex': () => renderRegex(body),
        'diff': () => renderDiff(body),
        'base64': () => renderBase64(body),
        'url': () => renderURL(body),
        'hash': () => renderHash(body),
        'color': () => renderColor(body),
        'case': () => renderCase(body),
        'lorem': () => renderLorem(body),
        'uuid': () => renderUUID(body),
        'jwt': () => renderJWT(body),
        'num': () => renderNum(body),
        'ts': () => renderTS(body),
        'html': () => renderHTML(body),
        'screenshot': () => renderScreenshot(body),
        'unwind': () => renderUnwind(body),
        'archeo': () => renderArcheo(body),
        'peephole': () => renderPeephole(body),
        'mock': () => renderMock(body),
        'retro': () => renderRetro(body),
        'lens': () => renderLens(body),
        'paper': () => renderPaper(body),
        'dash': () => renderDash(body),
        'blueprint': () => renderBlueprint(body),
        'stitch': () => renderStitch(body),
    };

    const renderer = uiMap[name];
    if (renderer) renderer();
}

function copyOutput(id) {
    const el = document.getElementById(id);
    if (el) navigator.clipboard.writeText(el.textContent);
}

/* ── Tool-specific renders with pre-populated examples ─────── */

function renderJSON(body) {
    body.innerHTML = `
        <div class="tool-layout">
            <div style="display:flex;flex-direction:column;gap:8px">
                <label>Paste JSON</label>
                <textarea id="json-input" rows="12" style="font-size:13px;flex:1" placeholder='{"key": "value", "array": [1, 2, 3]}'>{"name": "NeuroFlow", "version": "1.0.0", "stack": ["Python", "React", "PostgreSQL"], "features": {"ai": true, "crm": true, "auth": "JWT"}, "users": 1280}</textarea>
                <button onclick="formatJSON()" style="align-self:flex-start">Format <span style="font-size:11px;opacity:0.6">⌘⏎</span></button>
            </div>
            <div style="display:flex;flex-direction:column;gap:8px">
                <label>Output</label>
                <pre id="json-output" class="code-output" style="flex:1;min-height:200px"></pre>
                <button onclick="copyOutput('json-output')" style="align-self:flex-start">Copy</button>
            </div>
        </div>`;
    window.formatJSON = () => {
        fetch('/api/json', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('json-input').value})
        }).then(r=>r.text()).then(t => {
            const out = document.getElementById('json-output');
            out.textContent = t;
            out.className = 'code-output' + (t.includes('Error') ? ' error' : ' valid');
        });
    };
}

function renderRegex(body) {
    body.innerHTML = `
        <div class="tool-layout">
            <div style="display:flex;flex-direction:column;gap:8px">
                <label>Pattern</label>
                <input id="rx-pattern" type="text" value="([\\w.-]+)@([\\w.-]+)\\.(\\w+)" style="font-size:13px">
                <div class="tool-options" style="margin:0">
                    <label><input id="rx-i" type="checkbox"> i</label>
                    <label><input id="rx-m" type="checkbox"> m</label>
                    <label><input id="rx-s" type="checkbox"> s</label>
                </div>
                <label>Test string</label>
                <textarea id="rx-input" rows="6" style="font-size:13px" placeholder="Test string...">alice.smith@company.org
bob@startup.io
invalid-email</textarea>
                <button onclick="testRegex()" style="align-self:flex-start">Test <span style="font-size:11px;opacity:0.6">⌘⏎</span></button>
            </div>
            <div style="display:flex;flex-direction:column;gap:8px">
                <label>Result</label>
                <pre id="rx-output" class="code-output" style="flex:1;min-height:200px"></pre>
            </div>
        </div>`;
    window.testRegex = () => {
        let flags = '';
        if (document.getElementById('rx-i').checked) flags += 'i';
        if (document.getElementById('rx-m').checked) flags += 'm';
        if (document.getElementById('rx-s').checked) flags += 's';
        fetch('/api/regex', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                pattern:document.getElementById('rx-pattern').value,
                test_string:document.getElementById('rx-input').value, flags
            })
        }).then(r=>r.text()).then(t => document.getElementById('rx-output').textContent = t);
    };
}

function renderDiff(body) {
    body.innerHTML = `
        <div class="tool-layout tool-layout-2col" style="margin-bottom:12px">
            <div><label>Original</label><textarea id="diff-left" rows="8" style="font-size:13px">def hello(name):
    print("Hello, " + name)
    return True</textarea></div>
            <div><label>Modified</label><textarea id="diff-right" rows="8" style="font-size:13px">def hello(name, greeting="Hello"):
    msg = f"{greeting}, {name}!"
    print(msg)
    return msg</textarea></div>
        </div>
        <button onclick="runDiff()">Compare <span style="font-size:11px;opacity:0.6">⌘⏎</span></button>
        <pre id="diff-output" class="code-output" style="margin-top:12px"></pre>`;
    window.runDiff = () => {
        fetch('/api/diff', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text1:document.getElementById('diff-left').value, text2:document.getElementById('diff-right').value})
        }).then(r=>r.text()).then(t => document.getElementById('diff-output').textContent = t);
    };
}

function renderBase64(body) {
    body.innerHTML = `
        <div class="tool-options" style="margin-bottom:12px">
            <button onclick="setB64('encode')" id="b64-enc" class="active">Encode</button>
            <button onclick="setB64('decode')" id="b64-dec">Decode</button>
        </div>
        <textarea id="b64-input" rows="6" style="font-size:13px;width:100%" placeholder="Enter text...">Hello, NeuroFlow! This is a test string for base64 encoding.</textarea>
        <button onclick="convB64()" style="margin-top:8px">Convert</button>
        <pre id="b64-output" class="code-output" style="margin-top:12px"></pre>`;
    window.b64Mode = 'encode';
    window.setB64 = (m) => { b64Mode = m;
        document.getElementById('b64-enc').className=m==='encode'?'active':'';
        document.getElementById('b64-dec').className=m==='decode'?'active':'';
    };
    window.convB64 = () => {
        fetch('/api/base64', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('b64-input').value, mode:b64Mode})
        }).then(r=>r.text()).then(t => document.getElementById('b64-output').textContent = t);
    };
}

function renderURL(body) {
    body.innerHTML = `
        <div class="tool-options" style="margin-bottom:12px">
            <button onclick="setURLM('encode')" id="url-enc" class="active">Encode</button>
            <button onclick="setURLM('decode')" id="url-dec">Decode</button>
        </div>
        <textarea id="url-input" rows="4" style="font-size:13px;width:100%" placeholder="Enter text...">https://example.com/api?query=hello world&filter=name, age</textarea>
        <button onclick="convURL()" style="margin-top:8px">Convert</button>
        <pre id="url-output" class="code-output" style="margin-top:12px"></pre>`;
    window.urlMode = 'encode';
    window.setURLM = (m) => { urlMode = m;
        document.getElementById('url-enc').className=m==='encode'?'active':'';
        document.getElementById('url-dec').className=m==='decode'?'active':'';
    };
    window.convURL = () => {
        fetch('/api/url', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('url-input').value, mode:urlMode})
        }).then(r=>r.text()).then(t => document.getElementById('url-output').textContent = t);
    };
}

function renderHash(body) {
    body.innerHTML = `
        <textarea id="hash-input" rows="4" style="font-size:13px;width:100%" placeholder="Enter text to hash...">The quick brown fox jumps over the lazy dog</textarea>
        <button onclick="genHashes()" style="margin-top:8px">Generate</button>
        <div id="hash-output" style="margin-top:12px"></div>`;
    window.genHashes = () => {
        fetch('/api/hash', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('hash-input').value})
        }).then(r=>r.json()).then(data => {
            const out = document.getElementById('hash-output');
            out.innerHTML = Object.entries(data).map(([k,v]) =>
                `<div class="hash-row"><span class="hash-label">${k}</span><code onclick="navigator.clipboard.writeText(this.textContent)">${v}</code></div>`
            ).join('');
        });
    };
}

function renderColor(body) {
    body.innerHTML = `
        <input id="color-picker" type="color" value="#7C3AED" onchange="convColor()" style="width:100%;height:60px;cursor:pointer;border-radius:8px;background:var(--bg-card);border:1px solid var(--border)">
        <input id="color-input" type="text" value="#7C3AED" placeholder="#hex" style="width:100%;margin-top:8px;font-size:13px" oninput="convColor()">
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
            <button onclick="document.getElementById('color-input').value='#ff5500';convColor()" style="padding:4px 10px;font-size:11px">#ff5500</button>
            <button onclick="document.getElementById('color-input').value='rgb(16,185,129)';convColor()" style="padding:4px 10px;font-size:11px">rgb(16,185,129)</button>
            <button onclick="document.getElementById('color-input').value='hsl(200,80,50)';convColor()" style="padding:4px 10px;font-size:11px">hsl(200,80,50)</button>
        </div>
        <pre id="color-output" class="code-output" style="margin-top:12px"></pre>`;
    window.convColor = () => {
        const val = document.getElementById('color-input').value || document.getElementById('color-picker').value;
        fetch('/api/color', {method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({value: val})
        }).then(r=>r.text()).then(t => document.getElementById('color-output').textContent = t);
    };
}

function renderCase(body) {
    body.innerHTML = `
        <textarea id="case-input" rows="4" placeholder="Type text to convert..." style="width:100%;font-size:13px">hello_world_example</textarea>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px">
            <div class="case-mode" onclick="convCase('camel')"><strong>camelCase</strong><span id="case-camel"></span></div>
            <div class="case-mode" onclick="convCase('pascal')"><strong>PascalCase</strong><span id="case-pascal"></span></div>
            <div class="case-mode" onclick="convCase('snake')"><strong>snake_case</strong><span id="case-snake"></span></div>
            <div class="case-mode" onclick="convCase('kebab')"><strong>kebab-case</strong><span id="case-kebab"></span></div>
            <div class="case-mode" onclick="convCase('upper')"><strong>UPPER_CASE</strong><span id="case-upper"></span></div>
            <div class="case-mode" onclick="convCase('title')"><strong>Title Case</strong><span id="case-title"></span></div>
        </div>`;
    window.convCase = (mode) => {
        fetch('/api/case',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('case-input').value, mode})
        }).then(r=>r.text()).then(t => {
            document.getElementById('case-'+mode).textContent = ' ' + t;
            navigator.clipboard.writeText(t);
        });
    };
}

function renderLorem(body) {
    body.innerHTML = `
        <div class="tool-options">
            <label>Paragraphs: <input id="lorem-p" type="number" value="3" min="1" style="width:60px"></label>
            <label>Sentences: <input id="lorem-s" type="number" value="5" min="1" style="width:60px"></label>
            <button onclick="genLorem()">Generate</button>
        </div>
        <pre id="lorem-output" class="code-output" style="margin-top:12px"></pre>
        <button onclick="copyOutput('lorem-output')" style="margin-top:8px">Copy</button>`;
    window.genLorem = () => {
        fetch('/api/lorem',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({paragraphs:+document.getElementById('lorem-p').value, sentences:+document.getElementById('lorem-s').value})
        }).then(r=>r.text()).then(t => document.getElementById('lorem-output').textContent = t);
    };
}

function renderUUID(body) {
    body.innerHTML = `
        <div class="tool-options">
            <select id="uuid-version"><option value="v4">UUID v4 (random)</option><option value="v7">UUID v7 (time-ordered)</option></select>
            <label>Count: <input id="uuid-count" type="number" value="5" min="1" max="50" style="width:60px"></label>
            <button onclick="genUUID()">Generate</button>
        </div>
        <pre id="uuid-output" class="code-output" style="margin-top:12px"></pre>`;
    window.genUUID = () => {
        fetch('/api/uuid',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({version:document.getElementById('uuid-version').value, count:+document.getElementById('uuid-count').value})
        }).then(r=>r.text()).then(t => {
            document.getElementById('uuid-output').textContent = t;
            navigator.clipboard.writeText(t.split('\\n')[0]);
        });
    };
}

function renderJWT(body) {
    body.innerHTML = `
        <textarea id="jwt-input" rows="5" placeholder="Paste JWT token..." style="width:100%;font-size:13px">eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNzEyMzQ1Njc4LCJleHAiOjE4NzAxMTIwNzh9.GwD5tA6OaHkcFjwMd5T_ZsCqgqP1JkQdNExH1HlG2eI</textarea>
        <button onclick="decJWT()" style="margin-top:8px">Decode</button>
        <pre id="jwt-output" class="code-output" style="margin-top:12px"></pre>`;
    window.decJWT = () => {
        fetch('/api/jwt',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({token:document.getElementById('jwt-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('jwt-output').textContent = t);
    };
}

function renderNum(body) {
    body.innerHTML = `
        <input id="num-input" type="text" placeholder="e.g. 255, 0xFF, 0b11111111" style="width:100%;font-size:13px;font-family:var(--mono)" oninput="convNum()" value="255">
        <pre id="num-output" class="code-output" style="margin-top:12px"></pre>`;
    window.convNum = () => {
        fetch('/api/num',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({value:document.getElementById('num-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('num-output').textContent = t);
    };
}

function renderTS(body) {
    body.innerHTML = `
        <input id="ts-input" type="text" placeholder="e.g. 1712345678 or 2024-04-05 12:00:00" style="width:100%;font-size:13px" value="1712345678">
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap">
            <button onclick="document.getElementById('ts-input').value='1712345678';convTS()" style="padding:4px 10px;font-size:11px">Timestamp</button>
            <button onclick="document.getElementById('ts-input').value='2024-04-05 12:00:00';convTS()" style="padding:4px 10px;font-size:11px">Date string</button>
            <button onclick="document.getElementById('ts-input').value='1712345678000';convTS()" style="padding:4px 10px;font-size:11px">Milliseconds</button>
        </div>
        <pre id="ts-output" class="code-output" style="margin-top:12px"></pre>`;
    window.convTS = () => {
        fetch('/api/ts',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({value:document.getElementById('ts-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('ts-output').textContent = t);
    };
}

function renderHTML(body) {
    body.innerHTML = `
        <div class="tool-options" style="margin-bottom:12px">
            <button onclick="setHTMLM('encode')" id="html-enc" class="active">Encode</button>
            <button onclick="setHTMLM('decode')" id="html-dec">Decode</button>
        </div>
        <textarea id="html-input" rows="4" style="font-size:13px;width:100%" placeholder="Enter text..."><div class="main">Hello & welcome</div></textarea>
        <button onclick="convHTML()" style="margin-top:8px">Convert</button>
        <pre id="html-output" class="code-output" style="margin-top:12px"></pre>`;
    window.htmlMode = 'encode';
    window.setHTMLM = (m) => { htmlMode = m;
        document.getElementById('html-enc').className=m==='encode'?'active':'';
        document.getElementById('html-dec').className=m==='decode'?'active':'';
    };
    window.convHTML = () => {
        fetch('/api/html',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({text:document.getElementById('html-input').value, mode:htmlMode})
        }).then(r=>r.text()).then(t => document.getElementById('html-output').textContent = t);
    };
}

function renderScreenshot(body) {
    body.innerHTML = `
        <div class="tool-options">
            <label>Language: <select id="shot-lang">
                <option value="python">Python</option><option value="javascript">JS</option><option value="typescript">TS</option>
                <option value="html">HTML</option><option value="css">CSS</option><option value="go">Go</option>
                <option value="rust">Rust</option><option value="java">Java</option><option value="sql">SQL</option><option value="bash">Bash</option>
            </select></label>
            <label>Title: <input id="shot-title" value="example.py" style="width:120px;font-size:13px"></label>
        </div>
        <textarea id="shot-input" rows="8" placeholder="Paste code here..." style="width:100%;font-size:13px">def fibonacci(n):
    """Generate the Fibonacci sequence up to n."""
    a, b = 0, 1
    result = []
    while a < n:
        result.append(a)
        a, b = b, a + b
    return result

print(fibonacci(100))</textarea>
        <button onclick="genShot()" style="margin-top:8px">Generate Screenshot</button>
        <div id="shot-preview" class="preview-area" style="margin-top:12px">Preview will appear here</div>
        <a id="shot-dl" style="display:none;margin-top:8px;display:inline-block;color:var(--accent)">Download PNG</a>`;
    window.genShot = async () => {
        fetch('/api/screenshot',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                code:document.getElementById('shot-input').value,
                lang:document.getElementById('shot-lang').value,
                title:document.getElementById('shot-title').value || 'code'
            })
        }).then(r=>r.blob()).then(blob => {
            const url = URL.createObjectURL(blob);
            document.getElementById('shot-preview').innerHTML = `<img src="${url}" style="max-width:100%;border-radius:6px;box-shadow:0 4px 20px rgba(0,0,0,0.4)">`;
            const dl = document.getElementById('shot-dl');
            dl.href = url; dl.download = 'screenshot.png';
            dl.style.display = 'inline-block';
            dl.textContent = `Download PNG (${(blob.size/1024).toFixed(0)}KB)`;
        });
    };
}

function renderUnwind(body) {
    body.innerHTML = `
        <textarea id="unwind-input" rows="10" placeholder="Paste a Python stack trace..." style="width:100%;font-size:13px">Traceback (most recent call last):
  File "main.py", line 22, in <module>
    result = calculate_interest(1000, 0.05, "3 years")
  File "main.py", line 15, in calculate_interest
    return principal * rate * time
ZeroDivisionError: division by zero</textarea>
        <button onclick="doUnwind()" style="margin-top:8px">Humanize</button>
        <pre id="unwind-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doUnwind = () => {
        fetch('/api/unwind',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({trace:document.getElementById('unwind-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('unwind-output').textContent = t);
    };
}

function renderMock(body) {
    body.innerHTML = `
        <div class="tool-options">
            <input id="mock-schema" type="text" value="name:string, age:int, email:email, city:city, active:bool" style="width:60%;font-size:13px">
            <label>Count: <input id="mock-count" type="number" value="3" min="1" style="width:60px"></label>
            <select id="mock-fmt"><option value="json">JSON</option><option value="csv">CSV</option><option value="sql">SQL</option></select>
        </div>
        <button onclick="doMock()">Generate</button>
        <pre id="mock-output" class="code-output" style="margin-top:12px"></pre>
        <button onclick="copyOutput('mock-output')" style="margin-top:8px">Copy</button>`;
    window.doMock = () => {
        fetch('/api/mock',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                schema_def:document.getElementById('mock-schema').value,
                count:+document.getElementById('mock-count').value,
                format:document.getElementById('mock-fmt').value
            })
        }).then(r=>r.text()).then(t => document.getElementById('mock-output').textContent = t);
    };
}

function renderLens(body) {
    body.innerHTML = `
        <textarea id="lens-input" rows="10" placeholder='[{"name": "Alice", "age": 30}]' style="width:100%;font-size:13px">[{"name":"Alice","age":30,"email":"alice@example.com","active":true,"score":85.5},{"name":"Bob","age":25,"email":"bob@test.org","active":false,"score":92.0},{"name":"Charlie","age":35,"email":"charlie@corp.net","active":true,"score":78.0}]</textarea>
        <button onclick="doLens()" style="margin-top:8px">Infer Schema</button>
        <pre id="lens-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doLens = () => {
        fetch('/api/lens',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({data:document.getElementById('lens-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('lens-output').textContent = t);
    };
}

function renderPeephole(body) {
    body.innerHTML = `
        <textarea id="peep-input" rows="10" placeholder="Paste a Python function here..." style="width:100%;font-size:13px">def process_order(item, quantity, is_premium):
    if quantity <= 0:
        return "Invalid quantity"
    total = item.price * quantity
    if is_premium:
        total *= 0.9
        if quantity > 10:
            total *= 0.95
    elif quantity > 5:
        total *= 0.95
    else:
        if total > 100:
            total -= 10
    return round(total, 2)</textarea>
        <button onclick="doPeep()" style="margin-top:8px">Visualize</button>
        <pre id="peep-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doPeep = () => {
        fetch('/api/peephole',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({code:document.getElementById('peep-input').value})
        }).then(r=>r.text()).then(t => document.getElementById('peep-output').textContent = t);
    };
}

function renderBlueprint(body) {
    body.innerHTML = `
        <textarea id="bp-input" rows="10" placeholder="services:&#10;  api:&#10;    type: fastapi&#10;    depends_on: [db]" style="width:100%;font-size:13px">services:
  frontend:
    type: React
    depends_on: [api, auth]
  api:
    type: FastAPI
    depends_on: [db, redis]
  auth:
    type: Auth0
    depends_on: [db]
  db:
    type: PostgreSQL
  redis:
    type: Cache</textarea>
        <div class="tool-options">
            <select id="bp-fmt"><option value="ascii">ASCII Diagram</option><option value="mermaid">Mermaid</option></select>
            <button onclick="doBP()">Generate</button>
        </div>
        <pre id="bp-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doBP = () => {
        fetch('/api/blueprint',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({yaml:document.getElementById('bp-input').value, format:document.getElementById('bp-fmt').value})
        }).then(r=>r.text()).then(t => document.getElementById('bp-output').textContent = t);
    };
}

function renderPaper(body) {
    body.innerHTML = `
        <div class="tool-options">
            <select id="paper-topic">
                <option value="git">Git</option><option value="docker">Docker</option>
                <option value="python">Python</option><option value="sql">SQL</option><option value="vim">Vim</option>
            </select>
            <button onclick="doPaper()">Generate</button>
        </div>
        <pre id="paper-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doPaper = () => {
        fetch('/api/paper',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({topic:document.getElementById('paper-topic').value})
        }).then(r=>r.text()).then(t => document.getElementById('paper-output').textContent = t);
    };
}

function renderArcheo(body) {
    body.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:8px;max-width:500px">
            <label>File path:</label>
            <input id="archeo-file" type="text" placeholder="app.py" value="app.py" style="font-size:13px">
            <label>Lines:</label>
            <input id="archeo-lines" type="text" placeholder="42-48" value="1-20" style="font-size:13px">
            <button onclick="doArcheo()" style="align-self:flex-start">Investigate</button>
            <p style="font-size:12px;color:var(--text-dim)">Run from a git repository. The file path is relative to the git root.</p>
        </div>
        <pre id="archeo-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doArcheo = () => {
        fetch('/api/archeo',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({file:document.getElementById('archeo-file').value, lines:document.getElementById('archeo-lines').value})
        }).then(r=>r.text()).then(t => document.getElementById('archeo-output').textContent = t);
    };
}

function renderRetro(body) {
    body.innerHTML = `
        <p>Terminal Time Machine &mdash; Upload a .cast file (asciinema format) to convert to animated SVG.</p>
        <div class="tool-options" style="margin-top:12px">
            <input id="retro-file" type="file" accept=".cast" style="display:none">
            <button onclick="document.getElementById('retro-file').click()" style="margin:0" class="btn-file">Choose .cast file</button>
            <span id="retro-filename" style="color:var(--text-dim);font-size:13px">No file selected</span>
            <label style="margin-left:auto">Speed: <input id="retro-speed" type="number" value="2" min="1" style="width:60px">x</label>
        </div>
        <p style="font-size:12px;color:var(--text-dim);margin-top:8px">
            Record a session: <span class="terminal-line">asciinema rec session.cast</span>
        </p>
        <pre id="retro-output" class="code-output" style="margin-top:12px">Upload a .cast file to begin...</pre>`;
    document.getElementById('retro-file').addEventListener('change', async function(e) {
        const file = e.target.files[0];
        if (!file) return;
        document.getElementById('retro-filename').textContent = file.name;
        const text = await file.text();
        fetch('/api/retro',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({cast:text, speed:+document.getElementById('retro-speed').value})
        }).then(r=>r.text()).then(t=>document.getElementById('retro-output').textContent=t);
    });
}

function renderDash(body) {
    body.innerHTML = `
        <textarea id="dash-config" rows="10" placeholder="Paste dashboard YAML config..." style="width:100%;font-size:13px">panels:
  - type: clock
    title: Current Time
  - type: quote
    title: Dev Wisdom
  - type: info
    title: Status
    text: All systems nominal</textarea>
        <button onclick="doDash()" style="margin-top:8px">Render</button>
        <pre id="dash-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doDash = () => {
        fetch('/api/dash',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({config:document.getElementById('dash-config').value})
        }).then(r=>r.text()).then(t => document.getElementById('dash-output').textContent = t);
    };
}

function renderStitch(body) {
    body.innerHTML = `
        <p>Combine screenshots into an HTML storyboard. Enter a file path (glob pattern).</p>
        <div style="display:flex;flex-direction:column;gap:8px;max-width:500px;margin-top:12px">
            <label>Frames (glob pattern):</label>
            <input id="stitch-dir" type="text" placeholder="./screenshots/*.png" value="./screenshots/*.png" style="font-size:13px">
            <label>Captions (comma-separated):</label>
            <input id="stitch-captions" type="text" placeholder="Intro, Demo, Results" value="Architecture, Implementation, Results" style="font-size:13px">
            <button onclick="doStitch()" style="align-self:flex-start">Create Storyboard</button>
        </div>
        <pre id="stitch-output" class="code-output" style="margin-top:12px"></pre>`;
    window.doStitch = () => {
        fetch('/api/stitch',{method:'POST',headers:{'Content-Type':'application/json'},
            body:JSON.stringify({frames:document.getElementById('stitch-dir').value, captions:document.getElementById('stitch-captions').value})
        }).then(r=>r.text()).then(t => document.getElementById('stitch-output').textContent = t);
    };
}

/* ── Keyboard: Ctrl+Enter triggers first button ─── */
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const btn = document.querySelector('.tool-content button:not(.sidebar-item)');
        if (btn) btn.click();
    }
});
