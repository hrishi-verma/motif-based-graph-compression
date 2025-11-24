// Full Cluster Collapse - JavaScript
let graphData = null;
let motifData = null;
let clusterData = null;
let collapsedMotifs = new Set();
let collapsedNodes = new Set();
let motifToCluster = new Map();

let simulation = null;
let svg = d3.select("#graph");
let g = svg.append("g");

// Add zoom
const zoom = d3.zoom()
    .scaleExtent([0.1, 4])
    .on("zoom", (event) => {
        g.attr("transform", event.transform);
    });
svg.call(zoom);

async function loadData() {
    try {
        updateStatus('Loading graph data...', 'blue');
        
        const [graph, msts, clusters] = await Promise.all([
            d3.csv('facebook_weighted_filtered.csv'),
            d3.json('data/facebook_msts.json'),
            d3.json('data/agglomerative_50_cluster_groups.json')
        ]);
        
        // Build graph
        const nodes = new Set();
        const links = [];
        
        graph.forEach(row => {
            const source = parseInt(row.Node1);
            const target = parseInt(row.Node2);
            const weight = parseFloat(row.Weight);
            
            nodes.add(source);
            nodes.add(target);
            links.push({ source, target, weight });
        });
        
        graphData = {
            nodes: Array.from(nodes).map(id => ({ id, type: 'regular' })),
            links: links
        };
        
        motifData = msts;
        clusterData = clusters;
        
        // Build motif to cluster mapping
        Object.keys(clusters).forEach(clusterKey => {
            const cluster = clusters[clusterKey];
            cluster.motifs.forEach(motifId => {
                motifToCluster.set(motifId, clusterKey);
            });
        });
        
        updateStats();
        updateStatus(`Loaded ${graphData.nodes.length} nodes, ${graphData.links.length} edges, ${Object.keys(clusters).length} clusters`, 'green');
        
        drawGraph();
        
        // Auto-collapse all clusters
        setTimeout(() => {
            collapseAllClusters();
        }, 500);
        
    } catch (error) {
        console.error('Error loading data:', error);
        updateStatus('Error loading data: ' + error.message, 'red');
    }
}

function collapseAllClusters() {
    updateStatus('Collapsing all clusters...', 'blue');
    console.log('\n=== COLLAPSING ALL 50 CLUSTERS ===');
    
    collapsedMotifs.clear();
    collapsedNodes.clear();
    
    let totalMotifs = 0;
    let fullyCollapsed = 0;
    let partiallyCollapsed = 0;
    let merged = 0;
    
    // Process each cluster
    Object.keys(clusterData).sort((a, b) => {
        return parseInt(a.split('_')[1]) - parseInt(b.split('_')[1]);
    }).forEach(clusterKey => {
        const cluster = clusterData[clusterKey];
        
        cluster.motifs.forEach((motifId) => {
            totalMotifs++;
            const mst = motifData[motifId.toString()];
            if (!mst) return;
            
            const sourceNode = mst.source_node;
            const motifNodes = new Set(mst.nodes);
            
            const sourceAlreadyCollapsed = collapsedNodes.has(sourceNode);
            
            if (sourceAlreadyCollapsed) {
                let uniqueCount = 0;
                motifNodes.forEach(node => {
                    if (!collapsedNodes.has(node)) {
                        collapsedNodes.add(node);
                        uniqueCount++;
                    }
                });
                merged++;
            } else {
                let sharedCount = 0;
                motifNodes.forEach(node => {
                    if (collapsedNodes.has(node)) {
                        sharedCount++;
                    }
                });
                
                collapsedMotifs.add(motifId);
                motifNodes.forEach(node => collapsedNodes.add(node));
                
                if (sharedCount === 0) {
                    fullyCollapsed++;
                } else {
                    partiallyCollapsed++;
                }
            }
        });
    });
    
    console.log('Total motifs:', totalMotifs);
    console.log('Fully collapsed:', fullyCollapsed);
    console.log('Partially collapsed:', partiallyCollapsed);
    console.log('Merged:', merged);
    console.log('Collapsed structures:', collapsedMotifs.size);
    console.log('Nodes hidden:', collapsedNodes.size);
    
    updateStatus(`Collapsed ${totalMotifs} motifs into ${collapsedMotifs.size} structures (${collapsedNodes.size} nodes hidden)`, 'green');
    updateStats();
    drawGraph();
}

function expandAllClusters() {
    collapsedMotifs.clear();
    collapsedNodes.clear();
    updateStatus('All clusters expanded', 'blue');
    updateStats();
    drawGraph();
}

function resetGraph() {
    expandAllClusters();
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
}

function expandMotif(motifId) {
    collapsedMotifs.delete(motifId);
    const mst = motifData[motifId.toString()];
    
    const nodesToRemove = new Set(mst.nodes);
    nodesToRemove.forEach(node => {
        let inOtherMotif = false;
        for (const otherMotifId of collapsedMotifs) {
            const otherMst = motifData[otherMotifId.toString()];
            if (otherMst && otherMst.nodes.includes(node)) {
                inOtherMotif = true;
                break;
            }
        }
        if (!inOtherMotif) {
            collapsedNodes.delete(node);
        }
    });
    
    updateStatus(`Expanded Motif ${motifId}`, 'blue');
    updateStats();
    drawGraph();
}

function updateStats() {
    if (!graphData) return;
    
    const totalNodes = graphData.nodes.length;
    const hiddenNodes = collapsedNodes.size;
    const visibleNodes = totalNodes - hiddenNodes + collapsedMotifs.size;
    const compressionRatio = ((hiddenNodes / totalNodes) * 100).toFixed(1);
    
    document.getElementById('totalNodes').textContent = totalNodes;
    document.getElementById('visibleNodes').textContent = visibleNodes;
    document.getElementById('collapsedStructures').textContent = collapsedMotifs.size;
    document.getElementById('compressionRatio').textContent = compressionRatio + '%';
}

function updateStatus(message, color) {
    document.getElementById('status').innerHTML = `<span style="color: ${color};">${message}</span>`;
}

function drawGraph() {
    if (!graphData) return;
    
    g.selectAll("*").remove();
    
    const visibleNodes = new Set();
    const nodeData = [];
    
    graphData.nodes.forEach(node => {
        const nodeId = node.id;
        let isCollapsed = false;
        
        for (const motifId of collapsedMotifs) {
            const mst = motifData[motifId.toString()];
            if (mst && mst.nodes.includes(nodeId)) {
                isCollapsed = true;
                if (nodeId === mst.source_node) {
                    visibleNodes.add(nodeId);
                    nodeData.push({
                        id: nodeId,
                        type: 'collapsed',
                        motifId: motifId,
                        motifSize: mst.nodes.length,
                        cluster: motifToCluster.get(motifId)
                    });
                }
                break;
            }
        }
        
        if (!isCollapsed) {
            visibleNodes.add(nodeId);
            nodeData.push({ id: nodeId, type: 'regular' });
        }
    });
    
    // Process links
    const linkData = [];
    const processedLinks = new Set();
    
    graphData.links.forEach(link => {
        let sourceId = link.source.id || link.source;
        let targetId = link.target.id || link.target;
        
        for (const motifId of collapsedMotifs) {
            const mst = motifData[motifId.toString()];
            if (mst) {
                if (mst.nodes.includes(sourceId) && sourceId !== mst.source_node) {
                    sourceId = mst.source_node;
                }
                if (mst.nodes.includes(targetId) && targetId !== mst.source_node) {
                    targetId = mst.source_node;
                }
            }
        }
        
        if (sourceId === targetId) return;
        if (!visibleNodes.has(sourceId) || !visibleNodes.has(targetId)) return;
        
        const linkKey = sourceId < targetId ? `${sourceId}-${targetId}` : `${targetId}-${sourceId}`;
        
        if (!processedLinks.has(linkKey)) {
            processedLinks.add(linkKey);
            linkData.push({ source: sourceId, target: targetId, weight: link.weight });
        }
    });
    
    // Create simulation
    simulation = d3.forceSimulation(nodeData)
        .force('link', d3.forceLink(linkData).id(d => d.id).distance(50))
        .force('charge', d3.forceManyBody().strength(-50))
        .force('center', d3.forceCenter(700, 450))
        .force('collision', d3.forceCollide().radius(d => d.type === 'collapsed' ? 15 : 5));
    
    // Draw links
    const link = g.selectAll('.link')
        .data(linkData)
        .enter().append('line')
        .attr('class', 'link')
        .attr('stroke-width', 0.5);
    
    // Draw nodes
    const node = g.selectAll('.node')
        .data(nodeData)
        .enter().append('circle')
        .attr('class', d => `node ${d.type}`)
        .attr('r', d => d.type === 'collapsed' ? 12 : 3)
        .on('click', (event, d) => {
            if (d.type === 'collapsed') {
                expandMotif(d.motifId);
            }
        })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    node.append('title')
        .text(d => {
            if (d.type === 'collapsed') {
                return `Motif ${d.motifId}\nCluster: ${d.cluster}\n${d.motifSize} nodes\nClick to expand`;
            }
            return `Node ${d.id}`;
        });
    
    // Labels for collapsed nodes
    const label = g.selectAll('.node-label')
        .data(nodeData.filter(d => d.type === 'collapsed'))
        .enter().append('text')
        .attr('class', 'node-label')
        .style('font-size', '10px')
        .style('font-weight', 'bold')
        .text(d => `M${d.motifId}`)
        .attr('dy', 20);
    
    simulation.on('tick', () => {
        link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        label.attr('x', d => d.x).attr('y', d => d.y);
    });
}

function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

// Load data on page load
loadData();
