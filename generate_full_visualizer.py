#!/usr/bin/env python3
"""
Generate HTML visualizer with full Wasserstein distance data embedded
"""

import json

def generate_html_with_data():
    """Generate HTML file with embedded Wasserstein distance data"""
    
    # Load the full dataset
    print("Loading Wasserstein distance data...")
    with open('data/wasserstein_distances.json', 'r') as f:
        full_data = json.load(f)
    
    print(f"Loaded {len(full_data)} distance pairs")
    
    # HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wasserstein Distance Visualizer - Full Dataset</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .controls { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .slider-container { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
        .stats { display: flex; gap: 20px; background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .stat-item { text-align: center; }
        .stat-value { font-size: 24px; font-weight: bold; color: #1565c0; }
        .stat-label { font-size: 12px; color: #666; }
        .visualization { display: flex; justify-content: center; }
        .panel { background: #fafafa; padding: 15px; border-radius: 8px; }
        .panel-title { font-weight: bold; margin-bottom: 15px; text-align: center; }
        .histogram-svg { width: 100%; height: 400px; border: 1px solid #ddd; background: white; }
        .loading { text-align: center; padding: 40px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Wasserstein Distance Visualizer - Full Dataset</h1>
        <p>Interactive exploration of all {total_pairs} motif similarity relationships</p>
        
        <div id="loading" class="loading">
            <h3>Processing data...</h3>
            <p>Loading {data_size} distance pairs</p>
        </div>
        
        <div id="mainContent" style="display: none;">
            <div class="controls">
                <div class="slider-container">
                    <label>Distance Threshold:</label>
                    <input type="range" id="distanceSlider" min="0" max="2300" value="100" step="1" style="width: 300px;">
                    <span id="distanceValue">100</span>
                </div>
                <div class="slider-container">
                    <button onclick="resetView()">Reset</button>
                    <span style="margin-left: 20px; color: #666;">
                        Range: 0.5 - 2,272.5 | Use slider to explore different similarity thresholds
                    </span>
                </div>
            </div>

            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="totalPairs">0</div>
                    <div class="stat-label">Total Pairs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="filteredPairs">0</div>
                    <div class="stat-label">Filtered Pairs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="uniqueMotifs">0</div>
                    <div class="stat-label">Unique Motifs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="avgDistance">0</div>
                    <div class="stat-label">Avg Distance</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="minDistance">0</div>
                    <div class="stat-label">Min Distance</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="maxDistance">0</div>
                    <div class="stat-label">Max Distance</div>
                </div>
            </div>

            <div class="visualization">
                <div class="panel" style="width: 100%; max-width: 900px; margin: 0 auto;">
                    <div class="panel-title">Wasserstein Distance Distribution</div>
                    <svg class="histogram-svg" id="histogramSvg"></svg>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Full Wasserstein distance data embedded
        const fullData = {data_json};

        let filteredPairs = [];
        let currentThreshold = 100;

        function init() {{
            console.log("Initializing with", Object.keys(fullData).length, "distance pairs");
            
            // Hide loading and show main content
            document.getElementById('loading').style.display = 'none';
            document.getElementById('mainContent').style.display = 'block';
            
            setupEventListeners();
            updateVisualization();
        }}

        function setupEventListeners() {{
            document.getElementById('distanceSlider').addEventListener('input', function() {{
                currentThreshold = parseInt(this.value);
                document.getElementById('distanceValue').textContent = currentThreshold;
                updateVisualization();
            }});
        }}

        function updateVisualization() {{
            filterPairs();
            updateStats();
            updateHistogram();
        }}

        function filterPairs() {{
            filteredPairs = [];
            
            for (const [key, distance] of Object.entries(fullData)) {{
                if (distance > 0 && distance <= currentThreshold) {{
                    const [motif1, motif2] = key.split('-');
                    // Only keep one direction to avoid duplicates
                    if (parseInt(motif1) < parseInt(motif2)) {{
                        filteredPairs.push({{
                            motif1: motif1,
                            motif2: motif2,
                            distance: distance,
                            key: key
                        }});
                    }}
                }}
            }}
            
            filteredPairs.sort((a, b) => a.distance - b.distance);
        }}

        function updateStats() {{
            const totalPairs = Object.keys(fullData).length / 2;
            const uniqueMotifs = new Set();
            
            filteredPairs.forEach(pair => {{
                uniqueMotifs.add(pair.motif1);
                uniqueMotifs.add(pair.motif2);
            }});

            const distances = filteredPairs.map(p => p.distance);
            const avgDistance = distances.length > 0 ? 
                (distances.reduce((a, b) => a + b, 0) / distances.length).toFixed(1) : 0;
            const minDistance = distances.length > 0 ? Math.min(...distances).toFixed(1) : 0;
            const maxDistance = distances.length > 0 ? Math.max(...distances).toFixed(1) : 0;

            document.getElementById('totalPairs').textContent = totalPairs.toLocaleString();
            document.getElementById('filteredPairs').textContent = filteredPairs.length.toLocaleString();
            document.getElementById('uniqueMotifs').textContent = uniqueMotifs.size;
            document.getElementById('avgDistance').textContent = avgDistance;
            document.getElementById('minDistance').textContent = minDistance;
            document.getElementById('maxDistance').textContent = maxDistance;
        }}

        function updateHistogram() {{
            const svg = d3.select("#histogramSvg");
            svg.selectAll("*").remove();

            if (filteredPairs.length === 0) {{
                svg.append("text")
                    .attr("x", 450).attr("y", 200)
                    .attr("text-anchor", "middle")
                    .style("font-size", "16px").style("fill", "#666")
                    .text("No data within threshold - try increasing the slider value");
                return;
            }}

            const distances = filteredPairs.map(p => p.distance);
            const margin = {{ top: 20, right: 30, bottom: 60, left: 60 }};
            const width = 900 - margin.left - margin.right;
            const height = 400 - margin.bottom - margin.top;

            const x = d3.scaleLinear()
                .domain(d3.extent(distances))
                .range([0, width]);

            // Adaptive bin count based on data size
            const binCount = Math.min(30, Math.max(10, Math.ceil(Math.sqrt(distances.length))));
            
            const bins = d3.histogram()
                .domain(x.domain())
                .thresholds(binCount)(distances);

            const y = d3.scaleLinear()
                .domain([0, d3.max(bins, d => d.length)])
                .range([height, 0]);

            const g = svg.append("g")
                .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

            // Draw bars with hover effects
            g.selectAll("rect")
                .data(bins)
                .enter().append("rect")
                .attr("x", d => x(d.x0))
                .attr("y", d => y(d.length))
                .attr("width", d => Math.max(0, x(d.x1) - x(d.x0) - 1))
                .attr("height", d => y(0) - y(d.length))
                .style("fill", "#2196f3")
                .style("opacity", 0.7)
                .style("stroke", "#1976d2")
                .style("stroke-width", 1)
                .on("mouseover", function(event, d) {{
                    d3.select(this).style("opacity", 0.9);
                    
                    // Add tooltip
                    const tooltip = svg.append("g").attr("id", "tooltip");
                    const rect = tooltip.append("rect")
                        .attr("x", x(d.x0) + margin.left)
                        .attr("y", y(d.length) + margin.top - 30)
                        .attr("width", 120)
                        .attr("height", 25)
                        .style("fill", "rgba(0,0,0,0.8)")
                        .style("rx", 4);
                    
                    tooltip.append("text")
                        .attr("x", x(d.x0) + margin.left + 60)
                        .attr("y", y(d.length) + margin.top - 10)
                        .style("text-anchor", "middle")
                        .style("fill", "white")
                        .style("font-size", "12px")
                        .text(`${{d.x0.toFixed(1)}}-${{d.x1.toFixed(1)}}: ${{d.length}} pairs`);
                }})
                .on("mouseout", function(event, d) {{
                    d3.select(this).style("opacity", 0.7);
                    svg.select("#tooltip").remove();
                }});

            // Add axes
            g.append("g")
                .attr("transform", `translate(0,${{height}})`)
                .call(d3.axisBottom(x))
                .append("text")
                .attr("x", width / 2)
                .attr("y", 40)
                .style("text-anchor", "middle")
                .style("fill", "black")
                .style("font-size", "14px")
                .text("Wasserstein Distance");

            g.append("g")
                .call(d3.axisLeft(y))
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("x", -height / 2)
                .attr("y", -40)
                .style("text-anchor", "middle")
                .style("fill", "black")
                .style("font-size", "14px")
                .text("Number of Motif Pairs");

            // Add grid lines
            g.selectAll(".grid-line-x")
                .data(x.ticks(10))
                .enter().append("line")
                .attr("class", "grid-line-x")
                .attr("x1", d => x(d))
                .attr("x2", d => x(d))
                .attr("y1", 0)
                .attr("y2", height)
                .style("stroke", "#e0e0e0")
                .style("stroke-dasharray", "2,2");

            g.selectAll(".grid-line-y")
                .data(y.ticks(8))
                .enter().append("line")
                .attr("class", "grid-line-y")
                .attr("x1", 0)
                .attr("x2", width)
                .attr("y1", d => y(d))
                .attr("y2", d => y(d))
                .style("stroke", "#e0e0e0")
                .style("stroke-dasharray", "2,2");
        }}

        function resetView() {{
            document.getElementById('distanceSlider').value = 100;
            document.getElementById('distanceValue').textContent = '100';
            currentThreshold = 100;
            updateVisualization();
        }}

        // Initialize when page loads
        setTimeout(init, 100);
    </script>
</body>
</html>'''

    # Calculate statistics
    total_pairs = len(full_data) // 2  # Divide by 2 since we have both directions
    
    # Convert data to JSON string
    data_json = json.dumps(full_data)
    
    # Fill in the template
    html_content = html_template.replace('{data_json}', data_json)
    html_content = html_content.replace('{total_pairs}', str(total_pairs))
    html_content = html_content.replace('{data_size}', str(len(full_data)))
    
    # Write the HTML file
    output_file = 'wasserstein_full_visualizer.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with full dataset")
    print(f"File contains {len(full_data)} distance pairs")
    print(f"Representing {total_pairs} unique motif pairs")
    print(f"File size: ~{len(html_content) / 1024 / 1024:.1f} MB")
    
    return output_file

if __name__ == "__main__":
    generate_html_with_data()