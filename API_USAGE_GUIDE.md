# PyArchInit-Mini API Usage Guide

Questa guida fornisce esempi pratici su come utilizzare le API di PyArchInit-Mini in contesti reali e con altre applicazioni.

## Indice

1. [Introduzione](#introduzione)
2. [Avvio del Sistema](#avvio-del-sistema)
3. [REST API - Utilizzo con HTTP](#rest-api---utilizzo-con-http)
4. [Python SDK - Utilizzo Programmatico](#python-sdk---utilizzo-programmatico)
5. [Integrazione con App Web](#integrazione-con-app-web)
6. [Integrazione con App Mobile](#integrazione-con-app-mobile)
7. [Esempi di Workflow Completi](#esempi-di-workflow-completi)
8. [Autenticazione e Sicurezza](#autenticazione-e-sicurezza)
9. [Monitoraggio e Logging](#monitoraggio-e-logging)

## Introduzione

PyArchInit-Mini fornisce un ecosistema completo per la gestione di dati archeologici attraverso:

- **REST API FastAPI**: Per integrazioni HTTP e applicazioni web/mobile
- **Python SDK**: Per utilizzo diretto da codice Python
- **Web Interface**: Interfaccia web completa con Bootstrap
- **Desktop GUI**: Applicazione desktop con Tkinter
- **CLI Interface**: Interfaccia a riga di comando con Rich

## Avvio del Sistema

### 1. Server API (REST API)

```bash
# Avvio server API su porta 8000
cd pyarchinit-mini
python main.py

# Server disponibile su:
# - API: http://localhost:8000
# - Documentazione: http://localhost:8000/docs
# - Redoc: http://localhost:8000/redoc
```

### 2. Interfaccia Web (Flask)

```bash
# Avvio interfaccia web su porta 5000
python web_interface/app.py

# Interfaccia disponibile su: http://localhost:5000
```

### 3. Interfaccia Desktop (Tkinter)

```bash
# Avvio applicazione desktop
python desktop_gui/gui_app.py
```

### 4. Interfaccia CLI (Rich)

```bash
# Avvio interfaccia CLI
python cli_interface/cli_app.py
```

## REST API - Utilizzo con HTTP

### Configurazione Database

```bash
# Configurazione PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost:5432/pyarchinit"

# Configurazione SQLite (default)
export DATABASE_URL="sqlite:///./pyarchinit_mini.db"
```

### Esempi con cURL

#### 1. Gestione Siti Archeologici

```bash
# Creare un nuovo sito
curl -X POST "http://localhost:8000/api/v1/sites/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "Pompei_Regio_VII",
    "nazione": "Italia",
    "regione": "Campania",
    "provincia": "Napoli",
    "comune": "Pompei",
    "descrizione": "Scavo Regio VII - Insula 12",
    "responsabile": "Dr. Mario Rossi",
    "data_schedatura": "2024-01-15"
  }'

# Ottenere lista siti
curl "http://localhost:8000/api/v1/sites/?page=1&size=10"

# Ottenere sito specifico
curl "http://localhost:8000/api/v1/sites/1"

# Aggiornare sito
curl -X PUT "http://localhost:8000/api/v1/sites/1" \
  -H "Content-Type: application/json" \
  -d '{
    "descrizione": "Scavo Regio VII - Insula 12 - Casa del Chirurgo"
  }'
```

#### 2. Gestione Unità Stratigrafiche (US)

```bash
# Creare nuova US
curl -X POST "http://localhost:8000/api/v1/us/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "Pompei_Regio_VII",
    "area": "A",
    "us": 1001,
    "d_stratigrafica": "Strato di abbandono con cenere vulcanica",
    "d_interpretativa": "Livello di distruzione eruzione 79 d.C.",
    "rapporti": "Copre US 1002, coperto da US 1000",
    "campioni": "Carbone (C14), Ceramica (Tipo)",
    "responsabile": "Dr. Laura Bianchi",
    "data_schedatura": "2024-01-16"
  }'

# Ottenere US per sito
curl "http://localhost:8000/api/v1/us/?sito=Pompei_Regio_VII&page=1&size=20"

# Cercare US
curl "http://localhost:8000/api/v1/us/search?q=abbandono"
```

#### 3. Gestione Inventario Materiali

```bash
# Creare nuovo reperto
curl -X POST "http://localhost:8000/api/v1/inventario/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "Pompei_Regio_VII",
    "numero_inventario": 2024001,
    "area": "A",
    "us": 1001,
    "tipo_reperto": "Ceramica",
    "definizione": "Coppa a vernice nera",
    "descrizione": "Coppa emisferica con anse",
    "stato_conservazione": "Frammentario",
    "peso": 145.5,
    "schedatore": "Dr. Franco Verdi",
    "date_scheda": "2024-01-16"
  }'

# Ottenere inventario per US
curl "http://localhost:8000/api/v1/inventario/?sito=Pompei_Regio_VII&us=1001"
```

#### 4. Harris Matrix

```bash
# Generare Harris Matrix per sito
curl "http://localhost:8000/api/v1/harris-matrix/Pompei_Regio_VII/generate"

# Ottenere relazioni stratigrafiche
curl "http://localhost:8000/api/v1/harris-matrix/Pompei_Regio_VII/relationships"

# Validare Harris Matrix
curl "http://localhost:8000/api/v1/harris-matrix/Pompei_Regio_VII/validate"
```

#### 5. Export PDF

```bash
# Esportare schede US
curl -X POST "http://localhost:8000/api/v1/export/us-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "Pompei_Regio_VII",
    "format": "complete"
  }' \
  --output us_report.pdf

# Esportare inventario
curl -X POST "http://localhost:8000/api/v1/export/inventario-pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "Pompei_Regio_VII",
    "tipo_reperto": "Ceramica"
  }' \
  --output inventario_ceramica.pdf
```

### Esempi con Python Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Classe helper per API
class PyArchInitAPI:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def create_site(self, site_data):
        """Crea nuovo sito"""
        response = self.session.post(
            f"{self.base_url}/sites/",
            json=site_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_sites(self, page=1, size=10, filters=None):
        """Ottieni lista siti"""
        params = {"page": page, "size": size}
        if filters:
            params.update(filters)
        
        response = self.session.get(
            f"{self.base_url}/sites/",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_us(self, us_data):
        """Crea nuova US"""
        response = self.session.post(
            f"{self.base_url}/us/",
            json=us_data
        )
        response.raise_for_status()
        return response.json()
    
    def get_harris_matrix(self, site_name):
        """Genera Harris Matrix"""
        response = self.session.get(
            f"{self.base_url}/harris-matrix/{site_name}/generate"
        )
        response.raise_for_status()
        return response.json()

# Esempio di utilizzo
api = PyArchInitAPI()

# Creare sito di test
site_data = {
    "sito": "Test_Scavo_2024",
    "nazione": "Italia",
    "regione": "Lazio", 
    "comune": "Roma",
    "descrizione": "Sito di test per API"
}

site = api.create_site(site_data)
print(f"Sito creato: {site['id_sito']}")

# Creare sequenza stratigrafica
us_sequence = [
    {
        "sito": "Test_Scavo_2024",
        "area": "A",
        "us": 1000,
        "d_stratigrafica": "Humus superficiale",
        "d_interpretativa": "Strato agricolo moderno"
    },
    {
        "sito": "Test_Scavo_2024", 
        "area": "A",
        "us": 1001,
        "d_stratigrafica": "Strato di abbandono",
        "d_interpretativa": "Crollo strutture medievali"
    },
    {
        "sito": "Test_Scavo_2024",
        "area": "A", 
        "us": 1002,
        "d_stratigrafica": "Livello pavimentale",
        "d_interpretativa": "Pavimento in opus signinum"
    }
]

for us_data in us_sequence:
    us = api.create_us(us_data)
    print(f"US creata: {us['us']}")

# Generare Harris Matrix
matrix = api.get_harris_matrix("Test_Scavo_2024")
print(f"Harris Matrix generata: {len(matrix.get('nodes', []))} nodi")
```

## Python SDK - Utilizzo Programmatico

### Utilizzo Diretto dei Servizi

```python
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService

# Configurazione database
db_connection = DatabaseConnection.sqlite("./my_excavation.db")
db_connection.initialize_database()

db_manager = DatabaseManager(db_connection)

# Inizializza servizi
site_service = SiteService(db_manager)
us_service = USService(db_manager)
inventario_service = InventarioService(db_manager)

# Esempio: Setup completo progetto scavo
class ExcavationProject:
    def __init__(self, db_path):
        self.db_connection = DatabaseConnection.sqlite(db_path)
        self.db_connection.initialize_database()
        self.db_manager = DatabaseManager(self.db_connection)
        
        # Servizi
        self.sites = SiteService(self.db_manager)
        self.us = USService(self.db_manager)
        self.inventory = InventarioService(self.db_manager)
        
    def create_excavation_site(self, site_name, location_data):
        """Crea sito di scavo con dati localizzazione"""
        site_data = {
            "sito": site_name,
            **location_data
        }
        return self.sites.create_site(site_data)
    
    def add_stratigraphic_unit(self, site_name, us_number, description_data):
        """Aggiungi unità stratigrafica"""
        us_data = {
            "sito": site_name,
            "us": us_number,
            **description_data
        }
        return self.us.create_us(us_data)
    
    def add_find(self, site_name, inventory_number, find_data):
        """Aggiungi reperto"""
        find_data.update({
            "sito": site_name,
            "numero_inventario": inventory_number
        })
        return self.inventory.create_inventario(find_data)
    
    def get_site_summary(self, site_name):
        """Ottieni riassunto sito"""
        site = self.sites.get_site_by_name(site_name)
        if not site:
            return None
            
        us_count = self.us.count_us({"sito": site_name})
        inv_count = self.inventory.count_inventario({"sito": site_name})
        
        return {
            "site": site,
            "us_count": us_count,
            "inventory_count": inv_count
        }

# Esempio di utilizzo
project = ExcavationProject("./villa_adriana.db")

# Creare sito
site = project.create_excavation_site(
    site_name="Villa_Adriana_2024",
    location_data={
        "nazione": "Italia",
        "regione": "Lazio",
        "provincia": "Roma",
        "comune": "Tivoli",
        "descrizione": "Scavo Villa Adriana - Settore Nord",
        "responsabile": "Prof. Elena Rossi"
    }
)

# Aggiungere US
us_data = [
    {"us": 2001, "d_stratigrafica": "Humus", "d_interpretativa": "Strato vegetale"},
    {"us": 2002, "d_stratigrafica": "Crollo", "d_interpretativa": "Crollo muro perimetrale"},
    {"us": 2003, "d_stratigrafica": "Pavimento", "d_interpretativa": "Pavimento mosaico"}
]

for data in us_data:
    project.add_stratigraphic_unit("Villa_Adriana_2024", data["us"], data)

# Aggiungere reperti
finds = [
    {
        "numero_inventario": 202401,
        "us": 2002,
        "tipo_reperto": "Ceramica",
        "definizione": "Anfora",
        "peso": 250.0
    },
    {
        "numero_inventario": 202402,
        "us": 2002,
        "tipo_reperto": "Moneta",
        "definizione": "Sesterzio",
        "peso": 12.5
    }
]

for find in finds:
    project.add_find("Villa_Adriana_2024", find["numero_inventario"], find)

# Ottenere riassunto
summary = project.get_site_summary("Villa_Adriana_2024")
print(f"Sito: {summary['site'].sito}")
print(f"US totali: {summary['us_count']}")
print(f"Reperti totali: {summary['inventory_count']}")
```

## Integrazione con App Web

### Frontend JavaScript/React

```javascript
// API Client per React/JavaScript
class PyArchInitClient {
    constructor(baseURL = 'http://localhost:8000/api/v1') {
        this.baseURL = baseURL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    }
    
    // Sites
    async getSites(page = 1, size = 10) {
        return this.request(`/sites/?page=${page}&size=${size}`);
    }
    
    async createSite(siteData) {
        return this.request('/sites/', {
            method: 'POST',
            body: JSON.stringify(siteData)
        });
    }
    
    // US
    async getUS(siteId, page = 1, size = 10) {
        return this.request(`/us/?sito=${siteId}&page=${page}&size=${size}`);
    }
    
    async createUS(usData) {
        return this.request('/us/', {
            method: 'POST',
            body: JSON.stringify(usData)
        });
    }
    
    // Harris Matrix
    async getHarrisMatrix(siteName) {
        return this.request(`/harris-matrix/${siteName}/generate`);
    }
    
    // Export
    async exportUSPDF(siteId) {
        const response = await fetch(`${this.baseURL}/export/us-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sito: siteId })
        });
        
        if (!response.ok) throw new Error('Export failed');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `US_${siteId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }
}

// Esempio componente React
import React, { useState, useEffect } from 'react';

const SiteManagement = () => {
    const [sites, setSites] = useState([]);
    const [loading, setLoading] = useState(true);
    const client = new PyArchInitClient();
    
    useEffect(() => {
        loadSites();
    }, []);
    
    const loadSites = async () => {
        try {
            const data = await client.getSites();
            setSites(data);
        } catch (error) {
            console.error('Error loading sites:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const createNewSite = async (siteData) => {
        try {
            await client.createSite(siteData);
            await loadSites(); // Ricarica lista
        } catch (error) {
            console.error('Error creating site:', error);
        }
    };
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div>
            <h1>Gestione Siti Archeologici</h1>
            <div className="sites-list">
                {sites.map(site => (
                    <div key={site.id_sito} className="site-card">
                        <h3>{site.sito}</h3>
                        <p>{site.descrizione}</p>
                        <button 
                            onClick={() => client.exportUSPDF(site.sito)}
                        >
                            Esporta PDF
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};
```

### Vue.js Integration

```javascript
// Composable per Vue 3
import { ref, reactive } from 'vue';

export function useArchaeology() {
    const sites = ref([]);
    const loading = ref(false);
    const error = ref(null);
    
    const client = new PyArchInitClient();
    
    const loadSites = async () => {
        loading.value = true;
        error.value = null;
        
        try {
            sites.value = await client.getSites();
        } catch (err) {
            error.value = err.message;
        } finally {
            loading.value = false;
        }
    };
    
    const createSite = async (siteData) => {
        try {
            const newSite = await client.createSite(siteData);
            sites.value.push(newSite);
            return newSite;
        } catch (err) {
            error.value = err.message;
            throw err;
        }
    };
    
    return {
        sites,
        loading,
        error,
        loadSites,
        createSite
    };
}

// Componente Vue
<template>
  <div class="archaeology-app">
    <h1>PyArchInit-Mini Dashboard</h1>
    
    <div v-if="loading">Caricamento...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    
    <div v-else>
      <button @click="showCreateForm = true">Nuovo Sito</button>
      
      <div class="sites-grid">
        <div 
          v-for="site in sites" 
          :key="site.id_sito"
          class="site-card"
        >
          <h3>{{ site.sito }}</h3>
          <p>{{ site.comune }}, {{ site.provincia }}</p>
          <button @click="viewSite(site.id_sito)">Visualizza</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useArchaeology } from './composables/useArchaeology';

const { sites, loading, error, loadSites } = useArchaeology();
const showCreateForm = ref(false);

onMounted(() => {
    loadSites();
});

const viewSite = (siteId) => {
    // Navigate to site detail view
    router.push(`/sites/${siteId}`);
};
</script>
```

## Integrazione con App Mobile

### React Native

```javascript
// ArchaeologyService.js
class ArchaeologyService {
    constructor() {
        this.baseURL = 'http://10.0.2.2:8000/api/v1'; // Android emulator
        // this.baseURL = 'http://localhost:8000/api/v1'; // iOS simulator
    }
    
    async getSites() {
        const response = await fetch(`${this.baseURL}/sites/`);
        return response.json();
    }
    
    async createUS(usData) {
        const response = await fetch(`${this.baseURL}/us/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(usData)
        });
        return response.json();
    }
    
    async uploadImage(imageUri, usId) {
        const formData = new FormData();
        formData.append('file', {
            uri: imageUri,
            type: 'image/jpeg',
            name: 'photo.jpg'
        });
        formData.append('us_id', usId.toString());
        
        const response = await fetch(`${this.baseURL}/media/upload`, {
            method: 'POST',
            headers: { 'Content-Type': 'multipart/form-data' },
            body: formData
        });
        
        return response.json();
    }
}

// Componente React Native
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert } from 'react-native';
import { launchImageLibrary } from 'react-native-image-picker';

const FieldApp = () => {
    const [sites, setSites] = useState([]);
    const service = new ArchaeologyService();
    
    useEffect(() => {
        loadSites();
    }, []);
    
    const loadSites = async () => {
        try {
            const sitesData = await service.getSites();
            setSites(sitesData);
        } catch (error) {
            Alert.alert('Errore', 'Impossibile caricare i siti');
        }
    };
    
    const takePhoto = () => {
        launchImageLibrary({ mediaType: 'photo' }, (response) => {
            if (response.assets && response.assets[0]) {
                const imageUri = response.assets[0].uri;
                // Upload to server
                service.uploadImage(imageUri, selectedUSId);
            }
        });
    };
    
    return (
        <View style={{ flex: 1, padding: 20 }}>
            <Text style={{ fontSize: 24, fontWeight: 'bold' }}>
                Siti Archeologici
            </Text>
            
            <FlatList
                data={sites}
                keyExtractor={(item) => item.id_sito.toString()}
                renderItem={({ item }) => (
                    <TouchableOpacity 
                        style={{ padding: 15, borderBottomWidth: 1 }}
                        onPress={() => navigateToSite(item.id_sito)}
                    >
                        <Text style={{ fontSize: 18 }}>{item.sito}</Text>
                        <Text style={{ color: 'gray' }}>
                            {item.comune}, {item.provincia}
                        </Text>
                    </TouchableOpacity>
                )}
            />
            
            <TouchableOpacity 
                style={{ 
                    backgroundColor: 'blue', 
                    padding: 15, 
                    borderRadius: 8,
                    marginTop: 20
                }}
                onPress={takePhoto}
            >
                <Text style={{ color: 'white', textAlign: 'center' }}>
                    Scatta Foto
                </Text>
            </TouchableOpacity>
        </View>
    );
};
```

### Flutter Integration

```dart
// archaeology_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ArchaeologyService {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  
  Future<List<Site>> getSites() async {
    final response = await http.get(Uri.parse('$baseUrl/sites/'));
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Site.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load sites');
    }
  }
  
  Future<US> createUS(Map<String, dynamic> usData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/us/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode(usData),
    );
    
    if (response.statusCode == 201) {
      return US.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to create US');
    }
  }
}

// models/site.dart
class Site {
  final int idSito;
  final String sito;
  final String? comune;
  final String? provincia;
  final String? descrizione;
  
  Site({
    required this.idSito,
    required this.sito,
    this.comune,
    this.provincia,
    this.descrizione,
  });
  
  factory Site.fromJson(Map<String, dynamic> json) {
    return Site(
      idSito: json['id_sito'],
      sito: json['sito'],
      comune: json['comune'],
      provincia: json['provincia'],
      descrizione: json['descrizione'],
    );
  }
}

// widgets/site_list.dart
import 'package:flutter/material.dart';

class SiteList extends StatefulWidget {
  @override
  _SiteListState createState() => _SiteListState();
}

class _SiteListState extends State<SiteList> {
  final ArchaeologyService _service = ArchaeologyService();
  List<Site> _sites = [];
  bool _loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadSites();
  }
  
  Future<void> _loadSites() async {
    try {
      final sites = await _service.getSites();
      setState(() {
        _sites = sites;
        _loading = false;
      });
    } catch (error) {
      setState(() => _loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Errore nel caricamento: $error')),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Center(child: CircularProgressIndicator());
    }
    
    return ListView.builder(
      itemCount: _sites.length,
      itemBuilder: (context, index) {
        final site = _sites[index];
        return ListTile(
          title: Text(site.sito),
          subtitle: Text('${site.comune}, ${site.provincia}'),
          trailing: Icon(Icons.arrow_forward_ios),
          onTap: () {
            Navigator.pushNamed(
              context, 
              '/site-detail',
              arguments: site.idSito,
            );
          },
        );
      },
    );
  }
}
```

## Esempi di Workflow Completi

### 1. Workflow Completo Scavo Archeologico

```python
"""
Workflow completo per gestione scavo archeologico
Dalla creazione del sito alla pubblicazione dei risultati
"""

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.services import *
from datetime import datetime

class ExcavationWorkflow:
    def __init__(self, database_url):
        self.db_connection = DatabaseConnection.from_url(database_url)
        self.db_connection.initialize_database()
        self.db_manager = DatabaseManager(self.db_connection)
        
        # Initialize services
        self.sites = SiteService(self.db_manager)
        self.us = USService(self.db_manager)
        self.inventory = InventarioService(self.db_manager)
        self.harris = HarrisMatrixService(self.db_manager)
        self.export = ExportService(self.db_manager)
        
    def setup_excavation_project(self, project_data):
        """Phase 1: Setup new excavation project"""
        print("🏛️  Setting up excavation project...")
        
        # Create main site
        site = self.sites.create_site({
            "sito": project_data["site_name"],
            "nazione": project_data["country"],
            "regione": project_data["region"],
            "provincia": project_data["province"],
            "comune": project_data["municipality"],
            "descrizione": project_data["description"],
            "responsabile": project_data["director"],
            "data_schedatura": datetime.now().strftime("%Y-%m-%d")
        })
        
        print(f"✅ Site created: {site.sito}")
        return site
    
    def document_stratigraphy(self, site_name, stratigraphic_data):
        """Phase 2: Document stratigraphic sequence"""
        print("📋 Documenting stratigraphy...")
        
        created_us = []
        for us_data in stratigraphic_data:
            us_data["sito"] = site_name
            us_data["data_schedatura"] = datetime.now().strftime("%Y-%m-%d")
            
            us = self.us.create_us(us_data)
            created_us.append(us)
            print(f"✅ US {us.us} created")
        
        return created_us
    
    def process_finds(self, site_name, finds_data):
        """Phase 3: Process and catalog finds"""
        print("🏺 Processing finds...")
        
        processed_finds = []
        for find_data in finds_data:
            find_data["sito"] = site_name
            find_data["date_scheda"] = datetime.now().strftime("%Y-%m-%d")
            
            find = self.inventory.create_inventario(find_data)
            processed_finds.append(find)
            print(f"✅ Find {find.numero_inventario} cataloged")
        
        return processed_finds
    
    def analyze_relationships(self, site_name):
        """Phase 4: Analyze stratigraphic relationships"""
        print("🕸️  Analyzing stratigraphic relationships...")
        
        # Generate Harris Matrix
        matrix = self.harris.generate_matrix(site_name)
        
        # Validate relationships
        validation = self.harris.validate_relationships(site_name)
        
        if validation["valid"]:
            print("✅ Harris Matrix is valid")
        else:
            print(f"⚠️  Harris Matrix has issues: {validation['errors']}")
        
        return matrix, validation
    
    def generate_reports(self, site_name):
        """Phase 5: Generate documentation"""
        print("📄 Generating reports...")
        
        reports = {}
        
        # Generate US report
        us_pdf = self.export.generate_us_pdf(site_name)
        reports["us_report"] = us_pdf
        print("✅ US report generated")
        
        # Generate inventory report
        inv_pdf = self.export.generate_inventory_pdf(site_name)
        reports["inventory_report"] = inv_pdf
        print("✅ Inventory report generated")
        
        # Generate Harris Matrix visualization
        matrix_svg = self.harris.export_matrix_svg(site_name)
        reports["harris_matrix"] = matrix_svg
        print("✅ Harris Matrix exported")
        
        return reports
    
    def complete_workflow_example(self):
        """Complete workflow example"""
        # Project setup
        project = {
            "site_name": "Domus_Romana_2024",
            "country": "Italia",
            "region": "Lazio",
            "province": "Roma",
            "municipality": "Roma",
            "description": "Scavo domus romana - Via Appia",
            "director": "Prof. Marco Antonelli"
        }
        
        site = self.setup_excavation_project(project)
        
        # Stratigraphic documentation
        stratigraphy = [
            {
                "area": "A",
                "us": 3001,
                "d_stratigrafica": "Humus superficiale",
                "d_interpretativa": "Strato agricolo moderno",
                "rapporti": "Copre US 3002"
            },
            {
                "area": "A", 
                "us": 3002,
                "d_stratigrafica": "Strato di abbandono con tegole",
                "d_interpretativa": "Crollo copertura domus",
                "rapporti": "Copre US 3003, coperto da US 3001"
            },
            {
                "area": "A",
                "us": 3003,
                "d_stratigrafica": "Pavimento in opus sectile",
                "d_interpretativa": "Pavimento triclinium",
                "rapporti": "Coperto da US 3002"
            }
        ]
        
        us_list = self.document_stratigraphy(site.sito, stratigraphy)
        
        # Finds processing
        finds = [
            {
                "numero_inventario": 300101,
                "area": "A",
                "us": 3002,
                "tipo_reperto": "Ceramica",
                "definizione": "Tegola",
                "peso": 850.0,
                "stato_conservazione": "Frammentario"
            },
            {
                "numero_inventario": 300102,
                "area": "A", 
                "us": 3002,
                "tipo_reperto": "Moneta",
                "definizione": "Denario",
                "peso": 3.2,
                "stato_conservazione": "Buono"
            },
            {
                "numero_inventario": 300103,
                "area": "A",
                "us": 3003,
                "tipo_reperto": "Marmo",
                "definizione": "Tessera opus sectile",
                "peso": 125.0,
                "stato_conservazione": "Integro"
            }
        ]
        
        finds_list = self.process_finds(site.sito, finds)
        
        # Analysis
        matrix, validation = self.analyze_relationships(site.sito)
        
        # Documentation
        reports = self.generate_reports(site.sito)
        
        print(f"\n🎉 Workflow completed for {site.sito}")
        print(f"📊 Statistics:")
        print(f"   - US documented: {len(us_list)}")
        print(f"   - Finds processed: {len(finds_list)}")
        print(f"   - Reports generated: {len(reports)}")
        
        return {
            "site": site,
            "us": us_list,
            "finds": finds_list,
            "matrix": matrix,
            "validation": validation,
            "reports": reports
        }

# Usage
workflow = ExcavationWorkflow("postgresql://user:pass@localhost/excavation_db")
results = workflow.complete_workflow_example()
```

### 2. Integration con GIS

```python
"""
Integrazione con sistemi GIS per dati spaziali
"""

import geopandas as gpd
from shapely.geometry import Point, Polygon
import requests

class GISIntegration:
    def __init__(self, api_base_url="http://localhost:8000/api/v1"):
        self.api_url = api_base_url
        
    def import_sites_from_gis(self, shapefile_path):
        """Import sites from GIS shapefile"""
        # Read shapefile
        gdf = gpd.read_file(shapefile_path)
        
        imported_sites = []
        for _, row in gdf.iterrows():
            site_data = {
                "sito": row["SITE_NAME"],
                "comune": row.get("MUNICIPALITY", ""),
                "provincia": row.get("PROVINCE", ""),
                "descrizione": row.get("DESCRIPTION", ""),
                "coordinate_x": row.geometry.x if row.geometry else None,
                "coordinate_y": row.geometry.y if row.geometry else None
            }
            
            # Create site via API
            response = requests.post(
                f"{self.api_url}/sites/",
                json=site_data
            )
            
            if response.status_code == 201:
                imported_sites.append(response.json())
                
        return imported_sites
    
    def export_sites_to_gis(self, output_path):
        """Export sites to GIS format"""
        # Get sites from API
        response = requests.get(f"{self.api_url}/sites/")
        sites = response.json()
        
        # Create GeoDataFrame
        geometries = []
        data = []
        
        for site in sites:
            if site.get("coordinate_x") and site.get("coordinate_y"):
                point = Point(site["coordinate_x"], site["coordinate_y"])
                geometries.append(point)
                data.append({
                    "SITE_ID": site["id_sito"],
                    "SITE_NAME": site["sito"],
                    "MUNICIPALITY": site.get("comune", ""),
                    "PROVINCE": site.get("provincia", ""),
                    "DESCRIPTION": site.get("descrizione", "")
                })
        
        gdf = gpd.GeoDataFrame(data, geometry=geometries)
        gdf.to_file(output_path)
        
        return gdf

# Usage
gis = GISIntegration()
sites = gis.import_sites_from_gis("archaeological_sites.shp")
exported_gdf = gis.export_sites_to_gis("exported_sites.geojson")
```

## Autenticazione e Sicurezza

```python
"""
Implementazione autenticazione JWT
"""

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, secret_key="your-secret-key"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.security = HTTPBearer()
    
    def create_token(self, user_data: dict):
        """Create JWT token"""
        payload = {
            "user_id": user_data["id"],
            "username": user_data["username"],
            "role": user_data.get("role", "user"),
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                credentials.credentials, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# Utilizzo nelle API routes
auth_service = AuthService()

@app.post("/auth/login")
async def login(credentials: dict):
    # Verify user credentials
    user = verify_user_credentials(credentials["username"], credentials["password"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_service.create_token(user)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected-endpoint")
async def protected_route(current_user = Depends(auth_service.verify_token)):
    return {"message": f"Hello {current_user['username']}"}
```

## Monitoraggio e Logging

```python
"""
Sistema di monitoraggio e logging
"""

import logging
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pyarchinit_mini.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class MonitoringMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # Process request
            await self.app(scope, receive, send)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_LATENCY.observe(duration)
            REQUEST_COUNT.labels(
                method=scope["method"],
                endpoint=scope["path"]
            ).inc()
            
            # Log request
            logger.info(f"{scope['method']} {scope['path']} - {duration:.2f}s")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
```

Questa guida fornisce esempi completi e pratici per utilizzare PyArchInit-Mini in diversi contesti applicativi. Il sistema è progettato per essere flessibile e facilmente integrabile con tecnologie esistenti.