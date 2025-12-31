/**
 * Main Application Module
 * Entry point for the Shadee Mosaic frontend.
 * Orchestrates module interactions, manages global state, and handles event listeners.
 * 
 * Modules:
 * - API: Backend communication.
 * - UI: DOM manipulation and modals.
 * - Charts: Data visualization.
 * - Research: Core logic for the AI research engine.
 */
import { API } from './api.js';
import * as UI from './ui.js';
import { updateTrends } from './charts.js';
import * as Research from './research.js';

// Application State
let currentResults = [];
let currentSessionId = "";

// DOM Elements
const queryInput = document.getElementById('queryInput');
const resultsContainer = document.getElementById('results');
const loader = document.getElementById('loader');
const resultsArea = document.getElementById('results-area');
const initialState = document.getElementById('initial-state');
const synthesisText = document.getElementById('synthesis-text');
const aiOnlyToggle = document.getElementById('aiOnlyToggle');
const toggleLabel = document.getElementById('toggleLabel');
const sgOnlyToggle = document.getElementById('sgOnlyToggle');
const sgToggleLabel = document.getElementById('sgToggleLabel');
const followUpInput = document.getElementById('followUpInput');

/**
 * Main Search Handler
 */
async function handleSearch() {
    const query = queryInput.value.trim();
    if (!query) return;

    // Reset UI
    initialState.style.display = 'none';
    resultsArea.style.display = 'none';
    loader.style.display = 'block';
    resultsContainer.innerHTML = '';
    synthesisText.innerHTML = 'Generating insights...';
    document.getElementById('follow-up-ui').style.display = 'none';

    // Generate unique session ID for this research cycle
    currentSessionId = crypto.randomUUID ? crypto.randomUUID() : Date.now().toString();

    UI.switchTab('synthesis');

    try {
        // 0. Fetch Stats (Parallel with Search)
        const statsPromise = API.getStats(aiOnlyToggle.checked, sgOnlyToggle.checked)
            .catch(() => ({ total_posts: 0 }));

        // 1. Fetch Search Results
        const searchPromise = API.search(query, aiOnlyToggle.checked, sgOnlyToggle.checked);

        const [stats, searchResponse] = await Promise.all([statsPromise, searchPromise]);

        const results = searchResponse.results;
        const suggestion = searchResponse.suggestion;

        // Handle Suggestion Bridge
        const suggestionBox = document.getElementById('suggestion-bridge');
        if (suggestion && results.length < 5) {
            if (!suggestionBox) {
                resultsContainer.insertAdjacentHTML('beforebegin', `
<div id="suggestion-bridge" style="
                        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
                        border: 1px solid rgba(99, 102, 241, 0.3);
                        padding: 1.25rem;
                        border-radius: 1rem;
                        margin-bottom: 2rem;
                        color: #e2e8f0;
                        font-size: 0.95rem;
                        display: flex;
                        align-items: flex-start;
                        gap: 1rem;">
<div
    style="background: #6366f1; width: 2.5rem; height: 2.5rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
    <span style="font-size: 1.2rem;">💡</span>
</div>
<div>
    <div style="font-weight: 600; color: #a5b4fc; margin-bottom: 0.25rem;">Intelligence Suggestion</div>
    <div id="suggestion-text"></div>
</div>
</div>
`);
            }
            document.getElementById('suggestion-text').textContent = suggestion;
            document.getElementById('suggestion-bridge').style.display = 'flex';
        } else if (suggestionBox) {
            suggestionBox.style.display = 'none';
        }

        // Inject stats into Evidence Tab
        let bannerCont = document.getElementById('stats-banner-container');
        let statsCont = document.getElementById('stats-banner');
        if (!statsCont) {
            statsCont = document.createElement('div');
            statsCont.id = 'stats-banner';
            statsCont.className = 'stats-banner';
            statsCont.style.cssText = `
background: rgba(99, 102, 241, 0.1);
border: 1px solid rgba(99, 102, 241, 0.2);
padding: 1rem;
border-radius: 1rem;
margin-bottom: 2rem;
text-align: center;
color: #94a3b8;
font-size: 0.9rem;
`;
            bannerCont.appendChild(statsCont);
        }

        const totalCount = stats.total_posts !== undefined ? stats.total_posts.toLocaleString() : "0";
        statsCont.innerHTML = `Following results queried from <strong style="color: #6366f1;">${totalCount}</strong> datapoints.`;

        currentResults = results;

        if (results.length === 0) {
            loader.style.display = 'none';
            resultsArea.style.display = 'block';
            synthesisText.innerHTML = 'No matching narratives found to synthesize.';
            resultsContainer.innerHTML = '<div class="empty-state">No matching results in current database.</div>';
            return;
        }

        UI.renderResults(results, resultsContainer);
        resultsArea.style.display = 'block';
        loader.style.display = 'none';

        // 2. Start Dynamic Research Flow
        Research.conductResearch(query, sgOnlyToggle.checked, currentSessionId);

    } catch (error) {
        console.error("Critical Error:", error);
        loader.style.display = 'none';
        initialState.innerHTML = `<div style="color: #ef4444;">Error: ${error.message}</div>`;
        initialState.style.display = 'block';
    }
}

/**
 * Initialize Event Listeners
 */
function init() {
    // Search Interactions
    document.querySelector('.search-btn').addEventListener('click', handleSearch);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    // Toggle Labels
    aiOnlyToggle.addEventListener('change', () => {
        toggleLabel.textContent = aiOnlyToggle.checked ? "Verified posts only" : "Include all posts";
    });
    sgOnlyToggle.addEventListener('change', () => {
        sgToggleLabel.textContent = sgOnlyToggle.checked ? "SG Posts only" : "Whole DB";
        updateTrends(sgOnlyToggle.checked);
    });

    // Set initial labels
    toggleLabel.textContent = aiOnlyToggle.checked ? "Verified posts only" : "Include all posts";
    sgToggleLabel.textContent = sgOnlyToggle.checked ? "SG Posts only" : "Whole DB";

    // Follow-Up Interactions
    document.querySelector('#follow-up-ui button').addEventListener('click', () => {
        Research.handleFollowUp(currentResults, currentSessionId);
    });
    followUpInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') Research.handleFollowUp(currentResults, currentSessionId);
    });

    // Tab Switching
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabId = e.currentTarget.dataset.tab;
            if (tabId) UI.switchTab(tabId);
        });
    });

    // Modal Interactions
    document.querySelector('.close-btn').addEventListener('click', UI.closeModal);

    // Global Escape key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') UI.closeModal();
    });

    // Click outside modal to close
    document.getElementById('detailModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('detailModal')) {
            UI.closeModal();
        }
    });

    // Charts Initialization
    updateTrends(sgOnlyToggle.checked);
}

// Run initialization
init();
