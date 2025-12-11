# utils.py
import streamlit as st
import pandas as pd
import requests
import json
import datetime
import random
import concurrent.futures
from shapely.geometry import shape, Polygon, LineString, MultiLineString
from shapely.ops import unary_union, transform
import geopandas as gpd
import urllib3
import tempfile
import os
import zipfile
import fiona

# O Mutum (mutum_v1.py) ainda importa config.py, mas aqui usaremos a estrutura de dicionário para BASES
# Se você quiser que o utils.py também importe o config, adicione:
# from config import BASES_ADMINISTRATIVAS, BASES_GERAIS, BASES_HIDRO, BASES_FISCALIZACAO, BASES_LICENCAS

# Configuração (necessária para as funções de consulta)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

# --- FUNÇÕES AUXILIARES DE CONVERSÃO/GEOMETRIA ---

def converter_data_segura(data_str):
    """Tenta converter string para datetime de forma resiliente."""
    if not data_str or data_str in ["N/D", "-", "nan", "None"]:
        return None
    try:
        # Tenta formato DD/MM/YYYY (comum no Brasil)
        return pd.to_datetime(data_str, dayfirst=True)
    except:
        try:
            # Tenta formato universal YYYY-MM-DD
            return pd.to_datetime(data_str)
        except:
            return None

def gerar_cor_aleatoria():
    """Gera uma cor hexadecimal aleatória."""
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    
def force_2d(geometry):
    try:
        if geometry.has_z:
            return transform(lambda x, y, z=None: (x, y), geometry)
        return geometry
    except:
        return geometry

def buscar_valor_inteligente(attrs, lista_tentativas):
    if not attrs: return "N/D"
    attrs_lower = {k.lower(): v for k, v in attrs.items()}
    for chave in lista_tentativas:
        chave_low = chave.lower()
        if chave_low in attrs_lower and attrs_lower[chave_low]:
            val = attrs_lower[chave_low]
            if isinstance(val, (int, float)) and val > 100000000000:
                try: return datetime.datetime.fromtimestamp(val/1000).strftime('%d/%m/%Y')
                except: return str(val)
            return str(val)
    for key, val in attrs_lower.items():
        if ('nome' in key or 'nm_' in key) and val: return str(val)
    return ""

def parse_float_br(valor_str):
    try:
        if isinstance(valor_str, (int, float)): return float(valor_str)
        return float(valor_str.replace('.', '').replace(',', '.'))
    except: return 0.0

# --- FUNÇÕES DE CONSULTA API ---

def consultar_api_imasul(url, geometry_json, geometry_type):
    """
    Consulta API REST para filtro espacial.
    NOTA: Adiciona '/query' à URL base para acessar o endpoint, conforme ajuste do config.py.
    """
    url_query = f"{url}/query" if not url.endswith('/query') else url
    params = {'f': 'json', 'geometry': geometry_json, 'geometryType': geometry_type, 'spatialRel': 'esriSpatialRelIntersects', 'outFields': '*', 'returnGeometry': 'true', 'outSR': '31981'}
    try:
        # Aumentei o timeout para dar mais resiliência em APIs lentas
        response = requests.post(url_query, data=params, timeout=45) 
        return response.json()
    except: return None

def consultar_wfs_icmbio(url, layer_name, bbox_list):
    bbox_str = f"{bbox_list[0]},{bbox_list[1]},{bbox_list[2]},{bbox_list[3]}"
    params = {"service": "WFS", "version": "1.0.0", "request": "GetFeature", "typeName": layer_name, "outputFormat": "application/json", "srsName": "EPSG:4674", "bbox": f"{bbox_str},EPSG:4674"}
    try:
        response = requests.get(url, params=params, timeout=45)
        if response.status_code == 200: return response.json()
        else: return None
    except: return None


# --- NOVAS FUNÇÕES: ASSISTENTE DE CONFIGURAÇÃO (NÃO-ESPACIAL) ---

def consultar_api_amostra(url):
    """Consulta a API REST (ArcGIS Feature/MapServer) para obter uma amostra de 1 feição."""
    # Parâmetros para buscar 1 registro sem filtro espacial.
    # Adicionamos '/query' ao final da URL, se necessário, para garantir que estamos no endpoint correto
    url_query = f"{url}/query" if not url.endswith('/query') else url 
    params = {
        'f': 'json', 
        'where': '1=1', # Filtro não-espacial: 1=1
        'resultRecordCount': 1, # Limita a 1 feição
        'outFields': '*', # Retorna todos os campos
        'returnGeometry': 'false' # Não precisamos da geometria completa
    }
    try:
        response = requests.get(url_query, params=params, timeout=15) 
        response.raise_for_status() # Lança exceção para erros HTTP
        return response.json()
    except Exception as e: 
        return {"error": str(e), "url": url_query}

def consultar_wfs_amostra(url, layer_name):
    """Consulta WFS para obter uma amostra de 1 feição."""
    params = {
        "service": "WFS", 
        "version": "1.0.0", 
        "request": "GetFeature", 
        "typeName": layer_name, 
        "outputFormat": "application/json", 
        "maxFeatures": 1 # Limita a 1 feição
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        if response.status_code == 200: return response.json()
        else: return {"error": f"Status code: {response.status_code}"}
    except Exception as e: 
        return {"error": str(e)}

def extrair_atributos_amostra(response, base_tipo):
    """Extrai uma lista simples de atributos do JSON de resposta (REST ou WFS)."""
    if response is None or response.get('error'):
        return None
        
    atributos = {}
    
    # Lógica para REST (ArcGIS FeatureServer/MapServer)
    if base_tipo == 'REST' and 'features' in response and len(response['features']) > 0:
        attrs = response['features'][0].get('attributes', {})
        for k, v in attrs.items():
            # Tenta converter timestamp para data (ArcGIS FeatureServer)
            if isinstance(v, (int, float)) and k.lower().startswith('data'):
                try: 
                    v = datetime.datetime.fromtimestamp(v/1000).strftime('%d/%m/%Y %H:%M')
                except:
                    pass
            atributos[k] = str(v) if v is not None else "N/D"
        return atributos
    
    # Lógica para WFS (GeoJSON)
    elif base_tipo == 'WFS' and 'features' in response and len(response['features']) > 0:
        attrs = response['features'][0].get('properties', {})
        for k, v in attrs.items():
            atributos[k] = str(v) if v is not None else "N/D"
        return atributos
    
    return None

def processar_amostra_base(base):
    """Função auxiliar para coletar atributos de uma única base."""
    tipo_fonte = base.get('tipo_fonte', 'REST')
    url = base['url']
    
    resp = None
    if tipo_fonte == 'REST':
        resp = consultar_api_amostra(url)
        atributos = extrair_atributos_amostra(resp, 'REST')
    elif tipo_fonte == 'WFS':
        layer_name = base.get('layer_name')
        if not layer_name:
            return {"erro": "Layer name faltando para WFS.", "atributos": None, "tipo_fonte": tipo_fonte}
        resp = consultar_wfs_amostra(url, layer_name)
        atributos = extrair_atributos_amostra(resp, 'WFS')
    
    if atributos:
        # Adiciona o tipo de fonte para ajudar no debug
        return {"erro": None, "atributos": atributos, "tipo_fonte": tipo_fonte}
    else:
        erro_msg = resp.get('error', 'Resposta vazia ou erro desconhecido da API.') if resp else 'Nenhuma resposta da API.'
        return {"erro": erro_msg, "atributos": None, "tipo_fonte": tipo_fonte}

def coletar_atributos_de_todas_bases(bases_dict_list):
    """Itera sobre uma lista de bases e coleta os atributos de amostra, retornando um dict."""
    bases_com_atributos = {}
    
    # Usamos ThreadPoolExecutor para rodar as consultas em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_base = {}
        
        # Filtra e prepara a lista de bases (apenas REST/WFS)
        lista_bases_preparadas = []
        for base in bases_dict_list:
             tipo = base.get('tipo_fonte', 'REST')
             if tipo in ['REST', 'WFS']:
                 lista_bases_preparadas.append(base)
        
        for base in lista_bases_preparadas:
            future_to_base[executor.submit(processar_amostra_base, base)] = base['nome']

        for future in concurrent.futures.as_completed(future_to_base):
            base_nome = future_to_base[future]
            try:
                res = future.result()
                bases_com_atributos[base_nome] = res
            except Exception as e:
                bases_com_atributos[base_nome] = {"erro": f"Exceção ao processar: {str(e)}", "atributos": None}

    return bases_com_atributos


# --- FUNÇÃO DE CARGA DE BASE ESPECIAL (MIGRADA DO MAIN) ---
# No utils.py

def carregar_autex_ibama(url, gdf_imovel):
    """
    Baixa ZIP do Sinaflor/IBAMA, lê GeoJSON/SHP e filtra pontos.
    Versão com diagnóstico de erro.
    """
    resultados = []
    camadas = []
    
    # Truque anti-cache
    url_no_cache = f"{url}?v={random.randint(1, 999999)}"
    
    try:
        # 1. Download
        response = requests.get(url_no_cache, timeout=60) # Timeout aumentado
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name

        gdf_pontos = None
        
        # Tenta ler o ZIP
        try:
            # Opção B (Manual): Inspeciona o ZIP para decidir entre GeoJSON ou SHP
            with zipfile.ZipFile(tmp_path, 'r') as z:
                lista_arquivos = z.namelist()
                # Procura GeoJSON
                arquivos_geojson = [f for f in lista_arquivos if f.lower().endswith('.geojson') or f.lower().endswith('.json')]
                
                if arquivos_geojson:
                    # Lê o primeiro GeoJSON encontrado
                    gdf_pontos = gpd.read_file(f"zip://{tmp_path}!{arquivos_geojson[0]}")
                elif any(f.lower().endswith('.shp') for f in lista_arquivos):
                    # Lê Shapefile genérico no ZIP
                    gdf_pontos = gpd.read_file(f"zip://{tmp_path}")
                else:
                    st.warning("⚠️ O arquivo ZIP da AUTEX não contém .shp ou .geojson válidos.")
                    return [], []

        except Exception as e_read:
            st.error(f"Erro ao ler o arquivo geográfico dentro do ZIP: {e_read}")
            return [], []
        
        finally:
            # Limpeza do arquivo temporário
            try: os.remove(tmp_path)
            except: pass

        if gdf_pontos is None or gdf_pontos.empty:
            return [], []

        # 2. Processamento Geoespacial
        # Força CRS 4674 (SIRGAS 2000) se não tiver
        if gdf_pontos.crs is None: 
            gdf_pontos.set_crs(epsg=4674, inplace=True)
        else: 
            gdf_pontos = gdf_pontos.to_crs(epsg=4674)

        gdf_imovel_wgs84 = gdf_imovel.to_crs(epsg=4674)
        
        # Intersecção Espacial
        pontos_no_imovel = gpd.sjoin(gdf_pontos, gdf_imovel_wgs84, how="inner", predicate="intersects")

        if pontos_no_imovel.empty:
            # Descomente a linha abaixo se quiser confirmar que o arquivo foi lido mas não cruzou
            # st.info(f"Arquivo AUTEX lido com {len(gdf_pontos)} registros, mas nenhum caiu no imóvel.")
            return [], []

        # 3. Formatação dos Resultados
        # Colunas esperadas (ajuste conforme seu arquivo real se mudou no QGIS)
        for idx, row in pontos_no_imovel.iterrows():
            nro_autex = str(row.get('NRO_DA_AUTORIZACAO_ORIGINAL', row.get('NRO_AUT', 'S/N'))) # Tenta nome curto tb
            detentor = str(row.get('NOME_RAZAO_SOCIAL_DO_DETENTOR', row.get('DETENTOR', '')))
            situacao = str(row.get('SITUACAO_ATUAL', row.get('SITUACAO', '')))
            
            nome_origem = str(row.get('NOME_DA_ORIGEM', '-'))
            volume = str(row.get('RESUMO_VOLUME', '-'))
            
            validade_raw = row.get('DATA_DE_VALIDADE_DA_AUTEX', row.get('VALIDADE'))
            validade = converter_data_segura(str(validade_raw))
            str_validade = validade.strftime('%d/%m/%Y') if hasattr(validade, 'strftime') else str(validade)

            resultados.append({
                "Base": "IBAMA/Sinaflor (AUTEX)",
                "Identificação": nro_autex,
                "nome": f"AUTEX: {nro_autex}",
                "tipo": "ponto",
                "Detalhes": f"{volume} - {detentor}",
                "Área (ha)": "Ponto", 
                "Status": "Vigente" if situacao == "VIGENTE" else situacao,
                "Extra": {
                    "NumLicenca": nro_autex,
                    "Vencimento": str_validade,
                    "Situacao": situacao,
                    "Detentor": detentor,      
                    "NomeOrigem": nome_origem,
                    "Volume": volume,
                    "Emissao": str(row.get('ANO', '-'))
                }
            })

        # 4. Tratamento para JSON (Mapa)
        gdf_mapa = pontos_no_imovel.copy()
        # Converte datas para string para evitar erro no JSON
        for col in gdf_mapa.columns:
            if pd.api.types.is_datetime64_any_dtype(gdf_mapa[col]) or gdf_mapa[col].dtype == 'object':
                gdf_mapa[col] = gdf_mapa[col].astype(str)

        geojson_str = gdf_mapa.to_crs(epsg=4326).to_json()
        camadas.append({
            "nome": f"AUTEX: {len(pontos_no_imovel)} un.",
            "geojson": json.loads(geojson_str),
            "tipo": "ponto",
            "cor": "#FF00FF"
        })

        return resultados, camadas

    except Exception as e:
        st.error(f"Erro CRÍTICO ao carregar base AUTEX: {str(e)}")
        return [], []
        
# --- FUNÇÕES DE PROCESSAMENTO GEOESPACIAL E PARALELO ---

def processar_uma_base(base, dados_imovel):
    """Processa uma única base de dados, realiza a intersecção e formata os resultados."""
    resultados_parcial = []
    camadas_parcial = []
    
    geom_utm_imovel = dados_imovel['geom_utm']
    area_imovel = dados_imovel['area_ha']
    
    resp = None
    if base.get('tipo_fonte') == 'WFS':
        resp = consultar_wfs_icmbio(base['url'], base['layer_name'], dados_imovel['bounds_4674'])
    else:
        if base['tipo'] == 'ponto': payload = dados_imovel['json_point']; gtype = 'esriGeometryPoint'
        else: payload = dados_imovel['json_poly']; gtype = 'esriGeometryPolygon'
        # Usa a função ajustada que anexa /query
        resp = consultar_api_imasul(base['url'], payload, gtype)
    
    if resp and 'features' in resp and len(resp['features']) > 0:
        agrupamento = {} 
        for feat in resp['features']:
            attrs = feat.get('attributes') or feat.get('properties')
            
            # NOTA: O nome do grupo precisa ser gerado antes do break para pontos
            if base['tipo'] == 'ponto':
                 # Para pontos, usa um nome único/aleatório
                 nome_grupo = f"{base['nome']}_{buscar_valor_inteligente(attrs, base['colunas_nome'])}"
                 if nome_grupo == f"{base['nome']}_": nome_grupo = f"{base['nome']}_{random.randint(0,1000000)}"
            else:
                 # Para linhas/polígonos, usa o nome principal para agrupar
                 nome_grupo = buscar_valor_inteligente(attrs, base['colunas_nome'])
                 if not nome_grupo or nome_grupo == "N/D": nome_grupo = "Não identificado"
            
            poly_base = None
            try:
                if base['tipo'] == 'ponto': poly_base = shape(feat['geometry'])
                elif base.get('tipo_fonte') == 'WFS': poly_base = shape(feat['geometry'])
                elif 'geometry' in feat and 'rings' in feat['geometry']:
                    # API REST (Polígono)
                    partes = [Polygon(a) for a in feat['geometry']['rings']]
                    poly_base = unary_union(partes)
                elif 'geometry' in feat and 'paths' in feat['geometry']:
                    # API REST (Linha)
                    partes = [LineString(a) for a in feat['geometry']['paths']]
                    poly_base = unary_union(partes)
            except: continue

            if poly_base:
                if nome_grupo not in agrupamento: agrupamento[nome_grupo] = {'geoms': [], 'attrs': attrs}
                agrupamento[nome_grupo]['geoms'].append(poly_base)

        for nome_grupo, dados_grupo in agrupamento.items():
            attrs = dados_grupo['attrs']
            try:
                geom_unificada_base = unary_union(dados_grupo['geoms'])
                if not geom_unificada_base.is_valid: geom_unificada_base = geom_unificada_base.buffer(0)
            except: continue

            legis = "-"
            detalhes_extras = {}
            
            # --- EXTRAÇÃO DE DETALHES (USANDO COLUNAS_LEGIS CONFIGURADAS) ---
            # Se a lista coluna_legis estiver preenchida no config, usa ela para o campo Detalhes
            if base.get('coluna_legis'):
                 # Extrai todos os valores da lista de coluna_legis para o campo 'Detalhes'
                 valores_legis = [f"{c}: {buscar_valor_inteligente(attrs, [c])}" for c in base['coluna_legis']]
                 legis = " | ".join(valores_legis)
                 
                 # Adiciona cada coluna de legis nos detalhes extras
                 for c in base['coluna_legis']:
                     detalhes_extras[c] = buscar_valor_inteligente(attrs, [c])
            
            # Lógica de detalhes extras específicos (mantida por enquanto)
            if "Licenças" in base['nome']:
                detalhes_extras['NumLicenca'] = buscar_valor_inteligente(attrs, ["num_autorizacao", "numero_autorizacao", "autorizacao"])              
                detalhes_extras['Processo'] = buscar_valor_inteligente(attrs, ["numero do processo", "num_processo", "processo"])
                detalhes_extras['Atividade'] = buscar_valor_inteligente(attrs, ["Tipo Empreendimento", "tipo_empreendimento", "atividade", "desc_ativ"])
                detalhes_extras['Tipo Licença'] = buscar_valor_inteligente(attrs, ["Tipo de Licença", "tipo_licenca", "desc_tiple"])
                detalhes_extras['Situacao'] = buscar_valor_inteligente(attrs, ["status_licenca", "situacao", "status"])
                detalhes_extras['Emissao'] = buscar_valor_inteligente(attrs, ["data_expedicao", "data_emissao", "dt_emissao"])
                detalhes_extras['Vencimento'] = buscar_valor_inteligente(attrs, ["Data de Validade", "validade", "data_validade"])
            
            elif "Hidrografia" in base['nome']:
                detalhes_extras['Regime'] = buscar_valor_inteligente(attrs, ["REGIME", "regime"])
            elif "IBAMA" in base['nome']:
                detalhes_extras['Autuado'] = buscar_valor_inteligente(attrs, ["nome_embargado", "nom_pessoa"])
                detalhes_extras['Infração'] = buscar_valor_inteligente(attrs, ["des_infracao", "des_infra"])
            elif "MapBiomas" in base['nome']:
                detalhes_extras['Ano'] = buscar_valor_inteligente(attrs, ["year", "ano"])
                detalhes_extras['Bioma'] = buscar_valor_inteligente(attrs, ["biome", "bioma"])
                detalhes_extras['Data Detecção'] = buscar_valor_inteligente(attrs, ["detected_at", "data_deteccao"])
                if nome_grupo and nome_grupo != "Não identificado":
                    detalhes_extras['url_laudo'] = f"https://plataforma.alerta.mapbiomas.org/alerta/{nome_grupo}"
            elif "Antropizadas" in base['nome']:
                detalhes_extras['Classe'] = buscar_valor_inteligente(attrs, ["CLASS", "Class_Name"])

            area_txt, pct_txt = "---", "---"
            try:
                interseccao = None
                # Se for WFS (que retorna em 4674), precisa re-projetar para o CRS UTM do imóvel antes da intersecção
                if base.get('tipo_fonte') == 'WFS':
                    aux_gdf = gpd.GeoDataFrame({'geometry': [geom_unificada_base]}, crs="EPSG:4674").to_crs(dados_imovel['crs_utm'])
                    interseccao = geom_utm_imovel.intersection(aux_gdf.geometry.iloc[0])
                else:
                    # Para REST, a API já retorna na SR do imóvel (31981), então intersecção é direta
                    interseccao = geom_utm_imovel.intersection(geom_unificada_base)

                if not interseccao.is_empty:
                    if base['tipo'] == 'ponto':
                         area_txt = "Ponto no Imóvel"; pct_txt = "Foco/Ponto"
                    elif base['tipo'] == 'linha':
                         area_txt = "Sim"; pct_txt = "Cruzamento"
                    else:
                        area_calc = interseccao.area / 10000
                        if area_calc < 0.5: continue 
                        area_txt = f"{area_calc:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
                        pct_txt = f"{(area_calc/area_imovel)*100:.2f}%"
                    
                    # Cria GeoDataFrame do resultado da intersecção (para mapa)
                    gdf_conf = gpd.GeoDataFrame({'geometry': [interseccao]}, crs=dados_imovel['crs_utm'])
                    nome_camada = f"{base['nome']}: {nome_grupo}"
                    geojson_str = gdf_conf.to_crs(epsg=4326).to_json()
                    cor_atual = gerar_cor_aleatoria()
                    
                    camadas_parcial.append({
                        "nome": nome_camada, "geojson": json.loads(geojson_str), 
                        "tipo": base['tipo'], "cor": cor_atual
                    })
                    
                    resultados_parcial.append({
                        "Base": base['nome'], "Identificação": nome_grupo, "Detalhes": legis,
                        "Área (ha)": area_txt, "Status": pct_txt,
                        "Extra": detalhes_extras
                    })
            except: pass
                
    return resultados_parcial, camadas_parcial

def executar_varredura_paralela(lista_bases, dados_imovel):
    """Gerencia a execução paralela de processar_uma_base para todas as bases."""
    todos_resultados = []
    todas_camadas = []
    # Aumentando o número de threads para 12 para processar as APIs mais rápido
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor: 
        future_to_base = {executor.submit(processar_uma_base, base, dados_imovel): base for base in lista_bases}
        for future in concurrent.futures.as_completed(future_to_base):
            try:
                res, cam = future.result()
                todos_resultados.extend(res)
                todas_camadas.extend(cam)
            except: pass
    return todos_resultados, todas_camadas
