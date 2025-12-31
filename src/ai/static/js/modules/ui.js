/**
 * UI Module
 * Handles DOM manipulation, rendering, and modal interactions.
 */

/**
 * Switch the active tab in the results area.
 * @param {string} tab - The content ID of the tab ('synthesis', 'evidence', 'protocol').
 */
export function switchTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    if (tab === 'synthesis') {
        document.querySelector('.tab:nth-child(1)').classList.add('active');
        document.getElementById('synthesis-tab').classList.add('active');
    } else if (tab === 'evidence') {
        document.querySelector('.tab:nth-child(2)').classList.add('active');
        document.getElementById('evidence-tab').classList.add('active');
    } else if (tab === 'protocol') {
        document.querySelector('.tab:nth-child(3)').classList.add('active');
        document.getElementById('protocol-tab').classList.add('active');
    }
}

/**
 * Open the details modal for a specific result item.
 * @param {Object} item - The data object for the selected post.
 */
export function openModal(item) {
    if (!item) return;

    const modal = document.getElementById('detailModal');
    const isAi = !!item.ai_explanation;

    document.getElementById('modalPlatform').textContent = item.platform;
    document.getElementById('modalHeaderTitle').textContent = `Narrative ${item.id.substring(0, 8)}`;
    document.getElementById('modalContentScrubbed').textContent = item.content_scrubbed || "";
    document.getElementById('modalContentOriginal').textContent = item.content || "";
    document.getElementById('metaDate').textContent = item.post_dt ? new Date(item.post_dt).toLocaleDateString() : 'Unknown';
    document.getElementById('metaTier').textContent = isAi ? 'LLM Tier 2 (Optimized)' : 'Regex Tier 1 (Baseline)';
    document.getElementById('metaSimilarity').textContent = `${(item.similarity * 100).toFixed(1)}%`;
    document.getElementById('metaAiExplanation').textContent = item.ai_explanation || 'No detailed AI analysis available for this record yet.';

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Close the details modal.
 */
export function closeModal() {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Render search results into grid cards.
 * @param {Array} data - List of result objects.
 * @param {HTMLElement} container - DOM element to render cards into.
 */
export function renderResults(data, container) {
    container.innerHTML = '';
    data.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${index * 0.05}s`;

        // Pass the item object directly to openModal
        card.onclick = () => openModal(item);

        const isAi = !!item.ai_explanation;
        const score = (item.similarity * 100).toFixed(1);

        // Qualitative Label Mapping
        let relevanceLabel = "Potential Link";
        if (item.similarity >= 0.70) relevanceLabel = "Top Match";
        else if (item.similarity >= 0.55) relevanceLabel = "Highly Relevant";
        else if (item.similarity >= 0.45) relevanceLabel = "Relevant";

        card.innerHTML = `
            <div class="card-header">
                <span class="platform-tag">${item.platform}</span>
                <div style="display:flex; gap: 0.5rem; align-items:center;">
                    <span class="tier-pill ${isAi ? 'tier-llm' : 'tier-regex'}">${isAi ? 'LLM Tier 2' : 'Regex Tier 1'}</span>
                    <span class="similarity-badge">
                        ${relevanceLabel}
                        <span class="tooltiptext">Match Score: ${score}%</span>
                    </span>
                </div>
            </div>
            <div class="content-body">
                ${item.content_scrubbed ? item.content_scrubbed.substring(0, 180) + '...' : '[No Content]'}
            </div>
        `;
        container.appendChild(card);
    });
}

/**
 * Parse simple markdown-like syntax for the AI synthesis (fallback if marked.js isn't used).
 * Note: research.js uses window.marked, this is a lightweight helper for other text.
 * @param {string} text - Raw text with **bold** or bullets.
 * @param {HTMLElement} container - Element to inject HTML into.
 */
export function formatSynthesis(text, container) {
    // Split by lines and handle bolding/bullets
    const lines = text.split('\n');
    let html = '';
    let inList = false;

    lines.forEach(line => {
        let cleanLine = line.trim();
        if (!cleanLine) {
            if (inList) { html += '</ul>'; inList = false; }
            html += '<br>';
            return;
        }

        // Handle Bold
        cleanLine = cleanLine.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Handle Bullet Points
        if (cleanLine.startsWith('- ') || cleanLine.startsWith('* ') || /^\d+\.\s/.test(cleanLine)) {
            if (!inList) { html += '<ul style="margin-left: 1.5rem; margin-bottom: 1rem; list-style-type: disc;">'; inList = true; }
            const itemContent = cleanLine.replace(/^[-*]\s/, '').replace(/^\d+\.\s/, '');
            html += `<li style="margin-bottom: 0.5rem;">${itemContent}</li>`;
        } else {
            if (inList) { html += '</ul>'; inList = false; }
            html += `<p style="margin-bottom: 1rem;">${cleanLine}</p>`;
        }
    });

    if (inList) html += '</ul>';
    container.innerHTML = html;
}
