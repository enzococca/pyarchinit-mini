/**
 * Harris Matrix Interactive Editor
 *
 * Visual editor using Cytoscape.js for creating and editing Harris Matrix diagrams
 */

// Global state
let cy; // Cytoscape instance
let nodeTypes = [];
let relationshipTypes = [];
let periods = []; // Period data from period_table
let selectedNodeType = 'US';
let selectedRelationshipType = 'Covers';
let editorMode = 'node'; // 'node' or 'edge'
let edgeSourceNode = null; // For edge creation
let nodeIdCounter = 1;
let selectedElement = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeEditor();
});

async function initializeEditor() {
    console.log('Initializing Harris Matrix Editor...');

    // Load node and relationship types
    await loadNodeTypes();
    await loadRelationshipTypes();
    await loadPeriods();

    // Initialize Cytoscape
    initCytoscape();

    // Load existing data if in edit mode
    loadExistingData();

    // Setup event listeners
    setupEventListeners();

    console.log('Editor initialized successfully');
}

/**
 * Load node types from API
 */
async function loadNodeTypes() {
    try {
        const response = await fetch('/harris-creator/api/node-types');
        nodeTypes = await response.json();

        // Populate node type buttons
        const container = document.getElementById('node-type-buttons');
        container.innerHTML = '';

        nodeTypes.forEach(type => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm node-type-btn ' +
                           (type.value === 'US' ? 'btn-primary' : 'btn-outline-secondary');
            btn.setAttribute('data-type', type.value);
            btn.innerHTML = `<span class="legend-color" style="background: ${type.color}; display: inline-block; width: 12px; height: 12px; margin-right: 5px; vertical-align: middle;"></span>${type.value}`;
            btn.title = type.label;

            btn.addEventListener('click', function() {
                // Update selected type
                selectedNodeType = type.value;

                // Update button styles
                document.querySelectorAll('.node-type-btn').forEach(b => {
                    b.classList.remove('btn-primary');
                    b.classList.add('btn-outline-secondary');
                });
                btn.classList.remove('btn-outline-secondary');
                btn.classList.add('btn-primary');
            });

            container.appendChild(btn);
        });

        // Populate property panel select
        const propSelect = document.getElementById('prop-unit-type');
        propSelect.innerHTML = '';
        nodeTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.value;
            option.textContent = type.label;
            propSelect.appendChild(option);
        });

        // Populate legend
        const legend = document.getElementById('node-legend');
        legend.innerHTML = '';
        nodeTypes.slice(0, 6).forEach(type => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `
                <div class="legend-color" style="background: ${type.color};"></div>
                <span>${type.value}</span>
            `;
            legend.appendChild(item);
        });

        console.log('Loaded', nodeTypes.length, 'node types');
    } catch (error) {
        console.error('Error loading node types:', error);
        alert('Failed to load node types');
    }
}

/**
 * Load relationship types from API
 */
async function loadRelationshipTypes() {
    try {
        const response = await fetch('/harris-creator/api/relationship-types');
        relationshipTypes = await response.json();

        // Populate relationship type select
        const select = document.getElementById('relationshipType');
        const propSelect = document.getElementById('prop-relationship-type');

        [select, propSelect].forEach(sel => {
            sel.innerHTML = '';
            relationshipTypes.forEach(type => {
                const option = document.createElement('option');
                option.value = type.value;
                option.textContent = type.label;
                sel.appendChild(option);
            });
        });

        // Set default
        selectedRelationshipType = relationshipTypes[0].value;

        console.log('Loaded', relationshipTypes.length, 'relationship types');
    } catch (error) {
        console.error('Error loading relationship types:', error);
        alert('Failed to load relationship types');
    }
}

/**
 * Load periods and phases from API
 */
async function loadPeriods() {
    try {
        const response = await fetch('/harris-creator/api/periods');
        periods = await response.json();

        // Populate period dropdown
        const periodSelect = document.getElementById('prop-period');
        periodSelect.innerHTML = '<option value="">-- Select Period --</option>';

        periods.forEach(periodData => {
            const option = document.createElement('option');
            option.value = periodData.period;
            option.textContent = periodData.period;
            periodSelect.appendChild(option);
        });

        // Add event listener to populate phases when period changes
        periodSelect.addEventListener('change', function() {
            const selectedPeriod = this.value;
            const phaseSelect = document.getElementById('prop-phase');
            phaseSelect.innerHTML = '<option value="">-- Select Phase --</option>';

            if (selectedPeriod) {
                const periodData = periods.find(p => p.period === selectedPeriod);
                if (periodData && periodData.phases) {
                    periodData.phases.forEach(phase => {
                        const option = document.createElement('option');
                        option.value = phase;
                        option.textContent = phase;
                        phaseSelect.appendChild(option);
                    });
                }
            }
        });

        console.log('Loaded', periods.length, 'periods');
    } catch (error) {
        console.error('Error loading periods:', error);
        alert('Failed to load periods');
    }
}

/**
 * Initialize Cytoscape instance
 */
function initCytoscape() {
    cy = cytoscape({
        container: document.getElementById('cy'),

        style: [
            // Node styles - base style with default shape
            {
                selector: 'node',
                style: {
                    'label': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'background-color': 'data(color)',
                    'border-width': 2,
                    'border-color': '#333',
                    'font-size': '12px',
                    'width': 'label',
                    'height': 'label',
                    'padding': '10px',
                    'shape': 'rectangle'  // Default shape for all nodes
                }
            },
            // Override shape for nodes that have shape data defined
            {
                selector: 'node[shape]',
                style: {
                    'shape': 'data(shape)'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 4,
                    'border-color': '#007bff'
                }
            },
            // Edge styles
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#666',
                    'target-arrow-color': '#666',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '10px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -10
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'line-color': '#007bff',
                    'target-arrow-color': '#007bff',
                    'width': 3
                }
            },
            // Edge styles by type
            {
                selector: 'edge[style="dashed"]',
                style: {
                    'line-style': 'dashed'
                }
            },
            {
                selector: 'edge[style="dotted"]',
                style: {
                    'line-style': 'dotted'
                }
            },
            {
                selector: 'edge[arrow="none"]',
                style: {
                    'target-arrow-shape': 'none'
                }
            }
        ],

        layout: {
            name: 'preset'
        },

        // Interaction options
        minZoom: 0.1,
        maxZoom: 3,
        wheelSensitivity: 0.2
    });

    // Canvas click handler (for adding nodes)
    cy.on('click', function(event) {
        // Only add nodes on background click in node mode
        if (event.target === cy && editorMode === 'node') {
            addNodeAtPosition(event.position);
        }
    });

    // Node click handler (for selection and edge creation)
    cy.on('tap', 'node', function(event) {
        const node = event.target;

        if (editorMode === 'edge') {
            handleEdgeCreation(node);
        } else {
            selectElement(node);
        }
    });

    // Edge click handler (for selection)
    cy.on('tap', 'edge', function(event) {
        const edge = event.target;
        selectElement(edge);
    });

    // Background click deselects
    cy.on('tap', function(event) {
        if (event.target === cy) {
            deselectAll();
        }
    });

    console.log('Cytoscape initialized');
}

/**
 * Add node at position
 */
function addNodeAtPosition(position) {
    const nodeType = nodeTypes.find(t => t.value === selectedNodeType);
    if (!nodeType) return;

    const usNumber = generateUSNumber();
    const nodeId = `node_${nodeIdCounter++}`;

    cy.add({
        group: 'nodes',
        data: {
            id: nodeId,
            label: `${selectedNodeType} ${usNumber}`,
            us_number: usNumber,
            unit_type: selectedNodeType,
            description: '',
            area: '',
            period: '',
            phase: '',
            file_path: '',
            color: nodeType.color,
            shape: nodeType.shape || 'rectangle'
        },
        position: position
    });

    console.log('Added node:', nodeId, 'at position', position);
}

/**
 * Generate unique US number
 */
function generateUSNumber() {
    const existingNumbers = cy.nodes().map(n => parseInt(n.data('us_number')) || 0);
    const maxNumber = Math.max(1000, ...existingNumbers);
    return (maxNumber + 1).toString();
}

/**
 * Handle edge creation in edge mode
 */
function handleEdgeCreation(node) {
    if (!edgeSourceNode) {
        // First click: select source
        edgeSourceNode = node;
        node.style('border-color', '#28a745');
        node.style('border-width', 4);

        showNotification('Source selected. Click target node.', 'info');
    } else {
        // Second click: create edge
        const targetNode = node;

        if (edgeSourceNode.id() === targetNode.id()) {
            showNotification('Cannot connect node to itself', 'warning');
            resetEdgeCreation();
            return;
        }

        // Check if edge already exists
        const existingEdge = cy.edges().filter(e =>
            e.data('source') === edgeSourceNode.id() &&
            e.data('target') === targetNode.id()
        );

        if (existingEdge.length > 0) {
            showNotification('Edge already exists between these nodes', 'warning');
            resetEdgeCreation();
            return;
        }

        // Get relationship type details
        const relType = relationshipTypes.find(r => r.value === selectedRelationshipType);

        // Create edge
        const edgeId = `edge_${Date.now()}`;
        cy.add({
            group: 'edges',
            data: {
                id: edgeId,
                source: edgeSourceNode.id(),
                target: targetNode.id(),
                label: relType.symbol,
                relationship: selectedRelationshipType,
                style: relType.style,
                arrow: relType.arrow
            }
        });

        showNotification('Edge created successfully', 'success');
        resetEdgeCreation();

        console.log('Created edge:', edgeId);
    }
}

/**
 * Reset edge creation state
 */
function resetEdgeCreation() {
    if (edgeSourceNode) {
        edgeSourceNode.style('border-color', '#333');
        edgeSourceNode.style('border-width', 2);
        edgeSourceNode = null;
    }
}

/**
 * Select element and show properties
 */
function selectElement(element) {
    // Deselect previous
    if (selectedElement) {
        selectedElement.unselect();
    }

    // Select new
    element.select();
    selectedElement = element;

    // Show properties panel
    if (element.isNode()) {
        showNodeProperties(element);
    } else if (element.isEdge()) {
        showEdgeProperties(element);
    }
}

/**
 * Deselect all elements
 */
function deselectAll() {
    if (selectedElement) {
        selectedElement.unselect();
        selectedElement = null;
    }

    // Hide properties
    document.getElementById('no-selection').style.display = 'block';
    document.getElementById('node-properties').style.display = 'none';
    document.getElementById('edge-properties').style.display = 'none';
}

/**
 * Show node properties in panel
 */
function showNodeProperties(node) {
    document.getElementById('no-selection').style.display = 'none';
    document.getElementById('node-properties').style.display = 'block';
    document.getElementById('edge-properties').style.display = 'none';

    // Populate fields
    document.getElementById('prop-us-number').value = node.data('us_number') || '';
    document.getElementById('prop-unit-type').value = node.data('unit_type') || 'US';
    document.getElementById('prop-description').value = node.data('description') || '';
    document.getElementById('prop-area').value = node.data('area') || '';
    document.getElementById('prop-period').value = node.data('period') || '';
    document.getElementById('prop-phase').value = node.data('phase') || '';
    document.getElementById('prop-datazione').value = node.data('datazione') || '';
    document.getElementById('prop-file-path').value = node.data('file_path') || '';

    // Show/hide file path field for DOC type
    const isDoc = node.data('unit_type') === 'DOC';
    document.getElementById('file-path-field').style.display = isDoc ? 'block' : 'none';

    // Update visibility based on unit type change
    document.getElementById('prop-unit-type').addEventListener('change', function(e) {
        const isDocType = e.target.value === 'DOC';
        document.getElementById('file-path-field').style.display = isDocType ? 'block' : 'none';
    });
}

/**
 * Show edge properties in panel
 */
function showEdgeProperties(edge) {
    document.getElementById('no-selection').style.display = 'none';
    document.getElementById('node-properties').style.display = 'none';
    document.getElementById('edge-properties').style.display = 'block';

    // Populate fields
    const sourceNode = cy.getElementById(edge.data('source'));
    const targetNode = cy.getElementById(edge.data('target'));

    document.getElementById('prop-from-us').value = sourceNode.data('us_number') || '';
    document.getElementById('prop-to-us').value = targetNode.data('us_number') || '';

    // Use relationshipType (English value) for the select field
    // Fall back to relationship (Italian name) for backward compatibility
    const relValue = edge.data('relationshipType') || edge.data('relationship') || '';
    document.getElementById('prop-relationship-type').value = relValue;
}

/**
 * Load existing data (edit mode)
 */
function loadExistingData() {
    const nodesData = document.getElementById('existing-nodes').value;
    const relsData = document.getElementById('existing-relationships').value;

    if (!nodesData || !relsData) return;

    try {
        const nodes = JSON.parse(nodesData);
        const relationships = JSON.parse(relsData);

        console.log('Loading existing data:', nodes.length, 'nodes,', relationships.length, 'relationships');

        // Add nodes
        nodes.forEach((nodeData, index) => {
            const nodeType = nodeTypes.find(t => t.value === nodeData.unit_type) || nodeTypes[0];

            cy.add({
                group: 'nodes',
                data: {
                    id: nodeData.id,
                    label: `${nodeData.unit_type} ${nodeData.us_number}`,
                    us_number: nodeData.us_number,
                    unit_type: nodeData.unit_type,
                    description: nodeData.description,
                    area: nodeData.area,
                    period: nodeData.period,
                    phase: nodeData.phase,
                    datazione: nodeData.datazione || '',  // datazione_estesa
                    file_path: nodeData.file_path,
                    color: nodeType.color,
                    shape: nodeType.shape || 'rectangle'
                },
                position: {
                    x: 100 + (index % 5) * 150,
                    y: 100 + Math.floor(index / 5) * 100
                }
            });
        });

        // Add edges
        relationships.forEach(relData => {
            // Convert to strings for comparison (database may store as integers)
            const fromUsStr = String(relData.from_us);
            const toUsStr = String(relData.to_us);

            const sourceNode = cy.nodes().filter(n => String(n.data('us_number')) === fromUsStr).first();
            const targetNode = cy.nodes().filter(n => String(n.data('us_number')) === toUsStr).first();

            if (sourceNode.length && targetNode.length) {
                // Bilingual matching: support both Italian (symbol) and English (value) names
                const relType = relationshipTypes.find(r =>
                    r.symbol === relData.relationship || r.value === relData.relationship
                ) || relationshipTypes[0];

                cy.add({
                    group: 'edges',
                    data: {
                        id: `edge_${relData.from_us}_${relData.to_us}`,
                        source: sourceNode.id(),
                        target: targetNode.id(),
                        label: relType.symbol,
                        relationship: relData.relationship,
                        relationshipType: relType.value,  // Store English value for saving
                        style: relType.style,
                        arrow: relType.arrow
                    }
                });
            } else {
                console.warn('Could not find nodes for relationship:', relData);
            }
        });

        // Apply automatic layout
        applyLayout();

        console.log('Loaded existing data successfully');
    } catch (error) {
        console.error('Error loading existing data:', error);
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Mode switching
    document.querySelectorAll('input[name="editorMode"]').forEach(radio => {
        radio.addEventListener('change', function(e) {
            editorMode = e.target.value;
            updateEditorMode();
        });
    });

    // Relationship type selection
    document.getElementById('relationshipType').addEventListener('change', function(e) {
        selectedRelationshipType = e.target.value;
    });

    // Apply node properties
    document.getElementById('apply-node-props-btn').addEventListener('click', applyNodeProperties);

    // Apply edge properties
    document.getElementById('apply-edge-props-btn').addEventListener('click', applyEdgeProperties);

    // Delete selected
    document.getElementById('delete-selected-btn').addEventListener('click', deleteSelected);

    // Clear all
    document.getElementById('clear-all-btn').addEventListener('click', clearAll);

    // Layout
    document.getElementById('layout-btn').addEventListener('click', applyLayout);

    // Canvas controls
    document.getElementById('zoom-in-btn').addEventListener('click', () => cy.zoom(cy.zoom() * 1.2));
    document.getElementById('zoom-out-btn').addEventListener('click', () => cy.zoom(cy.zoom() * 0.8));
    document.getElementById('fit-btn').addEventListener('click', () => cy.fit(50));

    // Save button
    document.getElementById('save-btn').addEventListener('click', saveMatrix);

    // Export buttons
    document.getElementById('export-graphml-btn').addEventListener('click', () => exportMatrix('graphml'));
    document.getElementById('export-dot-btn').addEventListener('click', () => exportMatrix('dot'));
}

/**
 * Update editor mode UI
 */
function updateEditorMode() {
    const indicator = document.getElementById('mode-indicator');
    const nodeTools = document.getElementById('node-tools');
    const edgeTools = document.getElementById('edge-tools');

    if (editorMode === 'node') {
        indicator.innerHTML = '<i class="fas fa-square"></i> Node Mode';
        indicator.className = '';
        nodeTools.style.display = 'block';
        edgeTools.style.display = 'none';
        resetEdgeCreation();
    } else {
        indicator.innerHTML = '<i class="fas fa-arrow-right"></i> Edge Mode';
        indicator.className = 'edge-mode';
        nodeTools.style.display = 'none';
        edgeTools.style.display = 'block';
    }
}

/**
 * Apply node properties from panel
 */
function applyNodeProperties() {
    if (!selectedElement || !selectedElement.isNode()) return;

    const node = selectedElement;
    const usNumber = document.getElementById('prop-us-number').value;
    const unitType = document.getElementById('prop-unit-type').value;
    const description = document.getElementById('prop-description').value;
    const area = document.getElementById('prop-area').value;
    const period = document.getElementById('prop-period').value;
    const phase = document.getElementById('prop-phase').value;
    const filePath = document.getElementById('prop-file-path').value;

    // Update node data
    node.data('us_number', usNumber);
    node.data('unit_type', unitType);
    node.data('description', description);
    node.data('area', area);
    node.data('period', period);
    node.data('phase', phase);
    node.data('file_path', filePath);
    node.data('label', `${unitType} ${usNumber}`);

    // Update color
    const nodeType = nodeTypes.find(t => t.value === unitType);
    if (nodeType) {
        node.data('color', nodeType.color);
        node.data('shape', nodeType.shape || 'rectangle');
    }

    showNotification('Node properties updated', 'success');
}

/**
 * Apply edge properties from panel
 */
function applyEdgeProperties() {
    if (!selectedElement || !selectedElement.isEdge()) return;

    const edge = selectedElement;
    const relationship = document.getElementById('prop-relationship-type').value;

    // Update edge data
    edge.data('relationship', relationship);

    // Update label and style
    const relType = relationshipTypes.find(r => r.value === relationship);
    if (relType) {
        edge.data('label', relType.symbol);
        edge.data('style', relType.style);
        edge.data('arrow', relType.arrow);
    }

    showNotification('Edge properties updated', 'success');
}

/**
 * Delete selected element
 */
function deleteSelected() {
    if (!selectedElement) {
        showNotification('No element selected', 'warning');
        return;
    }

    if (confirm('Delete selected element?')) {
        cy.remove(selectedElement);
        selectedElement = null;
        deselectAll();
        showNotification('Element deleted', 'success');
    }
}

/**
 * Clear all nodes and edges
 */
function clearAll() {
    if (cy.elements().length === 0) {
        showNotification('Canvas is already empty', 'info');
        return;
    }

    if (confirm('Clear all nodes and edges? This cannot be undone.')) {
        cy.elements().remove();
        deselectAll();
        showNotification('Canvas cleared', 'success');
    }
}

/**
 * Remove redundant (transitive) edges from the graph
 * Implements transitive reduction: if A->B->C exists, A->C is redundant
 * ONLY removes edges with a direct 2-hop path (A->B->C), not longer paths
 */
function removeTransitiveEdges() {
    console.log('Starting transitive reduction...');
    const edges = cy.edges();
    const edgesToRemove = [];

    // Build adjacency list for quick lookups
    const outgoing = new Map();  // Map of node -> Set of target nodes

    edges.forEach(edge => {
        const src = edge.source().id();
        const tgt = edge.target().id();

        if (!outgoing.has(src)) {
            outgoing.set(src, new Set());
        }
        outgoing.get(src).add(tgt);
    });

    // For each edge A->C, check if there exists a node B such that A->B and B->C
    edges.forEach(edge => {
        const source = edge.source().id();
        const target = edge.target().id();

        // Check if there's a 2-hop path: source -> intermediate -> target
        const sourceTargets = outgoing.get(source);
        if (!sourceTargets) return;

        let isRedundant = false;

        // For each intermediate node that source points to
        for (const intermediate of sourceTargets) {
            // Skip if intermediate is the target itself (that's the edge we're checking)
            if (intermediate === target) continue;

            // Check if intermediate also points to target
            const intermediateTargets = outgoing.get(intermediate);
            if (intermediateTargets && intermediateTargets.has(target)) {
                // Found a 2-hop path: source -> intermediate -> target
                // This makes the direct edge source -> target redundant
                isRedundant = true;
                console.log(`Redundant edge: ${source} -> ${target} (via ${intermediate})`);
                break;
            }
        }

        if (isRedundant) {
            edgesToRemove.push(edge);
        }
    });

    // Remove redundant edges
    if (edgesToRemove.length > 0) {
        const edgeCollection = cy.collection(edgesToRemove);
        edgeCollection.remove();
        console.log(`Removed ${edgesToRemove.length} redundant edges`);
        showNotification(`Rimossi ${edgesToRemove.length} archi ridondanti`, 'info');
    } else {
        console.log('No redundant edges found');
        showNotification('Nessun arco ridondante trovato', 'info');
    }
}

/**
 * Apply hierarchical layout for Harris Matrix
 * Uses Dagre for reliable hierarchical visualization
 */
function applyLayout() {
    if (cy.nodes().length === 0) {
        showNotification('No nodes to layout', 'warning');
        return;
    }

    // Remove redundant transitive edges before layout
    removeTransitiveEdges();

    // Use Dagre layout (more reliable than ELK)
    cy.layout({
        name: 'dagre',
        // Direction: top to bottom (most recent to oldest)
        rankDir: 'TB',
        // Alignment
        align: 'UL',
        // Spacing
        nodeSep: 100,
        edgeSep: 50,
        rankSep: 120,
        // Padding
        padding: 40,
        // Animation
        animate: true,
        animationDuration: 600,
        animationEasing: 'ease-out',
        // Fit to viewport
        fit: true,
        // Ranking algorithm
        ranker: 'network-simplex'
    }).run();

    showNotification('Layout applied', 'success');
}

/**
 * Save matrix to database
 */
async function saveMatrix() {
    const siteName = document.getElementById('site-name').value;

    if (cy.nodes().length === 0) {
        showNotification('No nodes to save', 'warning');
        return;
    }

    // Collect data
    const nodes = [];
    cy.nodes().forEach(node => {
        nodes.push({
            us_number: node.data('us_number'),
            unit_type: node.data('unit_type'),
            description: node.data('description'),
            area: node.data('area'),
            period: node.data('period'),
            phase: node.data('phase'),
            file_path: node.data('file_path')
        });
    });

    const relationships = [];
    cy.edges().forEach(edge => {
        const sourceNode = cy.getElementById(edge.data('source'));
        const targetNode = cy.getElementById(edge.data('target'));

        relationships.push({
            from_us: sourceNode.data('us_number'),
            to_us: targetNode.data('us_number'),
            relationship: edge.data('relationship')
        });
    });

    // Send to server
    try {
        console.log('[DEBUG] Sending data:', {
            site_name: siteName,
            nodes: nodes.length,
            relationships: relationships.length
        });

        const response = await fetch('/harris-creator/api/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                site_name: siteName,
                nodes: nodes,
                relationships: relationships
            })
        });

        console.log('[DEBUG] Response status:', response.status);
        console.log('[DEBUG] Response headers:', response.headers.get('content-type'));

        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('[DEBUG] Non-JSON response:', text);
            showNotification('Server error: Response is not JSON. Check server logs.', 'danger');
            return;
        }

        const result = await response.json();
        console.log('[DEBUG] Result:', result);

        if (result.success) {
            showNotification(
                `Saved: ${result.nodes_created + result.nodes_updated} nodes, ` +
                `${result.relationships_created + result.relationships_updated} relationships`,
                'success'
            );
        } else {
            showNotification('Error: ' + result.message, 'danger');
        }
    } catch (error) {
        console.error('Save error:', error);
        showNotification('Failed to save: ' + error.message, 'danger');
    }
}

/**
 * Export matrix to GraphML or DOT
 */
async function exportMatrix(format) {
    const siteName = document.getElementById('site-name').value;

    if (cy.nodes().length === 0) {
        showNotification('No nodes to export. Save first.', 'warning');
        return;
    }

    // First save
    showNotification('Saving before export...', 'info');
    await saveMatrix();

    // Then export
    const url = `/harris-creator/api/export/${format}?site=${encodeURIComponent(siteName)}`;
    window.location.href = url;

    showNotification(`Exporting to ${format.toUpperCase()}...`, 'success');
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Simple implementation - you can enhance with toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);

    // Create Bootstrap alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}