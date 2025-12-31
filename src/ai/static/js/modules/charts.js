/**
 * Charts Module
 * Handles visualization using Chart.js, specifically the Atmosphere Pulse chart.
 */
import { API } from './api.js';

let trendsChartInstance = null;

// Weekend Highlighter Plugin
// Draws subtle vertical bands for Saturdays and Sundays
const weekendPlugin = {
    id: 'weekendHighlighter',
    beforeDraw: (chart) => {
        const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;
        ctx.save();
        const labels = chart.data.labels;
        if (!labels) return;

        const width = x.width / labels.length;

        labels.forEach((dateStr, index) => {
            const date = new Date(dateStr);
            const day = date.getDay(); // 0 is Sunday, 6 is Saturday

            if (day === 0 || day === 6) {
                const xPos = x.getPixelForValue(index);
                const start = xPos - (width / 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.035)';
                ctx.fillRect(start, top, width, bottom - top);
            }
        });
        ctx.restore();
    }
};

/**
 * Fetch and render the Google Trends chart for the last 180 days.
 * Includes weekend highlighting overlay.
 * @param {boolean} sgOnly - Filter by Singapore region.
 */
export async function updateTrends(sgOnly) {
    const container = document.getElementById('trends-container');
    try {
        const data = await API.getTrends(sgOnly).then(res => res.data);
        if (!data || data.length === 0) {
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        const ctx = document.getElementById('trendsChart').getContext('2d');

        // Group by keyword and date
        const keywords = ["anxiety", "depression", "mental health", "self care", "therapy"];
        const colors = {
            'anxiety': '#6366f1',
            'depression': '#ec4899',
            'mental health': '#10b981',
            'self care': '#f59e0b',
            'therapy': '#8b5cf6'
        };

        // Prepare labels (dates)
        const dates = [...new Set(data.map(d => d.date))].sort();

        const datasets = keywords.map(kw => {
            const kwData = data.filter(d => d.keyword === kw);
            const values = dates.map(date => {
                const entry = kwData.find(d => d.date === date);
                return entry ? entry.score : null;
            });

            return {
                label: kw.charAt(0).toUpperCase() + kw.slice(1),
                data: values,
                borderColor: colors[kw],
                backgroundColor: colors[kw] + '22',
                borderWidth: 2,
                tension: 0.4,
                pointRadius: 0
            };
        });

        if (trendsChartInstance) trendsChartInstance.destroy();

        trendsChartInstance = new Chart(ctx, {
            type: 'line',
            data: { labels: dates, datasets },
            plugins: [weekendPlugin],
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: true, labels: { color: '#94a3b8', boxWidth: 10, font: { size: 10 } } } },
                scales: {
                    x: {
                        display: true,
                        ticks: {
                            color: '#475569',
                            font: { size: 9 },
                            maxRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 6
                        },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { color: '#475569', font: { size: 10 } },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Trends Error:", err);
        container.style.display = 'none';
    }
}
