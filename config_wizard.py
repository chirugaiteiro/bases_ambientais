import streamlit as st
import requests
import pandas as pd
import random
import json

# ==============================================================================
# 1. DADOS DE CONFIGURAÇÃO (Copiados do seu arquivo original)
# ==============================================================================

BASES_ADMINISTRATIVAS = [
    {"nome": "Municípios MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/38/query", "tipo": "poligono"},
    {"nome": "Biomas em MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/lim_biomas_atual/MapServer/0/query", "tipo": "poligono"}
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
    {"nome": "CARMS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_lim_propriedade/FeatureServer/8/query", "tipo": "poligono"}
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

CATEGORIAS = {
    "Administrativas": BASES_ADMINISTRATIVAS,
    "Restrições Gerais": BASES_GERAIS,
    "Hidrografia": BASES_HIDRO,
    "Fiscalização": BASES_FISCALIZACAO,
    "Licenças": BASES_LICENCAS
}

# ==============================================================================
# 2. FUNÇÕES DE EXTRAÇÃO
# ==============================================================================

@st.cache_data(ttl=3600)
def fetch_sample_attributes(layer_config):
    """Tenta buscar uma feição aleatória e retorna suas chaves (colunas) e valores."""
    tipo = layer_config.get("tipo_fonte", "REST") # Default para ArcGIS REST
    url = layer_config["url"]
    
    try:
        data_attributes = {}
        
        # --- LÓGICA PARA ARCGIS REST ---
        if tipo == "REST":
            params = {
                "where": "1=1",
                "outFields": "*",
                "f": "json",
                "resultRecordCount": 5, # Pega 5 para variar
                "returnGeometry": "false"
            }
            # Ajuste para urls que não terminam em /query mas o config tem /query
            if not url.endswith("query"):
                if url.endswith("/"): url = url + "query"
                else: url = url + "/query"
                
            r = requests.get(url, params=params, timeout=10, verify=False) # verify=False pois alguns do gov tem SSL ruim
            if r.status_code == 200:
                features = r.json().get("features", [])
                if features:
                    feat = random.choice(features) # Escolhe uma aleatória das 5
                    data_attributes = feat.get("attributes", {})

        # --- LÓGICA PARA WFS (OGC) ---
        elif tipo == "WFS":
            layer_name = layer_config.get("layer_name")
            params = {
                "service": "WFS",
                "version": "1.1.0", # ou 2.0.0
                "request": "GetFeature",
                "typeName": layer_name,
                "outputFormat": "application/json",
                "maxFeatures": 5
            }
            r = requests.get(url, params=params, timeout=15)
            if r.status_code == 200:
                geojson = r.json()
                features = geojson.get("features", [])
                if features:
                    feat = random.choice(features)
                    data_attributes = feat.get("properties", {})
        
        return data_attributes

    except Exception as e:
        return {"ERRO": str(e)}

# ==============================================================================
# 3. INTERFACE STREAMLIT
# ==============================================================================

st.set_page_config(layout="wide", page_title="Configurador de Bases Mutum")
st.title("🛠️ Wizard de Configuração de Bases Ambientais")
st.markdown("Selecione as colunas que deseja extrair de cada base e dê nomes amigáveis para o aplicativo final.")

# Armazenar as configurações finais
if "final_config" not in st.session_state:
    st.session_state["final_config"] = {}

tabs = st.tabs(list(CATEGORIAS.keys()) + ["💾 Gerar Arquivo Final"])

# Iterar sobre as abas (Categorias)
for i, (cat_name, layers) in enumerate(CATEGORIAS.items()):
    with tabs[i]:
        st.header(f"Bases: {cat_name}")
        
        for layer in layers:
            with st.expander(f"📍 {layer['nome']}", expanded=False):
                col1, col2 = st.columns([1, 2])
                
                # Buscar dados (Amostra)
                amostra = fetch_sample_attributes(layer)
                
                if "ERRO" in amostra:
                    st.error(f"Não foi possível conectar: {amostra['ERRO']}")
                    continue
                
                if not amostra:
                    st.warning("Conectou, mas a tabela veio vazia.")
                    continue

                # Preparar DataFrame para edição
                df_data = []
                # Tenta recuperar config salva anteriormente se existir na sessão
                saved_conf = st.session_state["final_config"].get(layer["nome"], {})
                
                for k, v in amostra.items():
                    # Checkbox marcado se já estiver salvo ou se for uma coluna comum (opcional)
                    is_checked = k in saved_conf
                    # Nome amigável salvo ou vazio
                    friendly_name = saved_conf.get(k, "")
                    
                    df_data.append({
                        "Campo Original": k,
                        "Valor Exemplo": str(v),
                        "Usar?": is_checked,
                        "Nome no App (Alias)": friendly_name
                    })
                
                df = pd.DataFrame(df_data)

                # Editor de Dados
                st.info("Marque 'Usar?' nas colunas desejadas e digite o rótulo em 'Nome no App'.")
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Usar?": st.column_config.CheckboxColumn(
                            "Extrair?",
                            help="Se marcado, esta coluna será exibida no relatório do Mutum",
                            default=False,
                        ),
                        "Nome no App (Alias)": st.column_config.TextColumn(
                            "Nome Amigável",
                            help="Ex: De 'nm_prop' para 'Nome da Propriedade'",
                            width="medium"
                        ),
                        "Valor Exemplo": st.column_config.TextColumn(
                            "Exemplo Real",
                            disabled=True
                        ),
                        "Campo Original": st.column_config.TextColumn(
                            "Campo Original",
                            disabled=True
                        )
                    },
                    hide_index=True,
                    key=f"editor_{layer['nome']}"
                )

                # Processar as edições e salvar na sessão
                # Filtra apenas o que foi marcado como True
                selected_rows = edited_df[edited_df["Usar?"] == True]
                
                if not selected_rows.empty:
                    # Cria dicionario {campo_original: nome_amigavel}
                    # Se nome amigável estiver vazio, usa o nome original capitalizado
                    mapping = {}
                    for _, row in selected_rows.iterrows():
                        orig = row["Campo Original"]
                        alias = row["Nome no App (Alias)"]
                        if not alias or alias.strip() == "":
                            alias = orig
                        mapping[orig] = alias
                    
                    st.session_state["final_config"][layer["nome"]] = mapping
                    st.success(f"{len(mapping)} campos configurados para '{layer['nome']}'.")
                else:
                    # Se desmarcou tudo, remove da config
                    if layer["nome"] in st.session_state["final_config"]:
                        del st.session_state["final_config"][layer["nome"]]

# Aba de Exportação
with tabs[-1]:
    st.header("Resultado da Configuração")
    st.markdown("Copie o dicionário abaixo e substitua a lógica de colunas no seu script principal ou crie um arquivo `colunas_config.json`.")
    
    if st.button("Gerar JSON de Configuração"):
        json_output = json.dumps(st.session_state["final_config"], indent=4, ensure_ascii=False)
        st.code(json_output, language="json")
        
        st.markdown("### Como usar no código Python:")
        st.code(f"""
# Exemplo de uso no seu script de análise
CONFIG_COLUNAS = {json_output}

def processar_camada(nome_camada, atributos_brutos):
    mapa = CONFIG_COLUNAS.get(nome_camada)
    if not mapa:
        return atributos_brutos # Retorna tudo se não tiver config
    
    dados_limpos = {{}}
    for campo_orig, alias in mapa.items():
        if campo_orig in atributos_brutos:
            dados_limpos[alias] = atributos_brutos[campo_orig]
            
    return dados_limpos
        """, language="python")
