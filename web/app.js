/* =============================================================================
   💘 CUPID AGENT — FRONTEND APPLICATION LOGIC
   Manages tab navigation, API calls, live ReAct trace visualizer rendering,
   Mermaid diagram rendering, and test suite execution.
   ============================================================================= */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadProviderInfo();
    loadTestCases();
    loadCupidData();
    loadFlowchart();
    loadTraceEvalReport();
    setupEventListeners();
});

// 1. Tab Switching
function initTabs() {
    const tabs = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => {
                t.classList.remove("active");
                t.setAttribute("aria-selected", "false");
            });
            contents.forEach(c => c.classList.remove("active"));

            tab.classList.add("active");
            tab.setAttribute("aria-selected", "true");

            const targetId = tab.getAttribute("data-tab");
            document.getElementById(targetId).classList.add("active");
        });
    });
}

// 2. Fetch Provider Info
async function loadProviderInfo() {
    try {
        const res = await fetch("/api/provider-info");
        const info = await res.json();
        const el = document.getElementById("providerName");
        if (info.provider_env === "mock") {
            el.innerHTML = `Provider: <strong>Mock Engine</strong> (Offline Mode)`;
        } else {
            el.innerHTML = `Provider: <strong>${info.provider_env.toUpperCase()}</strong> (${info.model_name})`;
        }
    } catch (e) {
        console.error("Lỗi lấy thông tin provider:", e);
    }
}

// 3. Fetch Test Cases & Render Presets + Suite Cards
async function loadTestCases() {
    try {
        const res = await fetch("/api/test-cases");
        const testCases = await res.json();
        
        renderPresetPills(testCases);
        renderTestCasesSuite(testCases);
    } catch (e) {
        console.error("Lỗi tải Test Cases:", e);
    }
}

function renderPresetPills(testCases) {
    const container = document.getElementById("presetPills");
    container.innerHTML = "";

    testCases.forEach((tc) => {
        const pill = document.createElement("button");
        pill.className = "preset-pill";
        pill.innerHTML = `
            <span>${tc.id} (${tc.category})</span>
        `;
        pill.addEventListener("click", () => {
            document.getElementById("queryInput").value = tc.question;
            runSingleQuery(tc.question);
        });
        container.appendChild(pill);
    });
}

function renderTestCasesSuite(testCases) {
    const container = document.getElementById("testCasesSuite");
    container.innerHTML = "";

    testCases.forEach((tc) => {
        const card = document.createElement("div");
        card.className = "tc-card";
        
        let badgeClass = "badge-info";
        if (tc.category.includes("Đơn giản")) badgeClass = "badge-success";
        if (tc.category.includes("Single")) badgeClass = "badge-info";
        if (tc.category.includes("Multi")) badgeClass = "badge-warning";
        if (tc.category.includes("Edge")) badgeClass = "badge-danger";

        card.innerHTML = `
            <div class="tc-header">
                <span class="tc-id">${tc.id}</span>
                <span class="badge ${badgeClass}">${tc.category}</span>
            </div>
            <div class="tc-question">💬 "${tc.question}"</div>
            <div class="tc-expectation"><strong>🎯 Kỳ vọng:</strong> ${tc.expected_behavior}</div>
            <button class="btn btn-secondary btn-sm" onclick="runTestCaseFromSuite('${escapeQuotes(tc.question)}')">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                <span>Chạy thử ngay</span>
            </button>
        `;
        container.appendChild(card);
    });
}

function escapeQuotes(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

window.runTestCaseFromSuite = (question) => {
    // Switch to Playground Tab
    document.querySelector('.tab-btn[data-tab="tab-playground"]').click();
    document.getElementById("queryInput").value = question;
    runSingleQuery(question);
};

// 4. Run Single Query API
async function runSingleQuery(query) {
    const baselineBox = document.getElementById("baselineOutput");
    const agentBox = document.getElementById("agentTraceOutput");

    baselineBox.innerHTML = `
        <div class="empty-state">
            <svg class="spin" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>
            <p>Đang truy vấn Chatbot Baseline...</p>
        </div>
    `;

    agentBox.innerHTML = `
        <div class="empty-state">
            <svg class="spin" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></svg>
            <p>Vòng lặp ReAct Agent đang thực thi Thought → Action → Observation...</p>
        </div>
    `;

    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query })
        });
        const data = await res.json();

        // Render Baseline Output
        baselineBox.innerHTML = `
            <div class="final-answer-card" style="background: rgba(255, 255, 255, 0.03); border-color: var(--border-color);">
                <h4>💬 Baseline Response</h4>
                <div class="final-answer-text">${escapeHtml(data.baseline_answer)}</div>
            </div>
        `;

        // Render ReAct Agent Output Trace
        renderAgentTrace(data.react_agent, agentBox);

    } catch (e) {
        baselineBox.innerHTML = `<div class="badge badge-danger">Lỗi: ${e.message}</div>`;
        agentBox.innerHTML = `<div class="badge badge-danger">Lỗi: ${e.message}</div>`;
    }
}

function renderAgentTrace(agentData, container) {
    container.innerHTML = "";

    if (!agentData.steps || agentData.steps.length === 0) {
        container.innerHTML = `<div class="empty-state"><p>Không có bước thực thi nào.</p></div>`;
        return;
    }

    agentData.steps.forEach((st) => {
        const stepCard = document.createElement("div");
        stepCard.className = "step-card";

        if (st.type === "action") {
            const kwargsJson = st.kwargs ? JSON.stringify(st.kwargs) : "";
            stepCard.innerHTML = `
                <div class="step-badge">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
                    Step ${st.step} — ReAct Loop
                </div>
                <div class="step-thought">💡 <strong>Thought:</strong> ${escapeHtml(st.thought)}</div>
                <div class="step-action">🛠️ <strong>Action:</strong> ${st.tool_name}(${escapeHtml(kwargsJson)})</div>
                <div class="step-observation">👁️ <strong>Observation:</strong> ${escapeHtml(st.observation)}</div>
            `;
        } else if (st.type === "final") {
            stepCard.innerHTML = `
                <div class="step-badge" style="color: var(--status-success);">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                    Step ${st.step} — Final Answer Reached
                </div>
                <div class="step-thought">💡 <strong>Thought:</strong> ${escapeHtml(st.thought)}</div>
                <div class="final-answer-card" style="margin-top: 12px;">
                    <h4>🏁 Final Answer</h4>
                    <div class="final-answer-text">${escapeHtml(st.final_answer)}</div>
                </div>
            `;
        } else {
            stepCard.innerHTML = `
                <div class="step-badge" style="color: var(--status-warning);">Step ${st.step}</div>
                <div class="step-thought">💡 ${escapeHtml(st.thought)}</div>
                <div class="step-observation">👁️ ${escapeHtml(st.observation)}</div>
            `;
        }

        container.appendChild(stepCard);
    });

    if (agentData.guardrail_triggered) {
        const warningCard = document.createElement("div");
        warningCard.className = "step-card";
        warningCard.style.borderColor = "var(--status-warning)";
        warningCard.innerHTML = `
            <div class="badge badge-warning">🛡️ Guardrail Triggered (Max Iterations Exceeded)</div>
            <p style="font-size: 13px; margin-top: 8px;">Đã ngắt vòng lặp an toàn để tránh vô hạn loop.</p>
        `;
        container.appendChild(warningCard);
    }
}

// 5. Load Domain Data
async function loadCupidData() {
    try {
        const res = await fetch("/api/cupid-data");
        const data = await res.json();
        const container = document.getElementById("domainDataGrid");
        container.innerHTML = `
            <div class="card" style="padding: 20px;">
                <pre style="font-family: var(--font-mono); font-size: 13px; color: #a78bfa; overflow-x: auto;">${escapeHtml(JSON.stringify(data, null, 2))}</pre>
            </div>
        `;
    } catch (e) {
        console.error("Lỗi tải domain data:", e);
    }
}

// 6. Load Flowchart & Render Mermaid
async function loadFlowchart() {
    try {
        const res = await fetch("/api/flowchart");
        const mermaidText = await res.text();
        const el = document.getElementById("mermaidDiagram");
        el.removeAttribute("data-processed");
        el.innerHTML = mermaidText;
        mermaid.contentLoaded();
    } catch (e) {
        console.error("Lỗi tải flowchart:", e);
    }
}

// 7. Load Trace Eval Markdown Report
async function loadTraceEvalReport() {
    try {
        const res = await fetch("/api/trace-eval");
        const mdText = await res.text();
        const container = document.getElementById("reportContent");
        container.innerHTML = `<pre style="font-family: var(--font-mono); font-size: 13px; white-space: pre-wrap; color: var(--text-primary); padding: 20px;">${escapeHtml(mdText)}</pre>`;
    } catch (e) {
        console.error("Lỗi tải trace eval report:", e);
    }
}

// Helper Utilities
function setupEventListeners() {
    document.getElementById("btnRunQuery").addEventListener("click", () => {
        const q = document.getElementById("queryInput").value.trim();
        if (q) runSingleQuery(q);
    });

    document.getElementById("btnRunAll").addEventListener("click", async () => {
        const res = await fetch("/api/test-cases");
        const testCases = await res.json();
        document.querySelector('.tab-btn[data-tab="tab-testcases"]').click();
    });
}

function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
