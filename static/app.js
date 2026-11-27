// DocuLens Enterprise AI - Modern Web Controller with Role-Based Access Control (RBAC)
// Pure vanilla ES6+, zero external build dependencies

let currentAuthToken = localStorage.getItem('doculens_jwt') || '';
let currentUserInfo = null;

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function showToast(message, isSuccess = true) {
    const toast = document.getElementById('toastNotification');
    const toastMsg = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    toastIcon.textContent = isSuccess ? '✅' : '⚠️';
    toast.className = `fixed top-5 right-5 z-50 px-4 py-3 rounded-xl shadow-2xl flex items-center gap-2.5 transition-all text-xs font-semibold ${
        isSuccess ? 'bg-emerald-950/90 border border-emerald-700/80 text-emerald-200' : 'bg-rose-950/90 border border-rose-700/80 text-rose-200'
    }`;
    toast.classList.remove('hidden');

    setTimeout(() => {
        toast.classList.add('hidden');
    }, 4500);
}

// Wrapper for authenticated fetch calls
async function authFetch(url, options = {}) {
    const headers = options.headers ? { ...options.headers } : {};
    if (currentAuthToken) {
        headers['Authorization'] = `Bearer ${currentAuthToken}`;
    }
    return fetch(url, { ...options, headers });
}

// Enter the Main Studio after successful verification
function enterStudio(user) {
    currentUserInfo = user;
    const gateView = document.getElementById('authGateView');
    const studioView = document.getElementById('appStudioView');

    if (gateView) gateView.classList.add('hidden');
    if (studioView) studioView.classList.remove('hidden');

    updateProfileUI(user);
    fetchDocuments();
    fetchSystemStatus();

    showToast(`Welcome ${user.full_name} (${user.role.toUpperCase()}) • Studio Access Permitted`, true);
}

// Exit Studio back to Auth Gate Screen
function exitStudio() {
    currentAuthToken = '';
    currentUserInfo = null;
    localStorage.removeItem('doculens_jwt');

    const gateView = document.getElementById('authGateView');
    const studioView = document.getElementById('appStudioView');
    const tabSignIn = document.getElementById('gateTabSignInBtn');
    const tabRegister = document.getElementById('gateTabRegisterBtn');
    const signInForm = document.getElementById('gateSignInForm');
    const registerForm = document.getElementById('gateRegisterForm');

    if (studioView) studioView.classList.add('hidden');
    if (gateView) gateView.classList.remove('hidden');

    // Always reset to Sign In tab on logout so user is not stuck on the Register form
    if (tabSignIn && tabRegister && signInForm && registerForm) {
        tabSignIn.className = 'flex-1 py-2 text-xs font-bold rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 transition';
        tabRegister.className = 'flex-1 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition';
        signInForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    }

    showToast('Signed out. Please sign in or register to access confidential files.', false);
}

// Update UI to reflect current user identity
function updateProfileUI(user) {
    currentUserInfo = user;
    const badge = document.getElementById('currentUserRoleBadge');
    const nameEl = document.getElementById('navUserName');

    if (nameEl && user) {
        nameEl.textContent = user.full_name || user.username;
    }

    if (badge && user) {
        badge.textContent = user.role.toUpperCase();
        if (user.role === 'admin') {
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-950 text-indigo-400 border border-indigo-800';
        } else if (user.role === 'auditor') {
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-950 text-amber-400 border border-amber-800';
        } else {
            badge.className = 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-sky-950 text-sky-400 border border-sky-800';
        }
    }
}

// Switch user using demo credentials
async function switchDemoUser(username) {
    const passwords = {
        'admin': 'admin123',
        'auditor': 'auditor123'
    };
    const password = passwords[username] || 'admin123';

    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');

        currentAuthToken = data.token;
        localStorage.setItem('doculens_jwt', data.token);

        enterStudio(data.user);
    } catch (err) {
        showToast(`Authentication Error: ${err.message}`, false);
    }
}

// Fetch Corpus Documents & Populate Sidebar + Scope Selector
async function fetchDocuments() {
    try {
        const res = await authFetch('/api/documents');
        const data = await res.json();

        const badge = document.getElementById('docBadgeCount');
        if (badge) badge.textContent = `${data.count} of ${data.total_corpus_count} Authorized`;

        const container = document.getElementById('documentListContainer');
        const select = document.getElementById('docScopeSelect');

        if (container) {
            container.innerHTML = '';
            if (!data.documents || data.documents.length === 0) {
                container.innerHTML = '<div class="text-xs text-slate-500 font-mono p-3">No authorized documents for this user identity.</div>';
            } else {
                data.documents.forEach(doc => {
                    const typeIcon = doc.type === 'resume' ? '👤' : (doc.type === 'disputed' ? '🚨' : (doc.type === 'invoice' ? '🧾' : '📜'));
                    const typeColor = doc.type === 'disputed' ? 'text-rose-400 bg-rose-950/60 border-rose-800/60' : 'text-sky-400 bg-sky-950/60 border-sky-800/60';
                    
                    const item = document.createElement('div');
                    item.className = 'group p-2.5 rounded-xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800/80 transition-all cursor-pointer flex items-center justify-between';
                    item.innerHTML = `
                        <div class="flex items-center space-x-2.5 overflow-hidden">
                            <div class="w-7 h-7 rounded-lg ${typeColor} border flex items-center justify-center text-xs flex-shrink-0">
                                ${typeIcon}
                            </div>
                            <div class="overflow-hidden">
                                <p class="text-xs font-semibold text-slate-200 truncate group-hover:text-white" title="${escapeHtml(doc.filename)}">${escapeHtml(doc.filename)}</p>
                                <p class="text-[10px] text-slate-400 font-mono">${doc.total_pages} pg • ${doc.chunks} chunks</p>
                            </div>
                        </div>
                        <span class="text-[10px] font-mono text-slate-400 group-hover:text-sky-400">→</span>
                    `;
                    item.addEventListener('click', () => {
                        if (select) {
                            select.value = doc.filename;
                            showToast(`Search scope set to: ${doc.filename}`, true);
                        }
                    });
                    container.appendChild(item);
                });
            }
        }

        if (select) {
            const currentVal = select.value;
            select.innerHTML = '<option value="All Documents">All Authorized Documents</option>';
            if (data.documents) {
                data.documents.forEach(doc => {
                    const opt = document.createElement('option');
                    opt.value = doc.filename;
                    opt.textContent = `${doc.filename} (${doc.total_pages} pg)`;
                    select.appendChild(opt);
                });
            }
            if (currentVal && Array.from(select.options).some(o => o.value === currentVal)) {
                select.value = currentVal;
            }
        }
    } catch (err) {
        console.error("Failed to fetch documents:", err);
    }
}

// Drawer Controller
async function openDrawer(filename, page) {
    const drawer = document.getElementById('documentDrawer');
    const backdrop = document.getElementById('drawerBackdrop');
    const titleEl = document.getElementById('drawerDocTitle');
    const pageEl = document.getElementById('drawerDocPage');
    const textEl = document.getElementById('drawerDocText');

    if (!drawer || !backdrop) return;

    titleEl.textContent = filename;
    pageEl.textContent = `Page ${page}`;
    textEl.textContent = "Verifying authorization and loading excerpt...";

    backdrop.classList.remove('hidden');
    drawer.classList.remove('translate-x-full');

    try {
        const res = await authFetch(`/api/document-page/${encodeURIComponent(filename)}/${page}`);
        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || "Access Denied");
        }
        const data = await res.json();
        textEl.textContent = data.content || "Passage content unavailable.";
    } catch (err) {
        textEl.innerHTML = `<span class="text-rose-400 font-bold">🔒 ${escapeHtml(err.message)}</span>`;
    }
}

function closeDrawer() {
    const drawer = document.getElementById('documentDrawer');
    const backdrop = document.getElementById('drawerBackdrop');
    if (drawer) drawer.classList.add('translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
}

// System Telemetry
async function fetchSystemStatus() {
    try {
        const res = await authFetch('/api/system-status');
        const data = await res.json();
        const llmEl = document.getElementById('telemetryLLM');
        const tagEl = document.getElementById('modelInferenceTag');
        if (llmEl) llmEl.textContent = `${data.llm_engine} (${data.device})`;
        if (tagEl) tagEl.textContent = `Engine: ${data.llm_engine} (${data.device}) • Zero Hallucination • RBAC Enabled`;
    } catch (err) {
        console.error("Failed to fetch telemetry:", err);
    }
}

// File Upload
async function handleFileUpload(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Only PDF files are supported.', false);
        return;
    }

    const loader = document.getElementById('uploadLoader');
    if (loader) loader.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const res = await authFetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload failed');

        showToast(`Indexed & Bound to ${data.owner}: ${data.filename} (${data.pages} pgs)`, true);
        await fetchDocuments();

        const select = document.getElementById('docScopeSelect');
        if (select) select.value = data.filename;
    } catch (err) {
        showToast(`Upload Error: ${err.message}`, false);
    } finally {
        if (loader) loader.classList.add('hidden');
    }
}

// Query Execution with Pre-Retrieval Filtering
async function executeAudit() {
    const input = document.getElementById('mainQueryInput');
    const btn = document.getElementById('askCopilotBtn');
    const btnText = document.getElementById('askBtnText');
    const answerEl = document.getElementById('answerContent');
    const statusBadge = document.getElementById('statusBadge');
    const citSection = document.getElementById('citationPillsSection');
    const citContainer = document.getElementById('citationsPillContainer');
    const evidSection = document.getElementById('evidenceSection');
    const evidList = document.getElementById('evidencePassagesList');
    const evidCount = document.getElementById('evidenceCount');
    const scopeSelect = document.getElementById('docScopeSelect');

    const query = input ? input.value.trim() : '';
    if (!query) {
        showToast('Please enter a query or select a prompt chip.', false);
        return;
    }

    const selectedScope = scopeSelect ? scopeSelect.value : 'All Documents';
    const targetDoc = selectedScope === 'All Documents' ? null : selectedScope;

    if (btn) btn.disabled = true;
    if (btnText) btnText.textContent = 'Synthesizing...';
    if (answerEl) answerEl.innerHTML = '<div class="flex items-center gap-2 text-sky-400 font-mono text-xs"><span class="animate-spin">⏳</span> Running Authorized Hybrid Vector+BM25 Search, Cross-Encoder Reranking, and LLM Generation...</div>';

    try {
        const res = await authFetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                target_document: targetDoc,
                top_k: 5
            })
        });

        const data = await res.json();

        if (res.status === 403) {
            // Role-Based Access Control Violation
            if (statusBadge) {
                statusBadge.classList.remove('hidden');
                statusBadge.className = 'text-xs font-extrabold px-3.5 py-1 rounded-full uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30';
                statusBadge.textContent = '🔒 ACCESS FORBIDDEN (RBAC)';
            }
            if (answerEl) {
                answerEl.innerHTML = `
                    <div class="p-4 bg-rose-950/40 border border-rose-800/80 rounded-xl space-y-2">
                        <div class="font-bold text-rose-400 text-xs">⚠️ Document Clearance Required</div>
                        <div class="text-xs text-rose-200 leading-relaxed">${escapeHtml(data.detail)}</div>
                        <div class="text-[11px] text-slate-400 font-mono">Switch to an account with higher clearance (e.g. Administrator or Auditor) to query this document.</div>
                    </div>
                `;
            }
            if (citSection) citSection.classList.add('hidden');
            if (evidSection) evidSection.classList.add('hidden');
            showToast('Authorization Denied: Clearance restricted.', false);
            return;
        }

        if (!res.ok) {
            throw new Error(data.detail || 'Query execution failed');
        }

        // Status Badge
        if (statusBadge) {
            statusBadge.classList.remove('hidden');
            if (data.has_discrepancy) {
                statusBadge.className = 'text-xs font-extrabold px-3.5 py-1 rounded-full uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30';
                statusBadge.textContent = '🚨 AUDIT DISCREPANCY / NON-COMPLIANCE DETECTED';
            } else {
                statusBadge.className = 'text-xs font-extrabold px-3.5 py-1 rounded-full uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
                statusBadge.textContent = '✅ COMPLIANT & AUTHORIZED GROUNDING';
            }
        }

        // Check if Local Laptop Ollama bridge should synthesize the answer
        if (localStorage.getItem("doculens_use_local_ollama") === "true" && data.evidence_passages && data.evidence_passages.length > 0) {
            if (data.answer.includes("AI Neural Model Inference Unavailable") || data.answer.includes("⚠️")) {
                try {
                    const localModel = localStorage.getItem("doculens_local_model_name") || "qwen2.5:1.5b";
                    const contextText = data.evidence_passages.map((p, i) => `--- EXCERPT ${i+1} [Doc: ${p.document}, Page: ${p.page}] ---\n${p.content}`).join("\n\n");
                    const localPrompt = `You are an enterprise document intelligence assistant.\nAnswer the user's question accurately, directly, and professionally based strictly on the provided source excerpts.\nStructure your answer with clear bullet points. Answer ONLY what the user asks.\n\nContext:\n${contextText}\n\nQuestion: ${query}\n\nAnswer:`;

                    const localResp = await fetch("http://localhost:11434/api/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            model: localModel,
                            messages: [
                                { role: "system", content: "You are an enterprise document assistant. Answer accurately based on context. Be concise and use bullet points." },
                                { role: "user", content: localPrompt }
                            ],
                            stream: false,
                            options: { temperature: 0.1, num_predict: 450 }
                        })
                    });
                    if (localResp.ok) {
                        const localData = await localResp.json();
                        const localAns = localData.message ? localData.message.content : "";
                        if (localAns) {
                            data.answer = localAns + `\n\n[Doc: ${data.evidence_passages[0].document}, Page: ${data.evidence_passages[0].page}]`;
                        }
                    }
                } catch (localErr) {
                    console.warn("Local Ollama synthesis fallback error:", localErr);
                }
            }
        }

        // Answer formatting
        let formatted = escapeHtml(data.answer);
        formatted = formatted.replace(/\[(?:Doc:\s*)?([^,\]]+),\s*Page:\s*(\d+)(?:,\s*Section:[^\]]*)?\]/g, (match, doc, page) => {
            const d = doc.trim();
            const p = page.trim();
            return `<button type="button" class="inline-citation inline-flex items-center gap-1 px-2 py-0.5 rounded bg-sky-950 border border-sky-800 text-sky-300 font-mono text-[11px] hover:bg-sky-900 transition mx-1" data-doc="${escapeHtml(d)}" data-page="${p}">📄 ${escapeHtml(d)}:p${p}</button>`;
        });

        if (answerEl) {
            answerEl.innerHTML = formatted;
        }

        // Citations Section
        if (citSection && citContainer) {
            if (data.citations && data.citations.length > 0) {
                citSection.classList.remove('hidden');
                citContainer.innerHTML = data.citations.map(c => `
                    <button type="button" class="citation-pill px-3 py-1.5 rounded-lg bg-sky-950/60 hover:bg-sky-900/80 border border-sky-800/80 text-sky-300 font-mono text-xs flex items-center gap-1.5 transition" data-doc="${escapeHtml(c.document)}" data-page="${c.page}">
                        <span>📑</span> <span>${escapeHtml(c.document)} (pg ${c.page})</span>
                    </button>
                `).join('');
            } else {
                citSection.classList.add('hidden');
            }
        }

        // Evidence Section
        if (evidSection && evidList && evidCount) {
            if (data.retrieved_passages && data.retrieved_passages.length > 0) {
                evidSection.classList.remove('hidden');
                evidCount.textContent = data.retrieved_passages.length;
                evidList.innerHTML = data.retrieved_passages.map((p, idx) => {
                    const score = (p.rerank_score !== undefined && p.rerank_score !== null) ? Number(p.rerank_score).toFixed(4) : 'N/A';
                    const passageText = p.content || p.child_content || p.parent_content || '';
                    return `
                        <div class="p-3 bg-slate-900/90 rounded-xl border border-slate-800 text-xs text-slate-300 space-y-1.5">
                            <div class="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                                <span class="text-sky-400 font-semibold">#${idx + 1} • ${escapeHtml(p.document_filename)} (Page ${p.page_number})</span>
                                <span class="bg-slate-800 px-2 py-0.5 rounded text-amber-300">Rerank Score: ${score}</span>
                            </div>
                            <div class="font-mono text-slate-200 text-[11px] leading-relaxed whitespace-pre-wrap">${escapeHtml(passageText)}</div>
                        </div>
                    `;
                }).join('');
            } else {
                evidSection.classList.add('hidden');
            }
        }

    } catch (err) {
        if (answerEl) {
            answerEl.innerHTML = `<span class="text-rose-400">Error executing audit: ${escapeHtml(err.message)}</span>`;
        }
        showToast(`Query Failed: ${err.message}`, false);
    } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.textContent = 'Ask Copilot';
    }
}

// Benchmark Suite with RBAC
async function loadBenchmarkData(force = false) {
    const table = document.getElementById('benchmarkDetailsTable');
    if (table) table.innerHTML = '<div class="text-xs text-sky-400 font-mono p-4">Running automated RAG Triad test evaluation...</div>';

    try {
        const res = await authFetch(`/api/benchmark?force=${force}`);
        const data = await res.json();

        if (res.status === 403) {
            if (table) {
                table.innerHTML = `
                    <div class="p-5 bg-rose-950/30 border border-rose-800/80 rounded-xl space-y-2">
                        <div class="font-bold text-rose-400 text-xs flex items-center gap-1.5">🔒 Restricted to Administrator & Auditor Roles</div>
                        <div class="text-xs text-slate-300 leading-relaxed">${escapeHtml(data.detail)}</div>
                        <div class="text-[11px] text-slate-400 font-mono">Use the User Profile dropdown at the top to switch to 'Admin' or 'Auditor' to access the automated CI/CD benchmark suite.</div>
                    </div>
                `;
            }
            return;
        }

        const kpiF = document.getElementById('kpiFaithfulness');
        const kpiR = document.getElementById('kpiRecall');
        const kpiP = document.getElementById('kpiPrecision');
        const kpiD = document.getElementById('kpiDispute');

        if (kpiF) kpiF.textContent = `${(data.avg_faithfulness * 100).toFixed(1)}%`;
        if (kpiR) kpiR.textContent = `${(data.avg_context_recall * 100).toFixed(1)}%`;
        if (kpiP) kpiP.textContent = `${(data.avg_citation_precision * 100).toFixed(1)}%`;
        if (kpiD) kpiD.textContent = `${(data.discrepancy_detection_rate * 100).toFixed(1)}%`;

        if (table && data.detailed_results) {
            table.innerHTML = `
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-mono">
                        <thead>
                            <tr class="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                                <th class="pb-2.5">Test ID</th>
                                <th class="pb-2.5">Category</th>
                                <th class="pb-2.5 text-center">Context Recall</th>
                                <th class="pb-2.5 text-center">Faithfulness</th>
                                <th class="pb-2.5 text-center">Citation Precision</th>
                                <th class="pb-2.5 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800/60">
                            ${data.detailed_results.map(r => `
                                <tr class="hover:bg-slate-900/40">
                                    <td class="py-2.5 font-bold text-sky-400">${r.test_id}</td>
                                    <td class="py-2.5 text-slate-200">${escapeHtml(r.category)}</td>
                                    <td class="py-2.5 text-center text-emerald-400">${(r.context_recall * 100).toFixed(0)}%</td>
                                    <td class="py-2.5 text-center text-emerald-400">${(r.faithfulness * 100).toFixed(0)}%</td>
                                    <td class="py-2.5 text-center text-emerald-400">${(r.citation_precision * 100).toFixed(0)}%</td>
                                    <td class="py-2.5 text-center">
                                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${r.discrepancy_detected ? 'bg-amber-950 text-amber-400 border border-amber-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'}">
                                            ${r.discrepancy_detected ? 'DISCREPANCY' : 'PASSED'}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
    } catch (err) {
        if (table) table.innerHTML = `<div class="text-xs text-rose-400 font-mono p-4">Benchmark error: ${escapeHtml(err.message)}</div>`;
    }
}

// Tab Switcher
function switchTab(targetTab) {
    const viewCopilot = document.getElementById('viewCopilot');
    const viewBenchmark = document.getElementById('viewBenchmark');
    const tabCopilot = document.getElementById('tabBtnCopilot');
    const tabBenchmark = document.getElementById('tabBtnBenchmark');

    if (targetTab === 'copilot') {
        if (viewCopilot) viewCopilot.classList.remove('hidden');
        if (viewBenchmark) viewBenchmark.classList.add('hidden');
        if (tabCopilot) {
            tabCopilot.className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-sky-500/10 text-sky-400 border border-sky-500/30';
        }
        if (tabBenchmark) {
            tabBenchmark.className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800/50';
        }
    } else {
        if (viewCopilot) viewCopilot.classList.add('hidden');
        if (viewBenchmark) viewBenchmark.classList.remove('hidden');
        if (tabBenchmark) {
            tabBenchmark.className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 bg-sky-500/10 text-sky-400 border border-sky-500/30';
        }
        if (tabCopilot) {
            tabCopilot.className = 'px-4 py-2 rounded-lg text-xs font-bold transition flex items-center gap-2 text-slate-400 hover:text-white hover:bg-slate-800/50';
        }
        loadBenchmarkData(false);
    }
}

// DOM Ready Bindings
document.addEventListener('DOMContentLoaded', async () => {

    // ================= 1. INITIAL AUTHENTICATION GATE CHECK =================
    // Only permit access if valid token exists; otherwise display Login/Register Gate screen
    if (!currentAuthToken) {
        document.getElementById('authGateView').classList.remove('hidden');
        document.getElementById('appStudioView').classList.add('hidden');
    } else {
        try {
            const res = await authFetch('/api/auth/me');
            if (res.ok) {
                const data = await res.json();
                enterStudio(data.user);
            } else {
                exitStudio();
            }
        } catch (e) {
            exitStudio();
        }
    }

    // ================= 2. GATE TAB TOGGLES =================
    const tabSignIn = document.getElementById('gateTabSignInBtn');
    const tabRegister = document.getElementById('gateTabRegisterBtn');
    const signInForm = document.getElementById('gateSignInForm');
    const registerForm = document.getElementById('gateRegisterForm');

    if (tabSignIn && tabRegister && signInForm && registerForm) {
        tabSignIn.addEventListener('click', () => {
            tabSignIn.className = 'flex-1 py-2 text-xs font-bold rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30 transition';
            tabRegister.className = 'flex-1 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition';
            signInForm.classList.remove('hidden');
            registerForm.classList.add('hidden');
        });
        tabRegister.addEventListener('click', () => {
            tabRegister.className = 'flex-1 py-2 text-xs font-bold rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition';
            tabSignIn.className = 'flex-1 py-2 text-xs font-bold rounded-lg text-slate-400 hover:text-white transition';
            registerForm.classList.remove('hidden');
            signInForm.classList.add('hidden');
        });
    }

    // ================= 3. GATE FORM SUBMISSIONS =================
    if (signInForm) {
        signInForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('gateLoginUsername').value.trim();
            const password = document.getElementById('gateLoginPassword').value;

            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Authentication failed');

                currentAuthToken = data.token;
                localStorage.setItem('doculens_jwt', data.token);

                const loginUserEl = document.getElementById('gateLoginUsername');
                if (loginUserEl) loginUserEl.value = username;

                enterStudio(data.user);
            } catch (err) {
                showToast(`Sign In Error: ${err.message}`, false);
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('gateRegUsername').value.trim();
            const full_name = document.getElementById('gateRegFullName').value.trim();
            const email = document.getElementById('gateRegEmail').value.trim();
            const password = document.getElementById('gateRegPassword').value;

            try {
                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, full_name, email, password })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || 'Registration failed');

                currentAuthToken = data.token;
                localStorage.setItem('doculens_jwt', data.token);

                const loginUserEl = document.getElementById('gateLoginUsername');
                if (loginUserEl) loginUserEl.value = username;

                enterStudio(data.user);
            } catch (err) {
                showToast(`Sign Up Error: ${err.message}`, false);
            }
        });
    }

    // ================= 4. DEMO FAST LOGIN BUTTONS =================
    const demoBtns = document.querySelectorAll('.demo-login-btn');
    demoBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const user = btn.getAttribute('data-user');
            if (user) switchDemoUser(user);
        });
    });

    // ================= 5. STUDIO NAVBAR CONTROLS =================
    const signOutBtn = document.getElementById('signOutBtn');
    if (signOutBtn) {
        signOutBtn.addEventListener('click', exitStudio);
    }

    // ================= 6. STUDIO CORE ACTIONS =================
    const askBtn = document.getElementById('askCopilotBtn');
    if (askBtn) askBtn.addEventListener('click', executeAudit);

    const queryInput = document.getElementById('mainQueryInput');
    if (queryInput) {
        queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                executeAudit();
            }
        });
    }

    const chips = document.querySelectorAll('.chip-btn');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            if (query && queryInput) {
                queryInput.value = query;
                executeAudit();
            }
        });
    });

    const fileInput = document.getElementById('fileUploadInput');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    const closeBtn = document.getElementById('closeDrawerBtn');
    const backdrop = document.getElementById('drawerBackdrop');
    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (backdrop) backdrop.addEventListener('click', closeDrawer);

    document.addEventListener('click', (e) => {
        const citationEl = e.target.closest('.inline-citation, .citation-pill');
        if (citationEl) {
            const doc = citationEl.getAttribute('data-doc');
            const page = parseInt(citationEl.getAttribute('data-page'), 10) || 1;
            if (doc) openDrawer(doc, page);
        }
    });

    const tabCopilot = document.getElementById('tabBtnCopilot');
    const tabBenchmark = document.getElementById('tabBtnBenchmark');
    const quickBenchBtn = document.getElementById('quickBenchmarkBtn');
    const reRunBenchBtn = document.getElementById('reRunBenchmarkBtn');

    if (tabCopilot) tabCopilot.addEventListener('click', () => switchTab('copilot'));
    if (tabBenchmark) tabBenchmark.addEventListener('click', () => switchTab('benchmark'));
    if (quickBenchBtn) quickBenchBtn.addEventListener('click', () => {
        switchTab('benchmark');
        loadBenchmarkData(true);
    });
    if (reRunBenchBtn) reRunBenchBtn.addEventListener('click', () => loadBenchmarkData(true));

    // ================= 7. LOCAL AI MODEL BRIDGE & MODAL CONTROLS =================
    const localModal = document.getElementById('localModelModal');
    const btnLocalModal = document.getElementById('btnLocalModelModal');
    const closeLocalModal = document.getElementById('closeLocalModelModal');
    const dismissLocalModal = document.getElementById('btnDismissLocalModal');
    const btnDetectOllama = document.getElementById('btnDetectLocalOllama');

    if (btnLocalModal && localModal) {
        btnLocalModal.addEventListener('click', () => {
            localModal.classList.remove('hidden');
            if (localStorage.getItem('doculens_use_local_ollama') === 'true') {
                detectLocalOllama(false);
            }
        });
    }

    if (closeLocalModal && localModal) {
        closeLocalModal.addEventListener('click', () => localModal.classList.add('hidden'));
    }
    if (dismissLocalModal && localModal) {
        dismissLocalModal.addEventListener('click', () => localModal.classList.add('hidden'));
    }
    if (btnDetectOllama) {
        btnDetectOllama.addEventListener('click', () => detectLocalOllama(true));
    }

    // Auto-detect on page load if previously connected
    if (localStorage.getItem('doculens_use_local_ollama') === 'true') {
        detectLocalOllama(false);
    }
});

// Detect Local Ollama via Backend API or Client Browser
async function detectLocalOllama(showNotification = true) {
    const statusBox = document.getElementById("localOllamaStatusBox");
    const statusLabel = document.getElementById("localModelStatusLabel");
    const telemetryLLM = document.getElementById("telemetryLLM");

    if (statusBox) {
        statusBox.className = "p-3.5 rounded-xl border border-sky-800 bg-sky-950/60 text-sky-300 text-[11px] font-mono";
        statusBox.innerHTML = "⏳ Probing local Ollama service...";
        statusBox.classList.remove("hidden");
    }

    // 1. Try probing via backend proxy endpoint first (avoids browser Mixed Content blocks)
    try {
        const backendRes = await fetch("/api/local-ollama/status");
        if (backendRes.ok) {
            const bData = await backendRes.json();
            if (bData.active && bData.models && bData.models.length > 0) {
                const activeM = bData.active_model || bData.models[0];
                if (statusBox) {
                    statusBox.className = "p-3.5 rounded-xl border border-emerald-800 bg-emerald-950/80 text-emerald-300 text-[11px] font-mono leading-relaxed";
                    statusBox.innerHTML = `✅ <b>Local Ollama Connected!</b><br>• Active Model: <span class="text-white font-bold">${escapeHtml(activeM)}</span><br>• Installed Models: <span class="text-sky-300">${bData.models.map(escapeHtml).join(', ')}</span><br>• Execution: <b>NVIDIA CUDA GPU / CPU</b><br>• Zero Cloud Cost • Zero API Keys`;
                }
                if (statusLabel) statusLabel.innerText = `🟢 Local: ${activeM}`;
                if (telemetryLLM) telemetryLLM.innerText = `Local ${activeM} (NVIDIA CUDA GPU)`;
                localStorage.setItem("doculens_use_local_ollama", "true");
                localStorage.setItem("doculens_local_model_name", activeM);
                if (showNotification) showToast(`Local AI connected: ${activeM}`, true);
                return true;
            }
        }
    } catch (_) {}

    // 2. Try direct client browser fetch to http://localhost:11434/api/tags
    try {
        const res = await fetch("http://localhost:11434/api/tags", { method: "GET" });
        if (res.ok) {
            const data = await res.json();
            const models = (data.models || []).map(m => m.name);
            const activeModel = models.find(m => m.includes("qwen")) || models[0] || "qwen2.5:1.5b";

            if (statusBox) {
                statusBox.className = "p-3.5 rounded-xl border border-emerald-800 bg-emerald-950/80 text-emerald-300 text-[11px] font-mono leading-relaxed";
                statusBox.innerHTML = `✅ <b>Connected to Local Laptop!</b><br>• Active Model: <span class="text-white font-bold">${escapeHtml(activeModel)}</span><br>• Installed Models: <span class="text-sky-300">${models.map(escapeHtml).join(', ')}</span><br>• Status: 100% Ready for Local GPU/CPU inference!`;
            }

            if (statusLabel) statusLabel.innerText = `🟢 Local: ${activeModel}`;
            if (telemetryLLM) telemetryLLM.innerText = `Local ${activeModel} (Laptop GPU/CPU)`;

            localStorage.setItem("doculens_use_local_ollama", "true");
            localStorage.setItem("doculens_local_model_name", activeModel);
            if (showNotification) showToast(`Local AI connected: ${activeModel}`, true);
            return true;
        }
    } catch (e) {
        // Handle Browser HTTPS Mixed-Content block when on remote cloud
        const isHttpsCloud = window.location.protocol === "https:";
        if (statusBox) {
            statusBox.className = "p-3.5 rounded-xl border border-amber-800 bg-amber-950/90 text-amber-200 text-[11px] font-mono leading-relaxed space-y-1.5";
            if (isHttpsCloud) {
                statusBox.innerHTML = `
                    <div class="font-bold text-amber-400">🔒 Browser Security Notice (Mixed Content)</div>
                    <div>You are viewing the remote cloud link (<b>${escapeHtml(window.location.hostname)}</b>). Chrome blocks secure HTTPS websites from reading private <code class="text-sky-300">http://localhost:11434</code>.</div>
                    <div class="pt-1 text-emerald-300"><b>👉 To use your laptop's GPU & models directly:</b><br>
                    Open your local dashboard: <a href="http://127.0.0.1:8000/static/index.html" target="_blank" class="underline font-bold text-sky-400">http://127.0.0.1:8000/static/index.html</a><br>
                    <i>(Already active and running on your machine with CUDA GPU!)</i></div>
                `;
            } else {
                statusBox.innerHTML = `⚠️ Could not reach http://localhost:11434.<br>1. Download and run <b>setup_local_model.bat</b>.<br>2. Keep the Ollama terminal window open.<br>3. Click Detect again.`;
            }
        }
        localStorage.removeItem("doculens_use_local_ollama");
        return false;
    }
}
