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

# Silencia o aviso de "InsecureRequestWarning" (necessário para .gov.br com SSL inválido)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==============================================================================
# 1. DADOS DE CONFIGURAÇÃO (BASEADOS NO SEU CONFIG.PY)
# ==============================================================================

# --- URL DA SUA BASE GEOJSON NO GITHUB ---
URL_GEOJSON_GITHUB = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/focos_historico.zip"
URL_HIDRO_OFFLINE = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/hidrografia_MS.zip"
URL_AUTEX_IBAMA = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/Dados_Agrupados_QGIS.zip"

# --- LISTAS DE BASES ---

BASES_ADMINISTRATIVAS = [
    {"nome": "Municípios MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/38/query", "tipo": "poligono"},
    {"nome": "Biomas em MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/lim_biomas_atual/MapServer/0/query", "tipo": "poligono"}
]

# --- NOVAS BASES: CAR (IMASUL) ---
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

# --- BASES OFFLINE (ZIP GITHUB) ---
BASES_ZIP_GITHUB = [
    {"nome": "Focos Históricos (INPE - GitHub)", "url": URL_GEOJSON_GITHUB, "tipo_fonte": "ZIP"},
    {"nome": "Hidrografia MS (Offline - GitHub)", "url": URL_HIDRO_OFFLINE, "tipo_fonte": "ZIP"},
    {"nome": "Dados Agrupados (Autex - GitHub)", "url": URL_AUTEX_IBAMA, "tipo_fonte": "ZIP"}
]

# Agrupamento para as abas
CATEGORIAS = {
    "Administrativas": BASES_ADMINISTRATIVAS,
    "CAR (Sicar/MS)": BASES_CAR,  # <--- NOVA CATEGORIA ADICIONADA AQUI
    "Restrições Gerais": BASES_GERAIS,
    "Hidrografia (Online)": BASES_HIDRO,
    "Fiscalização": BASES_FISCALIZACAO,
    "Licenças": BASES_LICENCAS,
    "Arquivos ZIP (GitHub)": BASES_ZIP_GITHUB
}

# ==============================================================================
# 2. FUNÇÕES DE EXTRAÇÃO
# ==============================================================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_rest_wfs_attributes(layer_config):
    """
    Busca atributos via API (ArcGIS REST ou OGC WFS).
    Inclui verify=False para ignorar erros de SSL do governo.
    """
    tipo = layer_config.get("tipo_fonte", "REST")
    url = layer_config["url"]
    
    try:
        data_attributes = {}
        
        # --- LÓGICA PARA ARCGIS REST ---
        if tipo == "REST":
            params = {
                "where": "1=1",
                "outFields": "*",
                "f": "json",
                "resultRecordCount": 5,
                "returnGeometry": "false"
            }
            # Garante que termina com /query se não tiver
            if not url.endswith("query"):
                url = url.rstrip("/") + "/query"
                
            r = requests.get(url, params=params, timeout=15, verify=False)
            if r.status_code == 200:
                data = r.json()
                features = data.get("features", [])
                if features:
                    feat = random.choice(features)
                    data_attributes = feat.get("attributes", {})
                else:
                    return {"AVISO": "Camada vazia ou sem acesso público."}
            else:
                 return {"ERRO": f"Status code: {r.status_code}"}

        # --- LÓGICA PARA WFS (OGC) ---
        elif tipo == "WFS":
            layer_name = layer_config.get("layer_name")
            params = {
                "service": "WFS",
                "version": "1.1.0", 
                "request": "GetFeature",
                "typeName": layer_name,
                "outputFormat": "application/json",
                "maxFeatures": 5
            }
            r = requests.get(url, params=params, timeout=30, verify=False)
            if r.status_code == 200:
                try:
                    geojson = r.json()
                    features = geojson.get("features", [])
                    if features:
                        feat = random.choice(features)
                        data_attributes = feat.get("properties", {})
                    else:
                        return {"AVISO": "WFS retornou lista vazia."}
                except ValueError:
                    return {"ERRO": "Resposta do WFS não é um JSON válido."}
            else:
                return {"ERRO": f"Status WFS: {r.status_code}"}
        
        return data_attributes

    except Exception as e:
        return {"ERRO": str(e)}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_zip_attributes(url):
    """
    Baixa ZIP, descompacta na memória e lê com Geopandas.
    """
    try:
        # Baixar o conteúdo
        response = requests.get(url, timeout=60, verify=False)
        if response.status_code != 200:
            return {"ERRO": f"Falha ao baixar ZIP (Status: {response.status_code})"}
        
        # Descompactar na memória
        zip_file_object = io.BytesIO(response.content)
        
        # Criar diretório temporário para o Geopandas ler
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(zip_file_object, 'r') as zf:
                zf.extractall(temp_dir)
                
                # Procurar arquivos .shp ou .geojson
                valid_files = [
                    f for f in os.listdir(temp_dir) 
                    if f.endswith('.shp') or f.endswith('.geojson')
                ]
                
                if not valid_files:
                    return {"ERRO": "Nenhum arquivo .shp ou .geojson encontrado no ZIP."}
                
                # Ler o primeiro encontrado
                file_path = os.path.join(temp_dir, valid_files[0])
                gdf = gpd.read_file(file_path)
                
                if gdf.empty:
                    return {"AVISO": "Arquivo geográfico vazio."}
                
                # Pegar amostra (remove geometria para exibir só atributos)
                amostra = gdf.sample(n=1).iloc[0].drop('geometry', errors='ignore').to_dict()
                
                # Converter tipos não serializáveis (ex: numpy int)
                amostra_limpa = {}
                for k, v in amostra.items():
                    try:
                        # Tenta converter para string se for complexo
                        amostra_limpa[k] = str(v)
                    except:
                        amostra_limpa[k] = "Valor complexo"
                        
                return amostra_limpa

    except Exception as e:
        return {"ERRO": f"Processamento ZIP falhou: {str(e)}"}

# ==============================================================================
# 3. INTERFACE STREAMLIT
# ==============================================================================

st.title("🛠️ Wizard de Configuração de Bases Ambientais")
st.markdown("""
Esta ferramenta conecta nas bases do seu arquivo `config.py` (Online e GitHub), 
baixa amostras reais e permite que você defina quais colunas importar.
""")

# Inicializar estado
if "final_config" not in st.session_state:
    st.session_state["final_config"] = {}

# Criar abas
tabs = st.tabs(list(CATEGORIAS.keys()) + ["💾 Gerar Config Final"])

# Loop principal para gerar UI
for i, (cat_name, layers) in enumerate(CATEGORIAS.items()):
    with tabs[i]:
        st.header(f"Bases: {cat_name}")
        
        for layer in layers:
            with st.expander(f"📍 {layer['nome']}", expanded=False):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.caption(f"Fonte: {layer.get('tipo_fonte', 'REST')}")
                    if st.button("Carregar Amostra", key=f"btn_{layer['nome']}"):
                        st.session_state[f"load_{layer['nome']}"] = True

                # Lógica de Carregamento
                if st.session_state.get(f"load_{layer['nome']}", False):
                    with st.spinner("Conectando e baixando dados..."):
                        tipo = layer.get("tipo_fonte", "REST")
                        
                        if tipo == "ZIP":
                            amostra = fetch_zip_attributes(layer["url"])
                        else:
                            amostra = fetch_rest_wfs_attributes(layer)
                    
                    # Verificação de erros
                    if "ERRO" in amostra:
                        st.error(amostra["ERRO"])
                    elif "AVISO" in amostra:
                        st.warning(amostra["AVISO"])
                    elif not amostra:
                        st.warning("Nenhum atributo retornado.")
                    else:
                        # Preparar DataFrame para edição
                        df_data = []
                        saved_conf = st.session_state["final_config"].get(layer["nome"], {})
                        
                        for k, v in amostra.items():
                            is_checked = k in saved_conf
                            friendly_name = saved_conf.get(k, "")
                            
                            df_data.append({
                                "Campo Original": k,
                                "Valor Exemplo": str(v)[:100], # Corta strings muito longas
                                "Usar?": is_checked,
                                "Nome no App (Alias)": friendly_name
                            })
                        
                        df = pd.DataFrame(df_data)

                        st.markdown("##### Selecione as colunas desejadas:")
                        edited_df = st.data_editor(
                            df,
                            column_config={
                                "Usar?": st.column_config.CheckboxColumn(
                                    "Extrair?",
                                    default=False,
                                    width="small"
                                ),
                                "Nome no App (Alias)": st.column_config.TextColumn(
                                    "Nome Amigável (Label)",
                                    width="large",
                                    help="Nome que aparecerá para o usuário final"
                                ),
                                "Valor Exemplo": st.column_config.TextColumn(
                                    "Exemplo Real",
                                    disabled=True,
                                    width="medium"
                                ),
                                "Campo Original": st.column_config.TextColumn(
                                    "Campo Original",
                                    disabled=True,
                                    width="medium"
                                )
                            },
                            hide_index=True,
                            key=f"editor_{layer['nome']}"
                        )

                        # Salvar alterações em tempo real
                        selected_rows = edited_df[edited_df["Usar?"] == True]
                        if not selected_rows.empty:
                            mapping = {}
                            for _, row in selected_rows.iterrows():
                                orig = row["Campo Original"]
                                alias = row["Nome no App (Alias)"]
                                if not alias or alias.strip() == "":
                                    alias = orig.capitalize() # Default se vazio
                                mapping[orig] = alias
                            
                            st.session_state["final_config"][layer["nome"]] = mapping
                            st.success(f"✅ Configuração salva: {len(mapping)} campos selecionados.")
                        else:
                            if layer["nome"] in st.session_state["final_config"]:
                                del st.session_state["final_config"][layer["nome"]]

# Aba de Exportação
with tabs[-1]:
    st.header("Resultado da Configuração")
    st.markdown("Este JSON contém o mapeamento de **Campo Original -> Nome Amigável** para todas as bases configuradas.")
    
    if st.button("Gerar Código Python Final"):
        config_dict = st.session_state["final_config"]
        
        json_str = json.dumps(config_dict, indent=4, ensure_ascii=False)
        
        st.markdown("### Copie e cole no seu `config.py` ou crie um `colunas.json`:")
        st.code(f"""
# Dicionário de Configuração de Colunas (Gerado pelo Wizard)
CONFIG_COLUNAS = {json_str}
        """, language="python")
