# --- URL DA SUA BASE GEOJSON NO GITHUB (LINK RAW DA MAIN) ---
URL_GEOJSON_GITHUB = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/focos_historico.zip"
URL_HIDRO_OFFLINE = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/hidrografia_MS.zip"
URL_AUTEX_IBAMA = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/Dados_Agrupados_QGIS.zip"

# URLs para Análise Multitemporal
URL_LANDSAT_2008_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/Imagens/Landsat_5_antes_2008_upscaling8x_v2/ImageServer/exportImage"
URL_SENTINEL_2025_EXPORT = "https://sentinel.arcgis.com/arcgis/rest/services/Sentinel2/ImageServer/exportImage"

# --- LISTAS DE BASES (ESTRUTURA ORIGINAL MANTIDA) ---
# NOTA: As URLs REST foram ajustadas para o endpoint base (sem "/query" no final).

# 1. Apenas para identificação de local
BASES_ADMINISTRATIVAS = [
    {"nome": "Municípios MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/38", "colunas_nome": ["MUNICIPIO", "MUNICIPIO (Município)", "Município", "NOME_MUN", "nm_mun"], "coluna_legis": [], "tipo": "poligono"},
    {"nome": "Biomas em MS", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/lim_biomas_atual/MapServer/0", "colunas_nome": ["Bioma", "nm_bioma"], "coluna_legis": ["info_legis"], "tipo": "poligono"}
]

# 2. Apenas Restrições Ambientais
BASES_GERAIS = [
    {"nome": "Unidades de Conservação", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/UCs_MS_Mosaico/MapServer/0", "colunas_nome": ["Nome UC", "NOME_UC", "NM_UC"], "coluna_legis": ["leis", "LEIS"], "tipo": "poligono"},
    {"nome": "Terras Indígenas", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/4", "colunas_nome": ["terrai_nom", "TERRAI_NOM"], "coluna_legis": ["fase_ti"], "tipo": "poligono"},
    {"nome": "Povos Tradicionais (Quilombolas)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/AGRAER_SERVICOS/Povos_Tradicionais/MapServer/2", "colunas_nome": ["nm_comunid", "NM_COMUNID"], "coluna_legis": ["ob_descric"], "tipo": "poligono"},
    {"nome": "Áreas de Uso Restrito (Dec. 15.661)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/49", "colunas_nome": ["TOPONIMIA", "toponimia"], "coluna_legis": ["CLASSE"], "tipo": "poligono"},
    {"nome": "Áreas Priorit. Banhados", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/52", "colunas_nome": ["CLASSE", "classe"], "coluna_legis": ["leis"], "tipo": "poligono"},
    {"nome": "Corredores Ecológicos do Pantanal", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/Corredores_Ecológicos_Pantanal/MapServer/0", "colunas_nome": ["corredor", "CORREDOR", "nome"], "coluna_legis": ["leis"], "tipo": "poligono"},
    {"nome": "Área de Entorno 0-3 Km (Rio Taquari)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/48", "colunas_nome": ["FID", "gid"], "coluna_legis": [], "tipo": "poligono"},
    {"nome": "Zona de Amortecimento (Estaduais)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/2", "colunas_nome": ["NOME_UC", "nome_uc"], "coluna_legis": ["leis"], "tipo": "poligono"},
    {"nome": "ZA (Conama 0-2km)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/1", "colunas_nome": ["NOME", "nome"], "coluna_legis": ["FAIXA"], "tipo": "poligono"},
    {"nome": "ZA (Conama 0-3km)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/0", "colunas_nome": ["NOME", "nome"], "coluna_legis": ["FAIXA"], "tipo": "poligono"}
]

BASES_HIDRO = [
    {"nome": "Hidrografia MS (Rios)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/12", "colunas_nome": ["NOME", "nome", "Nome"], "coluna_legis": ["REGIME", "regime"], "tipo": "linha"}
]

BASES_FISCALIZACAO = [
    {"nome": "Embargos IBAMA", "tipo_fonte": "REST", "url": "https://pamgia.ibama.gov.br/server/rest/services/01_Publicacoes_Bases/adm_embargos_ibama_a/MapServer/0", "colunas_nome": ["num_tad", "NUM_TAD"], "tipo": "poligono"},
    {"nome": "Embargos ICMBio", "tipo_fonte": "WFS", "url": "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows", "layer_name": "ICMBio:embargos_icmbio", "colunas_nome": ["numero_embargo", "numero_emb"], "tipo": "poligono"},
    {"nome": "MapBiomas Alerta", "tipo_fonte": "WFS", "url": "https://production.alerta.mapbiomas.org/geoserver/wfs", "layer_name": "mapbiomas-alertas:alert_report", "colunas_nome": ["alert_code", "alerta_id"], "tipo": "poligono"},
    {"nome": "Focos de Calor (INPE - Ano Atual)", "tipo_fonte": "WFS", "url": "https://queimadas.dgi.inpe.br/queimadas/geoserver/wfs", "layer_name": "bdqueimadas:focos_br_ref", "colunas_nome": ["data_pas", "satelite"], "tipo": "ponto"},
    {"nome": "Áreas Antropizadas (SICAR/Dinamizada)", "tipo_fonte": "REST", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/CAR/Insumos/MapServer/1", "colunas_nome": ["Class_Name", "CLASS", "OBJECTID"], "tipo": "poligono"},
]

BASES_LICENCAS = [
    {"nome": "Licenças Emitidas (Siriema/IMASUL)", "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/licencas_ambientais/FeatureServer/16", "colunas_nome": ["num_processo", "processo", "n_processo", "emp_id"], "coluna_legis": ["atividade", "desc_ativ", "tipologia"], "tipo": "poligono"}
]

# --- DICIONÁRIO CONSOLIDADO PARA O ASSISTENTE DE CONFIGURAÇÃO ---
TODAS_AS_BASES = {
    "Administrativas": BASES_ADMINISTRATIVAS,
    "Restrições Gerais": BASES_GERAIS,
    "Hidrografia": BASES_HIDRO,
    "Fiscalização & Alertas": BASES_FISCALIZACAO,
    "Licenciamento": BASES_LICENCAS
}

URL_DECLIVIDADE_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/Imagens/fusao_declividade_graus/ImageServer/exportImage"
URL_HIDRO_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/export"
