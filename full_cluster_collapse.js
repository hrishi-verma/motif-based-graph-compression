// Full Cluster Collapse - JavaScript
// New compression logic with independent motif collapse.
// See COMPRESSION_LOGIC_SPEC.md for full documentation.
let graphData = null;
let motifData = null;
let clusterData = null;
let collapsedMotifs = new Set();
let motifOwnership = new Map();  // nodeId -> motifId (which motif owns each node)
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
    console.log('\n=== COLLAPSING ALL 50 CLUSTERS (New Independent Logic) ===');
    
    collapsedMotifs.clear();
    motifOwnership.clear();
    
    let totalMotifs = 0;
    let extractedSources = 0;
    let claimedNodes = 0;
    let skippedNodes = 0;
    
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
            
            // ============================================
            // STEP 1: Handle source node extraction
            // ============================================
            if (motifOwnership.has(sourceNode)) {
                const previousOwner = motifOwnership.get(sourceNode);
                // Extract: remove ownership from previous motif
                motifOwnership.delete(sourceNode);
                extractedSources++;
                console.log(`  Extracted source ${sourceNode} from Motif ${previousOwner}`);
            }
            
            // ============================================
            // STEP 2: Claim nodes for this motif
            // ============================================
            collapsedMotifs.add(motifId);
            
            motifNodes.forEach(node => {
                if (node === sourceNode) {
                    // Source node: this motif owns it
                    motifOwnership.set(node, motifId);
                    claimedNodes++;
                } else {
                    // Non-source node: only claim if not already owned
                    if (!motifOwnership.has(node)) {
                        motifOwnership.set(node, motifId);
                        claimedNodes++;
                    } else {
                        // Already owned by another motif - leave it there
                        skippedNodes++;
                    }
                }
            });
        });
    });
    
    console.log('Total motifs:', totalMotifs);
    console.log('Collapsed structures:', collapsedMotifs.size);
    console.log('Extracted sources:', extractedSources);
    console.log('Claimed nodes:', claimedNodes);
    console.log('Skipped nodes (already owned):', skippedNodes);
    console.log('Total owned nodes:', motifOwnership.size);
    
    updateStatus(`Collapsed ${totalMotifs} motifs into ${collapsedMotifs.size} structures (${motifOwnership.size} nodes owned)`, 'green');
    updateStats();
    drawGraph();
}

function expandAllClusters() {
    collapsedMotifs.clear();
    motifOwnership.clear();
    updateStatus('All clusters expanded', 'blue');
    updateStats();
    drawGraph();
}

function resetGraph() {
    expandAllClusters();
    svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity);
}

function expandMotif(motifId) {
    // Remove from collapsed set
    collapsedMotifs.delete(motifId);
    
    // Release nodes that this motif owns
    const mst = motifData[motifId.toString()];
    if (mst) {
        let releasedCount = 0;
        mst.nodes.forEach(node => {
            if (motifOwnership.get(node) === motifId) {
                motifOwnership.delete(node);
                releasedCount++;
            }
        });
        console.log(`Expanded Motif ${motifId}: released ${releasedCount} nodes`);
    }
    
    updateStatus(`Expanded Motif ${motifId}`, 'blue');
    updateStats();
    drawGraph();
}

function updateStats() {
    if (!graphData) return;
    
    const totalNodes = graphData.nodes.length;
    const ownedNodes = motifOwnership.size;
    const sourceNodes = collapsedMotifs.size;  // Each collapsed motif has 1 visible source
    const hiddenNodes = ownedNodes - sourceNodes;
    const visibleNodes = totalNodes - hiddenNodes;
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
        
        if (motifOwnership.has(nodeId)) {
            // Node is owned by a collapsed motif
            const ownerMotifId = motifOwnership.get(nodeId);
            const ownerMst = motifData[ownerMotifId.toString()];
            
            if (nodeId === ownerMst.source_node) {
                // This is a source node - show it as collapsed representative
                visibleNodes.add(nodeId);
                nodeData.push({
                    id: nodeId,
                    type: 'collapsed',
                    motifId: ownerMotifId,
                    motifSize: ownerMst.nodes.length,
                    cluster: motifToCluster.get(ownerMotifId)
                });
            }
            // Non-source owned nodes are hidden (not added to visibleNodes or nodeData)
        } else {
            // Node is not owned by any motif - show as regular
            visibleNodes.add(nodeId);
            nodeData.push({ id: nodeId, type: 'regular' });
        }
    });
    
    // Process links - redirect edges from hidden nodes to their owner's source node
    const linkData = [];
    const processedLinks = new Set();
    
    graphData.links.forEach(link => {
        let sourceId = link.source.id || link.source;
        let targetId = link.target.id || link.target;
        
        // Redirect source if owned by a motif
        if (motifOwnership.has(sourceId)) {
            const ownerMotifId = motifOwnership.get(sourceId);
            const ownerMst = motifData[ownerMotifId.toString()];
            if (sourceId !== ownerMst.source_node) {
                sourceId = ownerMst.source_node;
            }
        }
        
        // Redirect target if owned by a motif
        if (motifOwnership.has(targetId)) {
            const ownerMotifId = motifOwnership.get(targetId);
            const ownerMst = motifData[ownerMotifId.toString()];
            if (targetId !== ownerMst.source_node) {
                targetId = ownerMst.source_node;
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
