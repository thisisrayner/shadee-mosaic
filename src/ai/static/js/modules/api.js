/**
 * API Module
 * Handles all network requests to the backend.
 */

export const API = {
    /**
     * Fetch aggregated statistics from the backend.
     * @param {boolean} aiOnly - Filter for AI-verified posts.
     * @param {boolean} sgOnly - Filter for Singapore-based posts.
     * @returns {Promise<Object>} The stats object.
     */
    async getStats(aiOnly, sgOnly) {
        const res = await fetch(`/api/stats?ai_only=${aiOnly}&sg_only=${sgOnly}`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        return res.json();
    },

    /**
     * Fetch Google Trends data for the chart.
     * @param {boolean} sgOnly - Filter trends by SG region context.
     * @returns {Promise<Array>} List of trend data points.
     */
    async getTrends(sgOnly) {
        const res = await fetch(`/api/trends?sg_only=${sgOnly}`);
        if (!res.ok) throw new Error('Failed to fetch trends');
        return res.json();
    },

    /**
     * Perform a vector + keyword search on the database.
     * @param {string} query - The user's search query.
     * @param {boolean} aiOnly - Filter for AI-verified posts.
     * @param {boolean} sgOnly - Filter for Singapore-based posts.
     * @param {number} limit - Number of results to return.
     * @param {number} threshold - Similarity threshold.
     * @returns {Promise<Object>} Search results and suggestions.
     */
    async search(query, aiOnly, sgOnly, limit = 12, threshold = 0.3) {
        const res = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                limit,
                threshold,
                ai_only: aiOnly,
                sg_only: sgOnly
            })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Search API Error');
        }
        return res.json();
    },

    /**
     * Initiate the dynamic research loop (SSE).
     * @param {string} query - The research query.
     * @param {boolean} sgOnly - SG filter context.
     * @param {string} sessionId - Unique session ID for traceability.
     * @returns {Promise<Response>} The raw fetch response (for streaming).
     */
    async startResearch(query, sgOnly, sessionId) {
        const response = await fetch('/api/research', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                sg_only: sgOnly,
                session_id: sessionId
            })
        });
        if (!response.ok) throw new Error('Research Protocol Handshake Failed');
        return response; // Return full response for streaming
    },

    /**
     * Ask a follow-up question based on the previous synthesis.
     * @param {string} query - The user's follow-up question.
     * @param {string} context - The previous synthesis text.
     * @param {Array} results - The original search results context.
     * @param {string} sessionId - The current session ID.
     * @returns {Promise<Object>} The AI's answer.
     */
    async followUp(query, context, results, sessionId) {
        const res = await fetch('/api/follow-up', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                context,
                results,
                session_id: sessionId
            })
        });
        if (!res.ok) throw new Error('Follow-up API Error');
        return res.json();
    }
};
