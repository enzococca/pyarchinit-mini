/**
 * Stratigraphic Layout Algorithm - Horizontal Periods Layout
 *
 * New layout strategy:
 * - X-axis: Stratigraphic levels (left = recent, right = old)
 * - Y-axis: Periods (top to bottom)
 * - Areas: Polygonal bounding boxes that can span multiple periods
 */

class StratigraphicLayout {
    constructor(nodes, edges) {
        this.nodes = nodes;
        this.edges = edges;
        this.nodeMap = new Map(nodes.map(n => [n.id, n]));

        // Perform transitive reduction on edges
        this.edges = this.transitiveReduction(edges);
    }

    /**
     * Transitive Reduction - Remove redundant edges
     * If A->B and B->C and A->C exist, remove A->C
     */
    transitiveReduction(edges) {
        // Build adjacency list
        const graph = new Map();
        this.nodes.forEach(node => {
            graph.set(node.id, new Set());
        });

        // Add all edges
        edges.forEach(edge => {
            const rel = edge.stratigraphic_relation || '';
            // Only process hierarchical relationships
            if (rel === 'COVERS' || rel === 'CUTS' || rel === 'FILLS') {
                graph.get(edge.source).add(edge.target);
            } else if (rel === 'COVERED_BY' || rel === 'CUT_BY' || rel === 'FILLED_BY') {
                graph.get(edge.target).add(edge.source);
            }
        });

        // Find transitive edges
        const redundant = new Set();

        graph.forEach((targets, source) => {
            targets.forEach(intermediate => {
                const intermediateTargets = graph.get(intermediate);
                if (intermediateTargets) {
                    intermediateTargets.forEach(target => {
                        if (targets.has(target)) {
                            // Found transitive edge: source -> intermediate -> target
                            // Mark source -> target as redundant
                            redundant.add(`${source}->${target}`);
                        }
                    });
                }
            });
        });

        // Filter out redundant edges
        return edges.filter(edge => {
            const key = `${edge.source}->${edge.target}`;
            const reverseKey = `${edge.target}->${edge.source}`;
            return !redundant.has(key) && !redundant.has(reverseKey);
        });
    }

    /**
     * Calculate stratigraphic levels using topological sort
     * Returns nodes with assigned levels (x-coordinate now!)
     */
    calculateLevels() {
        // Build adjacency list for "covers" relationships
        const graph = new Map();
        const inDegree = new Map();

        // Initialize
        this.nodes.forEach(node => {
            graph.set(node.id, []);
            inDegree.set(node.id, 0);
        });

        // Build graph: if A covers B, then A is above B (A -> B)
        this.edges.forEach(edge => {
            const rel = edge.stratigraphic_relation || '';

            // COVERS means source is ABOVE target (more recent = left)
            if (rel === 'COVERS' || rel === 'CUTS' || rel === 'FILLS') {
                graph.get(edge.source).push(edge.target);
                inDegree.set(edge.target, inDegree.get(edge.target) + 1);
            }
            // COVERED_BY means source is BELOW target (older = right)
            else if (rel === 'COVERED_BY' || rel === 'CUT_BY' || rel === 'FILLED_BY') {
                graph.get(edge.target).push(edge.source);
                inDegree.set(edge.source, inDegree.get(edge.source) + 1);
            }
        });

        // Topological sort using Kahn's algorithm
        const levels = new Map();
        const queue = [];

        // Start with nodes that have no incoming edges (most recent)
        inDegree.forEach((degree, nodeId) => {
            if (degree === 0) {
                queue.push(nodeId);
                levels.set(nodeId, 0);
            }
        });

        let processed = 0;
        while (queue.length > 0) {
            const nodeId = queue.shift();
            const currentLevel = levels.get(nodeId);
            processed++;

            // Process neighbors
            const neighbors = graph.get(nodeId) || [];
            neighbors.forEach(neighborId => {
                const degree = inDegree.get(neighborId) - 1;
                inDegree.set(neighborId, degree);

                // Update level
                const newLevel = currentLevel + 1;
                if (!levels.has(neighborId) || levels.get(neighborId) < newLevel) {
                    levels.set(neighborId, newLevel);
                }

                if (degree === 0) {
                    queue.push(neighborId);
                }
            });
        }

        // Handle nodes not in any relationship (isolated nodes)
        this.nodes.forEach(node => {
            if (!levels.has(node.id)) {
                levels.set(node.id, 0);
            }
        });

        // Assign levels to nodes
        this.nodes.forEach(node => {
            node.level = levels.get(node.id) || 0;
        });

        return {
            maxLevel: Math.max(...Array.from(levels.values())),
            levels: levels
        };
    }

    /**
     * Calculate positions for nodes - Classic Vertical Harris Matrix
     * Top = Recent, Bottom = Old (GraphViz DOT style)
     */
    async calculatePositions(groups, width, height) {
        const { maxLevel } = this.calculateLevels();

        const nodeWidth = 80;
        const nodeHeight = 35;
        const levelHeight = 80;  // Vertical spacing between levels
        const nodeSpacing = 100;  // Horizontal spacing between nodes

        // Try to use GraphViz layout if available
        const hasGraphviz = window['@hpcc-js/wasm'] || window.hpccWasm || window.Graphviz;

        if (hasGraphviz) {
            try {
                await this.calculateGraphvizLayout(width, height);
                return [];
            } catch (error) {
                console.warn('GraphViz layout failed, falling back to manual layout:', error);
            }
        } else {
            console.log('GraphViz WASM not available, using manual layout');
            console.log('Available window properties:', Object.keys(window).filter(k => k.includes('graph') || k.includes('hpcc')));
        }

        // Fallback to manual layout
        return this.calculateSimpleHierarchical(width, height, levelHeight, nodeSpacing);
    }

    /**
     * Generate DOT graph and use GraphViz to calculate layout
     */
    async calculateGraphvizLayout(width, height) {
        // Generate DOT code
        const dot = this.generateDOT();
        console.log('Generated DOT:', dot);

        // Get the GraphViz module (try different global names)
        let GraphvizModule;
        if (window['@hpcc-js/wasm']) {
            GraphvizModule = window['@hpcc-js/wasm'];
        } else if (window.hpccWasm) {
            GraphvizModule = window.hpccWasm;
        } else if (window.Graphviz) {
            GraphvizModule = window.Graphviz;
        } else {
            throw new Error('GraphViz module not found');
        }

        console.log('GraphViz module found:', GraphvizModule);

        // Initialize GraphViz
        const graphviz = await GraphvizModule.Graphviz.load();

        // Layout the graph using DOT algorithm
        const svg = graphviz.layout(dot, "svg", "dot");

        // Parse SVG to extract node positions
        const parser = new DOMParser();
        const svgDoc = parser.parseFromString(svg, "image/svg+xml");

        // Extract positions from SVG
        this.extractPositionsFromSVG(svgDoc, width, height);
    }

    /**
     * Generate GraphViz DOT code from the graph
     */
    generateDOT() {
        let dot = 'digraph HarrisMatrix {\n';
        dot += '  rankdir=TB;\n';  // Top to Bottom
        dot += '  node [shape=box, width=1.1, height=0.5];\n';
        dot += '  nodesep=0.5;\n';
        dot += '  ranksep=0.8;\n\n';

        // Add nodes
        this.nodes.forEach(node => {
            const nodeId = this.escapeDOTId(node.id);
            const label = node.us_number || node.id.split('_').pop();
            dot += `  "${nodeId}" [label="${label}"];\n`;
        });

        dot += '\n';

        // Add edges (only hierarchical relationships)
        this.edges.forEach(edge => {
            const rel = edge.stratigraphic_relation || '';
            const sourceId = this.escapeDOTId(edge.source);
            const targetId = this.escapeDOTId(edge.target);

            // Only add COVERS, CUTS, FILLS (not the inverse relationships)
            if (rel === 'COVERS' || rel === 'CUTS' || rel === 'FILLS') {
                dot += `  "${sourceId}" -> "${targetId}";\n`;
            }
        });

        dot += '}\n';
        return dot;
    }

    /**
     * Escape node ID for DOT format
     */
    escapeDOTId(id) {
        return id.replace(/"/g, '\\"');
    }

    /**
     * Extract node positions from GraphViz SVG output
     */
    extractPositionsFromSVG(svgDoc, width, height) {
        const svgElement = svgDoc.querySelector('svg');
        if (!svgElement) {
            throw new Error('No SVG element found in GraphViz output');
        }

        // Get SVG viewBox to understand coordinate system
        const viewBox = svgElement.getAttribute('viewBox');
        const [vbX, vbY, vbWidth, vbHeight] = viewBox ? viewBox.split(' ').map(Number) : [0, 0, 100, 100];

        console.log('SVG viewBox:', {vbX, vbY, vbWidth, vbHeight});

        // Extract node positions from SVG <g> elements with class "node"
        const nodeElements = svgDoc.querySelectorAll('g.node');
        console.log(`Found ${nodeElements.length} nodes in SVG`);

        // Debug: inspect first node structure
        if (nodeElements.length > 0) {
            const firstNode = nodeElements[0];
            console.log('First node HTML:', firstNode.outerHTML.substring(0, 500));
            console.log('First node children:', Array.from(firstNode.children).map(c => `${c.tagName} ${c.getAttribute('class') || ''}`));

            // Check for common SVG shape elements
            const ellipse = firstNode.querySelector('ellipse');
            const rect = firstNode.querySelector('rect, polygon');
            if (ellipse) {
                console.log('Found ellipse:', {cx: ellipse.getAttribute('cx'), cy: ellipse.getAttribute('cy')});
            }
            if (rect) {
                console.log('Found rect/polygon:', {
                    x: rect.getAttribute('x'),
                    y: rect.getAttribute('y'),
                    points: rect.getAttribute('points')
                });
            }
        }

        let successCount = 0;
        nodeElements.forEach((nodeEl, index) => {
            // Get node ID from title element
            const titleEl = nodeEl.querySelector('title');
            if (!titleEl) {
                if (index < 3) console.warn('No title element found for node', index);
                return;
            }

            const nodeId = titleEl.textContent.trim();
            const node = this.nodeMap.get(nodeId);
            if (!node) {
                if (index < 3) console.warn(`Node not found in map: "${nodeId}"`);
                return;
            }

            // Extract position from text element (center of node)
            const textEl = nodeEl.querySelector('text');
            if (textEl) {
                const svgX = parseFloat(textEl.getAttribute('x'));
                const svgY = parseFloat(textEl.getAttribute('y'));

                if (!isNaN(svgX) && !isNaN(svgY)) {
                    // GraphViz uses negative Y coordinates, convert to positive
                    // Also normalize to viewBox origin
                    node.x = svgX - vbX;
                    node.y = Math.abs(svgY) - vbY;

                    if (index < 5) {
                        console.log(`Node ${nodeId.split('_').pop()}: svgX=${svgX}, svgY=${svgY} -> x=${node.x.toFixed(2)}, y=${node.y.toFixed(2)}`);
                    }
                    successCount++;
                } else {
                    if (index < 3) console.warn(`Invalid coordinates for node ${index}: x=${svgX}, y=${svgY}`);
                }
            } else {
                // Fallback: calculate center from polygon
                const polygon = nodeEl.querySelector('polygon');
                if (polygon) {
                    const points = polygon.getAttribute('points');
                    if (points) {
                        // Parse polygon points: "x1,y1 x2,y2 x3,y3 ..."
                        const coords = points.trim().split(/[\s,]+/).map(Number);
                        if (coords.length >= 4) {
                            // Calculate center (average of x and y coordinates)
                            const xCoords = [];
                            const yCoords = [];
                            for (let i = 0; i < coords.length; i += 2) {
                                xCoords.push(coords[i]);
                                yCoords.push(coords[i + 1]);
                            }
                            const svgX = xCoords.reduce((a, b) => a + b, 0) / xCoords.length;
                            const svgY = yCoords.reduce((a, b) => a + b, 0) / yCoords.length;

                            node.x = svgX - vbX;
                            node.y = Math.abs(svgY) - vbY;

                            if (index < 3) {
                                console.log(`Node ${nodeId.split('_').pop()} (from polygon): x=${node.x.toFixed(2)}, y=${node.y.toFixed(2)}`);
                            }
                            successCount++;
                        }
                    }
                } else {
                    if (index < 3) console.warn('No text or polygon element found for node', index);
                }
            }
        });

        console.log(`Successfully extracted positions for ${successCount}/${nodeElements.length} nodes`);

        // Scale coordinates to fit the viewport
        if (successCount > 0) {
            // Find bounds of the graph
            let minX = Infinity, maxX = -Infinity;
            let minY = Infinity, maxY = -Infinity;

            this.nodes.forEach(node => {
                if (node.x !== undefined && node.y !== undefined) {
                    minX = Math.min(minX, node.x);
                    maxX = Math.max(maxX, node.x);
                    minY = Math.min(minY, node.y);
                    maxY = Math.max(maxY, node.y);
                }
            });

            console.log('Graph bounds:', {minX, maxX, minY, maxY, width: maxX - minX, height: maxY - minY});

            // Scale to fit viewport with margin
            const margin = 50;
            const availableWidth = width - 2 * margin;
            const availableHeight = height - 2 * margin;

            const graphWidth = maxX - minX;
            const graphHeight = maxY - minY;

            // Scale X to fit width, but keep Y at reasonable scale for scrolling
            // Harris Matrix layouts are often very tall, so we don't compress vertically
            const scaleX = graphWidth > 0 ? availableWidth / graphWidth : 1;
            const scaleY = 1.0;  // Keep original vertical spacing (will be scrollable)

            console.log('Scaling:', {scaleX, scaleY, graphWidth, graphHeight});
            console.log('Result will be scrollable - height:', graphHeight * scaleY);

            // Apply scaling and add margin
            this.nodes.forEach(node => {
                if (node.x !== undefined && node.y !== undefined) {
                    // Scale X to fit width, keep Y proportional for readability
                    node.x = (node.x - minX) * scaleX + margin;
                    node.y = (node.y - minY) * scaleY + margin;
                }
            });

            console.log('Scaled sample positions:',
                this.nodes.slice(0, 3).map(n => ({
                    id: n.id.split('_').pop(),
                    x: n.x?.toFixed(2),
                    y: n.y?.toFixed(2)
                }))
            );
        }
    }

    /**
     * Calculate polygonal bounding boxes for Areas
     * Areas can span multiple periods
     */
    calculateAreaPolygons(groups) {
        if (!groups || groups.length === 0) return [];

        // Group nodes by area
        const nodesByArea = new Map();
        this.nodes.forEach(node => {
            const area = node.area || 'Unknown';
            if (!nodesByArea.has(area)) {
                nodesByArea.set(area, []);
            }
            nodesByArea.get(area).push(node);
        });

        const polygons = [];

        // For each area, calculate convex hull
        nodesByArea.forEach((areaNodes, areaName) => {
            if (areaNodes.length === 0) return;

            // Get all node positions
            const points = areaNodes.map(node => ({
                x: node.x,
                y: node.y,
                node: node
            }));

            // Calculate convex hull
            const hull = this.convexHull(points);

            if (hull.length > 0) {
                polygons.push({
                    type: 'area',
                    name: areaName,
                    points: hull,
                    nodes: areaNodes
                });
            }
        });

        return polygons;
    }

    /**
     * Convex Hull Algorithm (Gift Wrapping / Jarvis March)
     * Returns array of points forming the convex hull
     */
    convexHull(points) {
        if (points.length < 3) return points;

        const padding = 40; // Padding around nodes

        // Add padding to points
        const expandedPoints = [];
        points.forEach(p => {
            expandedPoints.push(
                { x: p.x - padding, y: p.y - padding },
                { x: p.x + padding, y: p.y - padding },
                { x: p.x + padding, y: p.y + padding },
                { x: p.x - padding, y: p.y + padding }
            );
        });

        // Find the leftmost point
        let start = expandedPoints[0];
        for (let i = 1; i < expandedPoints.length; i++) {
            if (expandedPoints[i].x < start.x ||
                (expandedPoints[i].x === start.x && expandedPoints[i].y < start.y)) {
                start = expandedPoints[i];
            }
        }

        const hull = [];
        let current = start;

        do {
            hull.push(current);
            let next = expandedPoints[0];

            for (let i = 1; i < expandedPoints.length; i++) {
                if (next === current || this.crossProduct(current, next, expandedPoints[i]) < 0) {
                    next = expandedPoints[i];
                }
            }

            current = next;
        } while (current !== start && hull.length < expandedPoints.length);

        return hull;
    }

    /**
     * Calculate cross product for convex hull
     */
    crossProduct(o, a, b) {
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x);
    }

    /**
     * Simple hierarchical layout - Vertical Harris Matrix (GraphViz DOT style)
     * Y-axis: Stratigraphic depth (top = recent, bottom = old)
     * X-axis: Horizontal distribution following stratigraphic relationships
     */
    calculateSimpleHierarchical(width, height, levelHeight, nodeSpacing) {
        const { maxLevel } = this.calculateLevels();

        // Organize nodes by level (vertical layers)
        const nodesByLevel = new Map();
        this.nodes.forEach(node => {
            const level = node.level || 0;
            if (!nodesByLevel.has(level)) {
                nodesByLevel.set(level, []);
            }
            nodesByLevel.get(level).push(node);
        });

        // Build parent/child relationships based on stratigraphic relations
        const parents = new Map();
        const children = new Map();
        this.nodes.forEach(n => {
            parents.set(n.id, []);
            children.set(n.id, []);
        });
        this.edges.forEach(edge => {
            const rel = edge.stratigraphic_relation || '';
            // Respect the actual stratigraphic relationships
            if (rel === 'COVERS' || rel === 'CUTS' || rel === 'FILLS') {
                children.get(edge.source).push(edge.target);
                parents.get(edge.target).push(edge.source);
            } else if (rel === 'COVERED_BY' || rel === 'CUT_BY' || rel === 'FILLED_BY') {
                children.get(edge.target).push(edge.source);
                parents.get(edge.source).push(edge.target);
            }
        });

        const startY = 100;
        const margin = 50;

        // Initialize X positions using a top-down pass
        // Each level processes nodes based on their parents' positions
        for (let level = 0; level <= maxLevel; level++) {
            const levelNodes = nodesByLevel.get(level) || [];

            // Assign Y coordinate
            levelNodes.forEach(node => {
                node.y = startY + level * levelHeight;
            });

            // Sort nodes to group related ones together
            levelNodes.sort((a, b) => {
                const aParents = parents.get(a.id) || [];
                const bParents = parents.get(b.id) || [];

                // Nodes with parents come after root nodes
                if (aParents.length === 0 && bParents.length > 0) return -1;
                if (aParents.length > 0 && bParents.length === 0) return 1;

                // Both have parents: sort by average parent X (if available)
                if (aParents.length > 0 && bParents.length > 0) {
                    const aParentNodes = aParents.map(id => this.nodeMap.get(id))
                        .filter(p => p && p.x !== undefined);
                    const bParentNodes = bParents.map(id => this.nodeMap.get(id))
                        .filter(p => p && p.x !== undefined);

                    if (aParentNodes.length > 0 && bParentNodes.length > 0) {
                        const aAvgX = aParentNodes.reduce((sum, p) => sum + p.x, 0) / aParentNodes.length;
                        const bAvgX = bParentNodes.reduce((sum, p) => sum + p.x, 0) / bParentNodes.length;
                        return aAvgX - bAvgX;
                    }
                }

                // Fallback to ID comparison
                return a.id.localeCompare(b.id);
            });

            // Assign X coordinates
            const numNodes = levelNodes.length;

            if (numNodes === 1) {
                // Single node: position based on parent median, or centered if no parents
                const node = levelNodes[0];
                const parentIds = parents.get(node.id) || [];

                if (parentIds.length > 0) {
                    const parentNodes = parentIds.map(id => this.nodeMap.get(id))
                        .filter(p => p && p.x !== undefined);

                    if (parentNodes.length > 0) {
                        // Use median of parent positions
                        const parentXs = parentNodes.map(p => p.x).sort((a, b) => a - b);
                        node.x = parentXs[Math.floor(parentXs.length / 2)];
                    } else {
                        node.x = width / 2;
                    }
                } else {
                    // Root node: center it
                    node.x = width / 2;
                }
            } else {
                // Multiple nodes: distribute with spacing, considering parent positions
                // Calculate ideal positions based on parents
                const idealPositions = levelNodes.map(node => {
                    const parentIds = parents.get(node.id) || [];
                    if (parentIds.length > 0) {
                        const parentNodes = parentIds.map(id => this.nodeMap.get(id))
                            .filter(p => p && p.x !== undefined);
                        if (parentNodes.length > 0) {
                            const parentXs = parentNodes.map(p => p.x).sort((a, b) => a - b);
                            return parentXs[Math.floor(parentXs.length / 2)];
                        }
                    }
                    return null;
                });

                // Distribute nodes with spacing
                const totalWidth = (numNodes - 1) * nodeSpacing;
                const startX = margin + (width - 2 * margin - totalWidth) / 2;

                levelNodes.forEach((node, index) => {
                    const idealX = idealPositions[index];
                    if (idealX !== null) {
                        // Use ideal position from parents
                        node.x = idealX;
                    } else {
                        // Use distributed position
                        node.x = startX + index * nodeSpacing;
                    }
                });

                // Resolve collisions while preserving order
                this.resolveCollisions(levelNodes, nodeSpacing);
            }
        }

        // Apply barycentric crossing reduction for multi-node levels
        this.reduceCrossings(nodesByLevel, maxLevel, nodeSpacing, width);

        return [];
    }

    /**
     * Resolve X-coordinate collisions between nodes on the same level
     */
    resolveCollisions(levelNodes, nodeSpacing) {
        if (levelNodes.length <= 1) return;

        // Sort by current X
        levelNodes.sort((a, b) => a.x - b.x);

        // Adjust positions to maintain minimum spacing
        for (let i = 1; i < levelNodes.length; i++) {
            const minX = levelNodes[i - 1].x + nodeSpacing;
            if (levelNodes[i].x < minX) {
                levelNodes[i].x = minX;
            }
        }
    }

    /**
     * Barycentric crossing reduction
     * Reorder nodes within each level to minimize edge crossings
     * Only processes levels with multiple nodes
     */
    reduceCrossings(nodesByLevel, maxLevel, nodeSpacing, width) {
        // Build adjacency information
        const parents = new Map();
        const children = new Map();

        this.nodes.forEach(n => {
            parents.set(n.id, []);
            children.set(n.id, []);
        });

        this.edges.forEach(edge => {
            children.get(edge.source).push(edge.target);
            parents.get(edge.target).push(edge.source);
        });

        // Sweep multiple times
        for (let iter = 0; iter < 2; iter++) {
            // Top-down pass
            for (let level = 0; level <= maxLevel; level++) {
                const levelNodes = nodesByLevel.get(level);
                // Skip levels with 1 or fewer nodes (preserve their parent-aligned position)
                if (!levelNodes || levelNodes.length <= 1) continue;

                // Calculate barycenter for each node based on parents
                levelNodes.forEach(node => {
                    const parentIds = parents.get(node.id);
                    if (parentIds && parentIds.length > 0) {
                        const parentNodes = parentIds.map(id => this.nodeMap.get(id));
                        const validParents = parentNodes.filter(p => p && p.x !== undefined);
                        if (validParents.length > 0) {
                            node.barycenter = validParents.reduce((sum, p) => sum + p.x, 0) / validParents.length;
                        } else {
                            node.barycenter = node.x;
                        }
                    } else {
                        node.barycenter = node.x;
                    }
                });

                // Sort by barycenter
                levelNodes.sort((a, b) => a.barycenter - b.barycenter);

                // Reposition after sorting - distribute evenly
                const margin = 50;
                const totalWidth = (levelNodes.length - 1) * nodeSpacing;
                const startX = margin + (width - 2 * margin - totalWidth) / 2;

                levelNodes.forEach((node, index) => {
                    node.x = startX + index * nodeSpacing;
                });
            }

            // Bottom-up pass
            for (let level = maxLevel; level >= 0; level--) {
                const levelNodes = nodesByLevel.get(level);
                // Skip levels with 1 or fewer nodes
                if (!levelNodes || levelNodes.length <= 1) continue;

                // Calculate barycenter for each node based on children
                levelNodes.forEach(node => {
                    const childIds = children.get(node.id);
                    if (childIds && childIds.length > 0) {
                        const childNodes = childIds.map(id => this.nodeMap.get(id));
                        const validChildren = childNodes.filter(c => c && c.x !== undefined);
                        if (validChildren.length > 0) {
                            node.barycenter = validChildren.reduce((sum, c) => sum + c.x, 0) / validChildren.length;
                        } else {
                            node.barycenter = node.x;
                        }
                    } else {
                        node.barycenter = node.x;
                    }
                });

                // Sort by barycenter
                levelNodes.sort((a, b) => a.barycenter - b.barycenter);

                // Reposition after sorting - distribute evenly
                const margin = 50;
                const totalWidth = (levelNodes.length - 1) * nodeSpacing;
                const startX = margin + (width - 2 * margin - totalWidth) / 2;

                levelNodes.forEach((node, index) => {
                    node.x = startX + index * nodeSpacing;
                });
            }
        }
    }
}

// Export for use in other scripts
window.StratigraphicLayout = StratigraphicLayout;
