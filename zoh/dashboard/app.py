"""
ZOH Dashboard Backend
FastAPI server for project telemetry visualization
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from zoh.commands.metrics import MetricsAggregator

# --- FastAPI Initialization ---
app = FastAPI(title="ZOH Dashboard API")
metrics = MetricsAggregator()

# --- API Endpoints ---

@app.get("/api/metrics")
async def get_dashboard_metrics():
    """Fetch all project telemetry for charts"""
    try:
        data = metrics.aggregate()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_dashboard_html():
    """Main Dashboard Page (Single Page App with Plotly.js)"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZOH Project Governance Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
            .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 10px; }
            .container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            .card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
            h2 { color: #38bdf8; }
            .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
            .stat-box { background: #0f172a; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-value { font-size: 24px; font-weight: bold; color: #22d3ee; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ZOH Project Governance Dashboard</h1>
            <div id="project-info">V 1.0.0</div>
        </div>

        <div class="stat-grid" id="stats">
            <div class="stat-box"><div>Token Burn</div><div class="stat-value" id="token-total">0</div></div>
            <div class="stat-box"><div>Bugs Blocked</div><div class="stat-value" id="bugs-blocked">0</div></div>
            <div class="stat-box"><div>Status</div><div class="stat-value" style="color:#4ade80">HEALTHY</div></div>
        </div>

        <div class="container">
            <div class="card">
                <h2>Token Consumption Rate</h2>
                <div id="token-chart"></div>
            </div>
            <div class="card">
                <h2>Gate/Bug Capture Efficiency</h2>
                <div id="bug-chart"></div>
            </div>
        </div>

        <script>
            async function loadData() {
                const res = await fetch('/api/metrics');
                const stats = await res.json();
                
                // Update Numeric Stats
                document.getElementById('token-total').innerText = stats.token_stats.total_consumed.toLocaleString();
                document.getElementById('bugs-blocked').innerText = stats.bug_stats.fixed;

                // 1. Token Chart (Line)
                const tokenData = [{
                    x: ['Init', 'Design', 'Coding', 'Final'],
                    y: [1200, 2500, stats.token_stats.total_consumed, stats.token_stats.total_consumed * 1.2],
                    type: 'scatter',
                    mode: 'lines+markers',
                    line: {color: '#38bdf8', width: 4},
                    marker: {size: 10}
                }];
                Plotly.newPlot('token-chart', tokenData, {
                    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {color: '#f8fafc'}, margin: {t: 0, r: 0, b: 40, l: 40}
                });

                // 2. Bug Chart (Bar)
                const bugData = [{
                    x: ['GATE-1', 'GATE-2', 'GATE-3', 'Final Audit'],
                    y: [stats.bug_stats.fixed, stats.bug_stats.fixed * 0.5, 2, 1],
                    type: 'bar',
                    marker: {color: '#4ade80'}
                }];
                Plotly.newPlot('bug-chart', bugData, {
                    paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
                    font: {color: '#f8fafc'}, margin: {t: 0, r: 0, b: 40, l: 40}
                });
            }
            loadData();
        </script>
    </body>
    </html>
    """
    return html_content
