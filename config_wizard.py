import streamlit as st
import requests
import pandas as pd
import geopandas as gpd
import random
import json
import io
import zipfile
import tempfile
import os
import urllib3

# ==============================================================================
# 0. CONFIGURAÇÕES GERAIS E SSL
# ==============================================================================

st.set_page_config(layout="wide", page_title="Configurador de Bases Mutum")

# Silencia o aviso de "InsecureRequestWarning"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# 1. DADOS DE CONFIGURAÇÃO
# ==============================================================================

# --- URLS GITHUB (ARQUIVOS ESTÁTICOS) ---
URL_GEOJSON_GITHUB = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/focos_historico.zip"
URL_HIDRO_OFFLINE = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/hidrografia_MS.zip"
URL_AUTEX_IBAMA = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/Dados_Agrupados_QGIS.zip"
URL_PARQUET_CONVERTED = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/converted_data.parquet"

# --- LISTAS DE BASES ---

BASES_ADMINISTRATIVAS = [
    {"nome": "Municípios MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/38/query", "tipo": "poligono"},
    {"nome": "Biomas em MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/lim_biomas_atual/MapServer/0/query", "tipo": "poligono"}
]

BASES_CAR = [
    {"nome": "CAR - Limite da Propriedade", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_lim_propriedade/FeatureServer/8/query", "tipo": "poligono"},
    {"nome": "CAR - Uso Restrito", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_uso_restrito/FeatureServer/3/query", "tipo": "poligono"},
    {"nome": "CAR - Uso Consolidado", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_uso_consolidado/FeatureServer/4/query", "tipo": "poligono"},
    {"nome": "CAR - Servidão Administrativa", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_servidao_adm/FeatureServer/5/query", "tipo": "poligono"},
    {"nome": "CAR - Reserva Legal", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_reserva_legal/FeatureServer/6/query", "tipo": "poligono"},
    {"nome": "CAR - Remanescente Veg. Nativa", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_remanescente_veg_nativa/FeatureServer/7/query", "tipo": "poligono"},
    {"nome": "CAR - Áreas de Preservação Permanente (APP)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_app/FeatureServer/9/query", "tipo": "poligono"}
]

BASES_GERAIS = [
    {"nome": "Unidades de Conservação", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/UCs_MS_Mosaico/MapServer/0/query", "tipo": "poligono"},
    {"nome": "Terras Indígenas", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/4/query", "tipo": "poligono"},
    {"nome": "Povos Tradicionais (Quilombolas)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/AGRAER_SERVICOS/Povos_Tradicionais/MapServer/2/query", "tipo": "poligono"},
    {"nome": "Áreas de Uso Restrito (Dec. 15.661)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/49/query", "tipo": "poligono"},
    {"nome": "Áreas Priorit. Banhados", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/52/query", "tipo": "poligono"},
    {"nome": "Corredores Ecológicos do Pantanal", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/Corredores_Ecológicos_Pantanal/MapServer/0/query", "tipo": "poligono"},
    {"nome": "Área de Entorno 0-3 Km (Rio Taquari)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/48/query", "tipo": "poligono"},
    {"nome": "Zona de Amortecimento (Estaduais)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/2/query", "tipo": "poligono"},
    {"nome": "ZA (Conama 0-2km)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/1/query", "tipo": "poligono"},
    {"nome": "ZA (Conama 0-3km)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/0/query", "tipo": "poligono"}
]

BASES_HIDRO = [
    {"nome": "Hidrografia MS (Rios)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/12/query", "tipo": "linha"}
]

BASES_FISCALIZACAO = [
    {"nome": "Embargos IBAMA", "tipo_fonte": "REST", "url": "https://pamgia.ibama.gov.br/server/rest/services/01_Publicacoes_Bases/adm_embargos_ibama_a/MapServer/0/query", "tipo": "poligono"},
    {"nome": "Embargos ICMBio", "tipo_fonte": "WFS", "url": "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows", "layer_name": "ICMBio:embargos_icmbio", "tipo": "poligono"},
    {"nome": "MapBiomas Alerta", "tipo_fonte": "WFS", "url": "https://production.alerta.mapbiomas.org/geoserver/wfs", "layer_name": "mapbiomas-alertas:alert_report", "tipo": "poligono"},
    {"nome": "Focos de Calor (INPE - Ano Atual)", "tipo_fonte": "WFS", "url": "https://queimadas.dgi.inpe.br/queimadas/geoserver/wfs", "layer_name": "bdqueimadas:focos_br_ref", "tipo": "ponto"},
    {"nome": "Áreas Antropizadas (SICAR/Dinamizada)", "tipo_fonte": "REST", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/CAR/Insumos/MapServer/1/query", "tipo": "poligono"},
]

BASES_LICENCAS = [
    {"nome": "Licenças Emitidas (Siriema/IMASUL)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/licencas_ambientais/FeatureServer/16/query", "tipo": "poligono"}
]

# --- BASES OFFLINE / GITHUB ---
BASES_GITHUB = [
    {"nome": "Focos Históricos (INPE - ZIP)", "url": URL_GEOJSON_GITHUB, "tipo_fonte": "ZIP"},
    {"nome": "Hidrografia MS (Offline - ZIP)", "url": URL_HIDRO_OFFLINE, "tipo_fonte": "ZIP"},
    {"nome": "Dados Agrupados (Autex - ZIP)", "url": URL_AUTEX_IBAMA, "tipo_fonte": "ZIP"},
    {"nome": "Dados Convertidos (Parquet)", "url": URL_PARQUET_CONVERTED, "tipo_fonte": "PARQUET"} # <--- NOVA BASE AQUI
]

CATEGORIAS = {
    "Administrativas": BASES_ADMINISTRATIVAS,
    "CAR (Sicar/MS)": BASES_CAR,
    "Restrições Gerais": BASES_GERAIS,
    "Hidrografia (Online)": BASES_HIDRO,
    "Fiscalização": BASES_FISCALIZACAO,
    "Licenças": BASES_LICENCAS,
    "Arquivos GitHub (ZIP/Parquet)": BASES_GITHUB
}

# ==============================================================================
# 2. FUNÇÕES DE EXTRAÇÃO
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rest_wfs_attributes(layer_config):
    """Busca atributos via API (ArcGIS REST ou OGC WFS)."""
    tipo = layer_config.get("tipo_fonte", "REST")
    url = layer_config["url"]
    
    try:
        data_attributes = {}
        # --- LÓGICA REST ---
        if tipo == "REST":
            params = {"where": "1=1", "outFields": "*", "f": "json", "resultRecordCount": 5, "returnGeometry": "false"}
            if not url.endswith("query"): url = url.rstrip("/") + "/query"
            r = requests.get(url, params=params, timeout=15, verify=False)
            if r.status_code == 200:
                features = r.json().get("features", [])
                if features: data_attributes = random.choice(features).get("attributes", {})
                else: return {"AVISO": "Camada vazia."}
            else: return {"ERRO": f"Status: {r.status_code}"}

        # --- LÓGICA WFS ---
        elif tipo == "WFS":
            params = {"service": "WFS", "version": "1.1.0", "request": "GetFeature", "typeName": layer_config.get("layer_name"), "outputFormat": "application/json", "maxFeatures": 5}
            r = requests.get(url, params=params, timeout=30, verify=False)
            if r.status_code == 200:
                try:
                    features = r.json().get("features", [])
                    if features: data_attributes = random.choice(features).get("properties", {})
                    else: return {"AVISO": "WFS vazio."}
                except: return {"ERRO": "JSON inválido."}
            else: return {"ERRO": f"WFS Status: {r.status_code}"}
        
        return data_attributes
    except Exception as e: return {"ERRO": str(e)}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_zip_attributes(url):
    """Baixa ZIP, extrai e lê Shapefile/GeoJSON com Geopandas."""
    try:
        r = requests.get(url, timeout=60, verify=False)
        if r.status_code != 200: return {"ERRO": f"Falha download (Status: {r.status_code})"}
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(io.BytesIO(r.content), 'r') as zf: zf.extractall(temp_dir)
            files = [f for f in os.listdir(temp_dir) if f.endswith(('.shp', '.geojson'))]
            if not files: return {"ERRO": "Nenhum .shp/.geojson no ZIP."}
            
            gdf = gpd.read_file(os.path.join(temp_dir, files[0]))
            if gdf.empty: return {"AVISO": "Arquivo vazio."}
            
            # Amostra e converte para dict seguro
            return {k: str(v) for k, v in gdf.sample(1).iloc[0].drop('geometry', errors='ignore').to_dict().items()}
    except Exception as e: return {"ERRO": f"ZIP falhou: {str(e)}"}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_parquet_attributes(url):
    """Baixa e lê arquivo PARQUET (requer engine pyarrow)."""
    try:
        r = requests.get(url, timeout=60, verify=False)
        if r.status_code != 200: return {"ERRO": f"Falha download (Status: {r.status_code})"}
        
        # Lê o parquet da memória
        with io.BytesIO(r.content) as f:
            df = pd.read_parquet(f)
            
        if df.empty: return {"AVISO": "Parquet vazio."}
        
        # Pega amostra, remove geometria se existir e converte para string
        sample = df.sample(1).iloc[0]
        if 'geometry' in sample: sample = sample.drop('geometry')
        
        return {k: str(v) for k, v in sample.to_dict().items()}
        
    except ImportError:
        return {"ERRO": "Biblioteca 'pyarrow' não instalada. Instale com pip install pyarrow"}
    except Exception as e:
        return {"ERRO": f"Parquet falhou: {str(e)}"}

# ==============================================================================
# 3. INTERFACE STREAMLIT
# ==============================================================================

st.title("🛠️ Wizard de Configuração de Bases Ambientais")
st.markdown("Extração automática de colunas para configuração do sistema.")

if "final_config" not in st.session_state: st.session_state["final_config"] = {}

tabs = st.tabs(list(CATEGORIAS.keys()) + ["💾 Gerar Config Final"])

for i, (cat_name, layers) in enumerate(CATEGORIAS.items()):
    with tabs[i]:
        st.header(cat_name)
        for layer in layers:
            with st.expander(f"📍 {layer['nome']}", expanded=False):
                if st.button("Carregar Amostra", key=f"btn_{layer['nome']}"):
                    st.session_state[f"load_{layer['nome']}"] = True

                if st.session_state.get(f"load_{layer['nome']}", False):
                    with st.spinner("Baixando dados..."):
                        tipo = layer.get("tipo_fonte", "REST")
                        if tipo == "ZIP": amostra = fetch_zip_attributes(layer["url"])
                        elif tipo == "PARQUET": amostra = fetch_parquet_attributes(layer["url"]) # <--- LÓGICA NOVA
                        else: amostra = fetch_rest_wfs_attributes(layer)
                    
                    if "ERRO" in amostra: st.error(amostra["ERRO"])
                    elif "AVISO" in amostra: st.warning(amostra["AVISO"])
                    else:
                        df_data = []
                        saved_conf = st.session_state["final_config"].get(layer["nome"], {})
                        for k, v in amostra.items():
                            df_data.append({
                                "Campo Original": k,
                                "Valor Exemplo": str(v)[:100],
                                "Usar?": k in saved_conf,
                                "Nome no App (Alias)": saved_conf.get(k, "")
                            })
                        
                        edited = st.data_editor(
                            pd.DataFrame(df_data),
                            column_config={
                                "Usar?": st.column_config.CheckboxColumn("Extrair?", width="small"),
                                "Nome no App (Alias)": st.column_config.TextColumn("Nome Amigável", width="large"),
                                "Valor Exemplo": st.column_config.TextColumn("Exemplo", disabled=True),
                                "Campo Original": st.column_config.TextColumn("Campo", disabled=True)
                            },
                            hide_index=True,
                            key=f"ed_{layer['nome']}"
                        )
                        
                        sel = edited[edited["Usar?"] == True]
                        if not sel.empty:
                            mapping = {row["Campo Original"]: (row["Nome no App (Alias)"] or row["Campo Original"].capitalize()) for _, row in sel.iterrows()}
                            st.session_state["final_config"][layer["nome"]] = mapping
                            st.success(f"Salvo: {len(mapping)} colunas.")

with tabs[-1]:
    st.header("JSON Final")
    if st.button("Gerar Código"):
        st.code(f"CONFIG_COLUNAS = {json.dumps(st.session_state['final_config'], indent=4, ensure_ascii=False)}", language="python")
