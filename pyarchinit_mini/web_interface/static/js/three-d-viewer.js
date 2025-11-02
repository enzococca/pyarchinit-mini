/**
 * 3D Stratigraphic Viewer
 *
 * Three.js-based interactive 3D viewer for stratigraphic proxy objects.
 * Integrates with PyArchInit MCP server and displays archaeological layers.
 */

class StratigraphicViewer3D {
    constructor(containerElement) {
        this.container = containerElement;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.raycaster = null;
        this.mouse = null;

        // Proxy management
        this.proxies = new Map(); // Map<us_id, {mesh, metadata, label}>
        this.selectedProxy = null;
        this.hoveredProxy = null;

        // Settings
        this.settings = {
            showLabels: true,
            showGrid: true,
            showAxes: true,
            backgroundColor: 0x1a1a1a,
            ambientLightIntensity: 0.6,
            directionalLightIntensity: 0.8,
            enableShadows: true
        };

        // Callbacks
        this.onProxySelect = null;
        this.onProxyHover = null;

        this.init();
    }

    /**
     * Initialize Three.js scene
     */
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.settings.backgroundColor);

        // Create camera
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(
            60,
            width / height,
            0.1,
            1000
        );
        this.camera.position.set(10, 10, 10);
        this.camera.lookAt(0, 0, 0);

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        if (this.settings.enableShadows) {
            this.renderer.shadowMap.enabled = true;
            this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        }

        this.container.appendChild(this.renderer.domElement);

        // Add lights
        this.addLights();

        // Add grid and axes
        if (this.settings.showGrid) {
            this.addGrid();
        }

        if (this.settings.showAxes) {
            this.addAxes();
        }

        // Setup controls
        this.setupControls();

        // Setup raycaster for object picking
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        // Event listeners
        this.setupEventListeners();

        // Start animation loop
        this.animate();

        console.log('StratigraphicViewer3D initialized');
    }

    /**
     * Add lighting to scene
     */
    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(
            0xffffff,
            this.settings.ambientLightIntensity
        );
        this.scene.add(ambientLight);

        // Directional light (sun)
        const directionalLight = new THREE.DirectionalLight(
            0xffffff,
            this.settings.directionalLightIntensity
        );
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = this.settings.enableShadows;

        if (this.settings.enableShadows) {
            directionalLight.shadow.camera.left = -20;
            directionalLight.shadow.camera.right = 20;
            directionalLight.shadow.camera.top = 20;
            directionalLight.shadow.camera.bottom = -20;
            directionalLight.shadow.camera.near = 0.1;
            directionalLight.shadow.camera.far = 50;
            directionalLight.shadow.mapSize.width = 2048;
            directionalLight.shadow.mapSize.height = 2048;
        }

        this.scene.add(directionalLight);

        // Hemisphere light (ground/sky)
        const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.4);
        this.scene.add(hemisphereLight);
    }

    /**
     * Add grid helper
     */
    addGrid() {
        const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
        gridHelper.name = 'grid';
        this.scene.add(gridHelper);
    }

    /**
     * Add axes helper
     */
    addAxes() {
        const axesHelper = new THREE.AxesHelper(5);
        axesHelper.name = 'axes';
        this.scene.add(axesHelper);
    }

    /**
     * Setup camera controls
     */
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 2;
        this.controls.maxDistance = 100;
        this.controls.maxPolarAngle = Math.PI / 2;
        this.controls.target.set(0, 0, 0);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Window resize
        window.addEventListener('resize', () => this.onWindowResize(), false);

        // Mouse events for object picking
        this.renderer.domElement.addEventListener('click', (e) => this.onMouseClick(e), false);
        this.renderer.domElement.addEventListener('mousemove', (e) => this.onMouseMove(e), false);
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    /**
     * Handle mouse click for object selection
     */
    onMouseClick(event) {
        this.updateMousePosition(event);

        const intersects = this.getIntersectedProxies();

        if (intersects.length > 0) {
            const proxy = intersects[0].object.userData.proxy;
            this.selectProxy(proxy.us_id);
        } else {
            this.deselectProxy();
        }
    }

    /**
     * Handle mouse move for object hover
     */
    onMouseMove(event) {
        this.updateMousePosition(event);

        const intersects = this.getIntersectedProxies();

        if (intersects.length > 0) {
            const proxy = intersects[0].object.userData.proxy;
            this.hoverProxy(proxy.us_id);
        } else {
            this.unhoverProxy();
        }
    }

    /**
     * Update mouse position for raycasting
     */
    updateMousePosition(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }

    /**
     * Get intersected proxy objects
     */
    getIntersectedProxies() {
        this.raycaster.setFromCamera(this.mouse, this.camera);

        const meshes = [];
        this.proxies.forEach((proxy) => {
            if (proxy.mesh && proxy.mesh.visible) {
                meshes.push(proxy.mesh);
            }
        });

        return this.raycaster.intersectObjects(meshes);
    }

    /**
     * Load proxies from session data
     * @param {Array} proxiesData - Array of proxy metadata objects
     */
    loadProxies(proxiesData) {
        console.log(`Loading ${proxiesData.length} proxies...`);

        // Clear existing proxies
        this.clearProxies();

        // Create mesh for each proxy
        proxiesData.forEach(proxyData => {
            this.createProxy(proxyData);
        });

        // Center camera on all proxies
        this.centerCameraOnProxies();

        console.log(`Loaded ${this.proxies.size} proxies`);
    }

    /**
     * Create 3D mesh for proxy
     * @param {Object} proxyData - Proxy metadata
     */
    createProxy(proxyData) {
        console.log('Creating proxy:', proxyData);

        const blenderProps = proxyData.blender_properties;
        const visualization = proxyData.visualization;

        console.log('Blender properties:', blenderProps);
        console.log('Location:', blenderProps.location);
        console.log('Scale:', blenderProps.scale);

        // Create geometry
        const geometry = new THREE.BoxGeometry(
            blenderProps.scale.x,
            blenderProps.scale.z,  // Z and Y swapped for Three.js
            blenderProps.scale.y
        );

        // Create material
        const material = this.createProxyMaterial(blenderProps.material);

        // Create mesh
        const mesh = new THREE.Mesh(geometry, material);

        // Set position (swap Y and Z for Three.js coordinate system)
        mesh.position.set(
            blenderProps.location.x,
            blenderProps.location.z,
            blenderProps.location.y
        );

        // Set rotation
        mesh.rotation.set(
            blenderProps.rotation.x,
            blenderProps.rotation.y,
            blenderProps.rotation.z
        );

        // Set visibility
        mesh.visible = visualization.visible;

        // Enable shadows
        if (this.settings.enableShadows) {
            mesh.castShadow = true;
            mesh.receiveShadow = true;
        }

        // Store proxy reference in mesh
        mesh.userData.proxy = proxyData;
        mesh.userData.us_id = proxyData.us_id;

        // Add to scene
        this.scene.add(mesh);

        // Create label
        const label = this.createProxyLabel(proxyData, mesh);

        // Store proxy
        this.proxies.set(proxyData.us_id, {
            mesh: mesh,
            metadata: proxyData,
            label: label,
            originalMaterial: material.clone()
        });
    }

    /**
     * Create material for proxy
     * @param {Object} materialData - Material properties
     * @returns {THREE.Material}
     */
    createProxyMaterial(materialData) {
        const color = new THREE.Color(
            materialData.base_color[0],
            materialData.base_color[1],
            materialData.base_color[2]
        );

        const material = new THREE.MeshStandardMaterial({
            color: color,
            roughness: materialData.roughness,
            metalness: materialData.metallic,
            transparent: materialData.alpha < 1.0,
            opacity: materialData.alpha,
            side: THREE.DoubleSide
        });

        return material;
    }

    /**
     * Create text label for proxy
     * @param {Object} proxyData - Proxy metadata
     * @param {THREE.Mesh} mesh - Proxy mesh
     * @returns {THREE.Sprite}
     */
    createProxyLabel(proxyData, mesh) {
        if (!this.settings.showLabels) {
            return null;
        }

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;

        // Draw label background
        context.fillStyle = 'rgba(0, 0, 0, 0.7)';
        context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw label text
        context.font = 'Bold 24px Arial';
        context.fillStyle = 'white';
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(`US ${proxyData.us_id}`, canvas.width / 2, canvas.height / 2);

        // Create sprite
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);

        // Position above mesh
        sprite.position.copy(mesh.position);
        sprite.position.y += (mesh.geometry.parameters.height / 2) + 0.5;
        sprite.scale.set(2, 0.5, 1);

        sprite.visible = proxyData.visualization.label_visible;

        this.scene.add(sprite);

        return sprite;
    }

    /**
     * Select proxy by US ID
     */
    selectProxy(usId) {
        // Deselect previous
        if (this.selectedProxy && this.selectedProxy !== usId) {
            this.deselectProxy();
        }

        const proxy = this.proxies.get(usId);
        if (!proxy) return;

        this.selectedProxy = usId;

        // Highlight selected proxy
        proxy.mesh.material.emissive = new THREE.Color(0x00ff00);
        proxy.mesh.material.emissiveIntensity = 0.3;

        // Callback
        if (this.onProxySelect) {
            this.onProxySelect(proxy.metadata);
        }
    }

    /**
     * Deselect current proxy
     */
    deselectProxy() {
        if (!this.selectedProxy) return;

        const proxy = this.proxies.get(this.selectedProxy);
        if (proxy) {
            proxy.mesh.material.emissive = new THREE.Color(0x000000);
            proxy.mesh.material.emissiveIntensity = 0;
        }

        this.selectedProxy = null;

        if (this.onProxySelect) {
            this.onProxySelect(null);
        }
    }

    /**
     * Hover proxy by US ID
     */
    hoverProxy(usId) {
        if (this.hoveredProxy === usId) return;

        // Unhover previous
        if (this.hoveredProxy) {
            this.unhoverProxy();
        }

        const proxy = this.proxies.get(usId);
        if (!proxy || usId === this.selectedProxy) return;

        this.hoveredProxy = usId;

        // Highlight hovered proxy
        proxy.mesh.material.emissive = new THREE.Color(0xffff00);
        proxy.mesh.material.emissiveIntensity = 0.2;

        // Change cursor
        this.renderer.domElement.style.cursor = 'pointer';

        // Callback
        if (this.onProxyHover) {
            this.onProxyHover(proxy.metadata);
        }
    }

    /**
     * Unhover current proxy
     */
    unhoverProxy() {
        if (!this.hoveredProxy) return;

        const proxy = this.proxies.get(this.hoveredProxy);
        if (proxy && this.hoveredProxy !== this.selectedProxy) {
            proxy.mesh.material.emissive = new THREE.Color(0x000000);
            proxy.mesh.material.emissiveIntensity = 0;
        }

        this.hoveredProxy = null;
        this.renderer.domElement.style.cursor = 'default';

        if (this.onProxyHover) {
            this.onProxyHover(null);
        }
    }

    /**
     * Update proxy visibility
     */
    updateProxyVisibility(usId, visible) {
        const proxy = this.proxies.get(usId);
        if (!proxy) return;

        proxy.mesh.visible = visible;
        if (proxy.label) {
            proxy.label.visible = visible && this.settings.showLabels;
        }
    }

    /**
     * Update proxy transparency
     */
    updateProxyTransparency(usId, opacity) {
        const proxy = this.proxies.get(usId);
        if (!proxy) return;

        proxy.mesh.material.transparent = opacity < 1.0;
        proxy.mesh.material.opacity = opacity;
        proxy.mesh.material.needsUpdate = true;
    }

    /**
     * Update all proxies transparency
     */
    updateAllTransparency(opacity) {
        this.proxies.forEach((proxy, usId) => {
            this.updateProxyTransparency(usId, opacity);
        });
    }

    /**
     * Clear all proxies from scene
     */
    clearProxies() {
        this.proxies.forEach((proxy) => {
            this.scene.remove(proxy.mesh);
            if (proxy.label) {
                this.scene.remove(proxy.label);
            }

            proxy.mesh.geometry.dispose();
            proxy.mesh.material.dispose();
        });

        this.proxies.clear();
        this.selectedProxy = null;
        this.hoveredProxy = null;
    }

    /**
     * Center camera on all proxies
     */
    centerCameraOnProxies() {
        if (this.proxies.size === 0) {
            console.log('No proxies to center on');
            return;
        }

        console.log(`Centering camera on ${this.proxies.size} proxies`);

        // Calculate bounding box
        const box = new THREE.Box3();

        this.proxies.forEach((proxy) => {
            box.expandByObject(proxy.mesh);
        });

        // Get center and size
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        console.log('Bounding box center:', center);
        console.log('Bounding box size:', size);

        // Calculate camera distance
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        const cameraDistance = Math.abs(maxDim / Math.sin(fov / 2)) * 1.5;

        console.log('Camera distance:', cameraDistance);

        // Position camera
        this.camera.position.set(
            center.x + cameraDistance * 0.7,
            center.y + cameraDistance * 0.7,
            center.z + cameraDistance * 0.7
        );

        console.log('Camera position:', this.camera.position);

        this.camera.lookAt(center);
        this.controls.target.copy(center);
        this.controls.update();
    }

    /**
     * Toggle grid visibility
     */
    toggleGrid(visible) {
        const grid = this.scene.getObjectByName('grid');
        if (grid) {
            grid.visible = visible;
        }
        this.settings.showGrid = visible;
    }

    /**
     * Toggle axes visibility
     */
    toggleAxes(visible) {
        const axes = this.scene.getObjectByName('axes');
        if (axes) {
            axes.visible = visible;
        }
        this.settings.showAxes = visible;
    }

    /**
     * Toggle labels visibility
     */
    toggleLabels(visible) {
        this.settings.showLabels = visible;

        this.proxies.forEach((proxy) => {
            if (proxy.label) {
                proxy.label.visible = visible && proxy.mesh.visible;
            }
        });
    }

    /**
     * Animation loop
     */
    animate() {
        requestAnimationFrame(() => this.animate());

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Dispose and cleanup
     */
    dispose() {
        this.clearProxies();

        window.removeEventListener('resize', this.onWindowResize);

        if (this.renderer) {
            this.renderer.dispose();
            this.container.removeChild(this.renderer.domElement);
        }

        if (this.controls) {
            this.controls.dispose();
        }

        console.log('StratigraphicViewer3D disposed');
    }
}

// Export for use in other scripts
window.StratigraphicViewer3D = StratigraphicViewer3D;
