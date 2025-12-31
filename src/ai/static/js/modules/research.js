/**
 * Research Module
 * Handles the Dynamic Research Engine flow (SSE), trace logging, and follow-up interaction.
 */
import { API } from './api.js';
import * as UI from './ui.js';

// Internal state to track the latest synthesis for follow-ups
let _currentSynthesis = "";

/**
 * Orchestrate the research protocol via Server-Sent Events (SSE).
 * Handles the N=25 -> Audit -> N=X loop and live trace logs.
 * @param {string} query - The main research topic.
 * @param {boolean} sgOnly - Filter by SG context.
 * @param {string} sessionId - Unique session ID.
 */
export async function conductResearch(query, sgOnly, sessionId) {
    const trace = document.getElementById('research-trace');
    const logs = document.getElementById('trace-logs');
    const synthesisText = document.getElementById('synthesis-text');
    const followUpUI = document.getElementById('follow-up-ui');

    trace.style.display = 'block';
    trace.style.opacity = '1';
    logs.innerHTML = '';
    synthesisText.innerHTML = '<div class="pulse-loader"></div> Initiating research protocol...';
    // Hide follow-up UI until research completes
    followUpUI.style.display = 'none';

    try {
        const response = await API.startResearch(query, sgOnly, sessionId);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep partial line in buffer

            for (const line of lines) {
                const trimmed = line.trim();
                // SSE Standard: lines starting with "data: "
                if (trimmed.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(trimmed.substring(6));
                        handleResearchUpdate(data, logs, synthesisText);
                    } catch (e) {
                        console.error("Research Stream Parse Error", e, trimmed);
                    }
                }
            }
        }
    } catch (err) {
        console.error("Research Error:", err);
        synthesisText.innerHTML = `<span style="color: #ef4444;">Research Protocol Failed: ${err.message}</span>`;
    }
}

/**
 * Internal handler for SSE data events.
 * Updates the protocol log and synthesizes the final output.
 * @param {Object} data - parsed JSON from SSE stream.
 * @param {HTMLElement} logs - trace log container.
 * @param {HTMLElement} synthesisText - synthesis output container.
 */
function handleResearchUpdate(data, logs, synthesisText) {
    const protocolLog = document.getElementById('protocol-log');

    // 1. Regular Phases
    if (data.phase === 'sampling' || data.phase === 'audit' || data.phase === 'synthesis') {
        const entry = document.createElement('div');
        entry.style.borderBottom = "1px solid rgba(255,255,255,0.03)";
        entry.style.padding = "4px 0";
        entry.innerHTML = `> ${data.status} <span style="color: #6366f1;">[N=${data.n || '?'}]</span>`;
        logs.appendChild(entry);
        logs.scrollTop = logs.scrollHeight;

        // Protocol Log Sync
        const pEntry = document.createElement('div');
        pEntry.innerHTML = `<span style="color: #6d6d6d;">[${new Date().toLocaleTimeString()}]</span> <span style="color: #4ade80;">[PHASE]</span> ${data.status || data.phase}`;
        if (protocolLog) protocolLog.appendChild(pEntry);

        // 2. Audit Decisions
    } else if (data.phase === 'audit_result') {
        const entry = document.createElement('div');
        const color = data.decision === 'EXPAND' ? '#f59e0b' : '#10b981';
        entry.style.padding = "4px 0";
        entry.style.color = "#e2e8f0";
        entry.innerHTML = `> AUDIT: <span style="color: ${color}; font-weight: bold;">${data.decision}</span> - ${data.reason}`;
        logs.appendChild(entry);
        logs.scrollTop = logs.scrollHeight;

        // Protocol Detail
        const pEntry = document.createElement('div');
        pEntry.innerHTML = `<span style="color: #6d6d6d;">[${new Date().toLocaleTimeString()}]</span> <span style="color: #6366f1;">[AUDIT_TRACE]</span> Full Audit Model Output:
<pre style="font-size: 0.75rem; color: #cbd5e1; background: #1e1e1e; padding: 10px; margin: 10px 0; border-radius: 5px; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>`;
        if (protocolLog) protocolLog.appendChild(pEntry);

        // 3. Debug Logs
    } else if (data.phase === 'log') {
        const pEntry = document.createElement('div');
        pEntry.innerHTML = `<span style="color: #6d6d6d;">[${new Date().toLocaleTimeString()}]</span> <span style="color: #94a3b8;">[DEBUG]</span> ${data.message} ${data.data ? `
<pre style="font-size: 0.75rem; color: #cbd5e1; background: #1e1e1e; padding: 10px; margin: 10px 0; border-radius: 5px; overflow-x: auto;">${JSON.stringify(data.data, null, 2)}</pre>` : ''}`;
        if (protocolLog) protocolLog.appendChild(pEntry);

        // 4. Completion
    } else if (data.phase === 'complete') {
        // Store synthesis for follow-up
        _currentSynthesis = data.content;

        // Render markdown (assumes marked is global)
        synthesisText.innerHTML = window.marked ? window.marked.parse(data.content) : data.content;

        document.getElementById('follow-up-ui').style.display = 'flex';
        document.getElementById('research-trace').style.opacity = '0.6';

        const pEntry = document.createElement('div');
        pEntry.innerHTML = `<span style="color: #6d6d6d;">[${new Date().toLocaleTimeString()}]</span> <span style="color: #4ade80;">[SUCCESS]</span> Protocol complete with N=${data.n}`;
        if (protocolLog) protocolLog.appendChild(pEntry);

        // 5. Errors within stream
    } else if (data.phase === 'error') {
        synthesisText.innerHTML = `<span style="color: #ef4444;">Error: ${data.content}</span>`;
    }

    if (protocolLog) protocolLog.scrollTop = protocolLog.scrollHeight;
}

/**
 * Submit a follow-up question to the AI, using the current synthesis as context.
 * @param {Array} currentResults - The list of search results used in this session.
 * @param {string} sessionId - The session ID.
 */
export async function handleFollowUp(currentResults, sessionId) {
    const q = document.getElementById('followUpInput').value.trim();
    if (!q) return;

    const originalBtnText = "Ask";
    const btn = document.querySelector('#follow-up-ui button');
    const synthesisText = document.getElementById('synthesis-text');

    if (btn) {
        btn.textContent = "...";
        btn.disabled = true;
    }

    try {
        const data = await API.followUp(q, _currentSynthesis, currentResults, sessionId);

        if (data) {
            const followUpDiv = document.createElement('div');
            followUpDiv.style.marginTop = '2rem';
            followUpDiv.style.paddingTop = '2rem';
            followUpDiv.style.borderTop = '1px solid var(--glass-border)';

            const responseTitle = document.createElement('div');
            responseTitle.style.cssText = "color: var(--accent-color); font-size: 0.7rem; font-weight: 800; margin-bottom: 1rem;";
            responseTitle.textContent = "FOLLOW-UP RESPONSE";
            followUpDiv.appendChild(responseTitle);

            const responseContent = document.createElement('div');
            UI.formatSynthesis(data.answer, responseContent);
            followUpDiv.appendChild(responseContent);

            synthesisText.appendChild(followUpDiv);
            document.getElementById('follow-up-ui').style.display = 'none'; // Only one follow-up per design
        }
    } catch (e) {
        console.error(e);
    } finally {
        if (btn) {
            btn.textContent = originalBtnText;
            btn.disabled = false;
        }
    }
}
