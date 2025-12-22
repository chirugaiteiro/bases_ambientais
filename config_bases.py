# modulos/config_bases.py

# --- URLS GLOBAIS (ARQUIVOS ESTÁTICOS/GITHUB) ---
URL_FOCOS_PARQUET = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/focos_historico.parquet"
URL_HIDRO_OFFLINE = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/hidrografia_MS.zip"

# ATUALIZADO PARA GEOJSON RAW 👇
URL_AUTEX_IBAMA = "https://raw.githubusercontent.com/chirugaiteiro/bases_ambientais/main/Dados_Agrupados_QGIS.geojson"

URL_PARQUET_CONVERTED = "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/converted_data.parquet"

# --- URLS DE SERVIÇOS DE IMAGEM (RESTORED) ---
URL_LANDSAT_2008_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/Imagens/Landsat_5_antes_2008_upscaling8x_v2/ImageServer/exportImage"
URL_SENTINEL_2025_EXPORT = "https://sentinel.arcgis.com/arcgis/rest/services/Sentinel2/ImageServer/exportImage"
URL_DECLIVIDADE_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/Imagens/fusao_declividade_graus/ImageServer/exportImage"
URL_HIDRO_EXPORT = "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/export"

# --- ESTRUTURA DOS MAPEAMENTOS ---
# (Mantido o restante do arquivo igual...)

BASES_ADMINISTRATIVAS = [
    {
        "nome": "Municípios MS", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/38/query", 
        "colunas_nome": ["MUNICIPIO", "MUNICIPIO (Município)", "Município", "NOME_MUN", "nm_mun"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["cod_mun", "geocodigo"],
            "detalhes": {"Área Oficial": ["area_km2", "area_ha"]}
        }
    },
    {
        "nome": "Biomas em MS", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/lim_biomas_atual/MapServer/0/query", 
        "colunas_nome": ["Bioma", "nm_bioma"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["CD_BIOMA", "ID"]
        }
    }
]

BASES_CAR = [
    {
        "nome": "CAR - Limite da Propriedade", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_lim_propriedade/FeatureServer/8/query", 
        "colunas_nome": ["cod_imovel", "COD_IMOVEL", "nome_propriedade"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["nome_propriedade", "nom_imovel"],
            "detalhes": {
                "Sicar": ["cod_imovel"],
                "Município": ["municipio"],
                "Módulo Fiscal": ["mod_fiscal"],
                "Status": ["situacao", "condicao"]
            }
        }
    },
    {
        "nome": "CAR - Uso Restrito", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_uso_restrito/FeatureServer/3/query", 
        "colunas_nome": ["tema", "TEMA"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["classe"],
            "detalhes": {"Área Decl.": ["area_ha"]}
        }
    },
    {
        "nome": "CAR - Uso Consolidado", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_uso_consolidado/FeatureServer/4/query", 
        "colunas_nome": ["tema", "TEMA"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["classe"],
            "detalhes": {"Área Decl.": ["area_ha"]}
        }
    },
    {
        "nome": "CAR - Servidão Administrativa", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_servidao_adm/FeatureServer/5/query", 
        "colunas_nome": ["tema", "TEMA"], 
        "tipo": "poligono",
        "mapeamento": {"legenda": ["classe"]}
    },
    {
        "nome": "CAR - Reserva Legal", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_reserva_legal/FeatureServer/6/query", 
        "colunas_nome": ["tema", "TEMA", "status"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["status", "situacao"],
            "detalhes": {"Tipo": ["fisionomia"]}
        }
    },
    {
        "nome": "CAR - Remanescente Veg. Nativa", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_remanescente_veg_nativa/FeatureServer/7/query", 
        "colunas_nome": ["tema", "TEMA"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["fisionomia"],
            "detalhes": {"Área Decl.": ["area_ha"]}
        }
    },
    {
        "nome": "CAR - Áreas de Preservação Permanente (APP)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/car_app/FeatureServer/9/query", 
        "colunas_nome": ["tema", "TEMA"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["tipo_app", "classe"],
            "detalhes": {"Área Decl.": ["area_ha"]}
        }
    }
]

DICIONARIO_SOLOS = {
    "LE": "Latossolo Vermelho-Escuro (Solos profundos e bem drenados)",
    "LR": "Latossolo Roxo",
    "LV": "Latossolo Vermelho-Amarelo",
    "TR": "Terra Roxa Estruturada",
    "PE": "Podzólico Vermelho-Escuro",
    "PEL": "Podzólico Vermelho-Amarelo Latossólico",
    "PV": "Podzólico Vermelho-Amarelo",
    "BV": "Brunizém Avermelhado",
    "PL": "Planossolo",
    "PS": "Planossolo Solódico",
    "SS": "Solonetz Solodizado",
    "PT": "Plintossolo",
    "PTS": "Plintossolo Solódico", # <--- CONFIRMAR COM SUA IMAGEM
    "HGHV": "Glei Húmico vértico",
    "HGP": "Glei Pouco Húmico",
    "HAQ": "Areias Quartzosas Hidromórficas",
    "HO": "Solos Orgânicos",
    "AQ": "Areias Quartzosas", # <--- CONFIRMAR COM SUA IMAGEM
    "RE": "Regossolo",
    "A": "Solos Aluviais",
    "V": "Vertissolo",
    "VS": "Vertissolo Solódico",
    "RZ": "Rendzina",
    "R": "Solos Litólicos",
    "AC1": "Associação Complexa composta de: Podzólico Vermelho - Amarelo + Cambissolo + Areias Quartzosas + Solos Litólicos",
    "AC2": "Associação Complexa composta de: Planossolo + Glei Húmico + Glei Pouco Húmico + Areias Quartzosas Hidromórficas + Areias Quartzosas + Solos Orgânicos + Solo Aluviais"
}

BASES_CLASSIFICACAO = [
    {
        "nome": "Vegetação (RADAM/IBGE 1:250k)",
        "chave": "vegetacao_ms",
        "url": "https://raw.githubusercontent.com/chirugaiteiro/bases_ambientais/main/Veg_MS_1_250K.geojson",
        "tipo": "geojson",
        "colunas_nome": ["tipo_de_ve", "dominio", "newfield1"], 
        "style": {"fillColor": "#228B22", "color": "#228B22"}
    },
    {
        "nome": "Solos - Macrozoneamento (1:250k)",
        "chave": "solos_ms",
        "url": "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/Solos_MS_1_250K.parquet",
        "tipo": "parquet", 
        "colunas_nome": ["classe_pri", "classe"], 
        "dicionario": DICIONARIO_SOLOS, 
        "style": {"fillColor": "#8B4513", "color": "#A0522D"}
    },
    {
        "nome": "Geologia (CPRM 1:250k)", # Ajustei o nome para refletir o dado
        "chave": "geologia_ms",
        # Converti o link 'blob' para 'raw' automaticamente
        "url": "https://raw.githubusercontent.com/chirugaiteiro/bases_ambientais/main/Geologia_CPRM_2006.geojson",
        "tipo": "geojson",
        "colunas_nome": ["nome_unida", "sigla_unid", "periodo_ma"], 
        # Escolhi tons de Roxo/Cinza, padrão para mapas geológicos
        "style": {"fillColor": "#778899", "color": "#4B0082"}
    }
]


BASES_GERAIS = [
    {
        "nome": "Certificação INCRA - SNCI", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/publico/INCRA_Imóveis_Rurais/MapServer/1/query", 
        "colunas_nome": ["CLASSE"], 
        "tipo": "poligono", # ou "linha" ou "ponto"
        "mapeamento": {
            "legenda": ["nome_imove"],
            "detalhes": {
                "Descrição": ["num_certif"],
            }
        }
    },
    {
        "nome": "Certificação INCRA - SIGEF", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/publico/INCRA_Imóveis_Rurais/MapServer/2/query", 
        "colunas_nome": ["CLASSE"], 
        "tipo": "poligono", # ou "linha" ou "ponto"
        "mapeamento": {
            "legenda": ["nome_area"],
            "detalhes": {
                "Descrição": ["parcela_co"],
            }
        }
    },
    {
        "nome": "Projetos de Assentamentos Estado de MS - Perímetros", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/18/query", 
        "colunas_nome": ["CLASSE"], 
        "tipo": "poligono", # ou "linha" ou "ponto"
        "mapeamento": {
            "legenda": ["NOME"],
            "detalhes": {
                "Descrição": ["CRIACAO"],
            }
        }
    },
    {
        "nome": "Projetos de Assentamentos Incra - Perímetros", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/16/query", 
        "colunas_nome": ["PA"], 
        "tipo": "poligono", # ou "linha" ou "ponto"
        "mapeamento": {
            "legenda": ["PA"],
            "detalhes": {
                "Descrição": ["ATO"],
            }
        }
    },
    {
        "nome": "Unidades de Conservação", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/UCs_MS_Mosaico/MapServer/0/query", 
        "colunas_nome": ["Nome UC", "NOME_UC", "NM_UC"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["grupo", "categoria"],
            "detalhes": {
                "Esfera": ["esfera", "jurisdicao"],
                "Ato de Criação": ["ato_criacao", "decreto", "leis"],
                "Ano": ["ano_criacao"]
            }
        }
    },
    {
        "nome": "Terras Indígenas", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/4/query", 
        "colunas_nome": ["terrai_nom", "TERRAI_NOM"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["fase_ti", "situacao"],
            "detalhes": {
                "Etnia": ["etnia_nome"],
                "Modalidade": ["modalidade"]
            }
        }
    },
    {
        "nome": "Povos Tradicionais (Quilombolas)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/AGRAER_SERVICOS/Povos_Tradicionais/MapServer/2/query", 
        "colunas_nome": ["nm_comunid", "NM_COMUNID"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["municipio"],
            "detalhes": {"Descrição": ["ob_descric"]}
        }
    },
    {
        "nome": "Áreas de Uso Restrito (Dec. 15.661)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/49/query", 
        "colunas_nome": ["TOPONIMIA", "toponimia"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["CLASSE", "classe"],
            "detalhes": {"Obs": ["leis"]}
        }
    },
    {
        "nome": "Áreas Priorit. Banhados", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/52/query", 
        "colunas_nome": ["CLASSE", "classe"], 
        "tipo": "poligono",
        "mapeamento": {"legenda": ["leis"]}
    },
    {
        "nome": "Bacias Hidrográficas do Rio Paraná em MS", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/14/query", 
        "colunas_nome": ["bacia", "BACIA", "nome"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["unidade_pl"],
            "detalhes": {"Cód. Bacia": ["cod_bacia"]}
        }
    },
    {
        "nome": "Bacias Hidrográficas do Rio Paraguai em MS", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/13/query", 
        "colunas_nome": ["bacia", "BACIA", "nome"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["unidade_pl"],
            "detalhes": {"Cód. Bacia": ["cod_bacia"]}
        }
    },
    {
        "nome": "Corredores Ecológicos do Pantanal", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/Corredores_Ecológicos_Pantanal/MapServer/0/query", 
        "colunas_nome": ["corredor", "CORREDOR", "nome"], 
        "tipo": "poligono",
        "mapeamento": {"legenda": ["leis"]}
    },
    {
        "nome": "Área de Entorno 0-3 Km (Rio Taquari)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/SiriemaGeo_Sisla/MapServer/48/query", 
        "colunas_nome": ["FID", "gid"], 
        "tipo": "poligono",
        "mapeamento": {"legenda": ["CLASSE"]}
    },
    {
        "nome": "Zona de Amortecimento (Estaduais)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/2/query", 
        "colunas_nome": ["NOME_UC", "nome_uc"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["leis"],
            "detalhes": {"Categoria": ["categoria"]}
        }
    },
    {
        "nome": "ZA (Conama 0-2km)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/1/query", 
        "colunas_nome": ["NOME", "nome"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["FAIXA", "faixa"],
            "detalhes": {"Obs": ["leis"]}
        }
    },
    {
        "nome": "ZA (Conama 0-3km)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/CAMADAS_API_SISGEO_v1/FeatureServer/0/query", 
        "colunas_nome": ["NOME", "nome"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["FAIXA", "faixa"],
            "detalhes": {"Obs": ["leis"]}
        }
    }
]

BASES_HIDRO = [
    {
        "nome": "Hidrografia MS (Rios)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/SEMADESC/SEMADESC_MAPAS/MapServer/12/query", 
        # ATUALIZAR AQUI 👇
        "colunas_nome": ["nome", "NOME", "rio", "RIO", "nm_curso", "no_rio", "nome_rio"], 
        "tipo": "linha",
        "mapeamento": {
            # ATUALIZAR AQUI TAMBÉM 👇
            "legenda": ["regime", "REGIME", "ds_regime", "tipo_regime"],
            "detalhes": {"Extensão": ["shape_len"]}
        }
    }
]

BASES_FISCALIZACAO = [
    {
        "nome": "Embargos IBAMA", 
        "tipo_fonte": "REST", 
        "url": "https://pamgia.ibama.gov.br/server/rest/services/01_Publicacoes_Bases/adm_embargos_ibama_a/MapServer/0/query", 
        "colunas_nome": ["num_tad", "NUM_TAD"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["nom_pessoa", "nome_embargado"],
            "detalhes": {
                "Infração": ["des_infracao", "des_infra"],
                "Data": ["dat_embargo"],
                "Qtd. Área": ["qtd_area_embargada"]
            }
        }
    },
    {
        "nome": "Embargos ICMBio", 
        "tipo_fonte": "WFS", 
        "url": "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows", 
        "layer_name": "ICMBio:embargos_icmbio", 
        "colunas_nome": ["numero_embargo", "numero_emb"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["infracao"],
            "detalhes": {"Data": ["data_embargo"]}
        }
    },
    {
        # --- CONFIGURAÇÃO CORRIGIDA MAPBIOMAS ---
        "nome": "MapBiomas Alerta", 
        "tipo_fonte": "WFS", 
        "url": "https://production.alerta.mapbiomas.org/geoserver/wfs", 
        "layer_name": "mapbiomas-alertas:alert_report", 
        # Adicionei 'alert_code' como primeira opção
        "colunas_nome": ["alert_code", "alerta_id", "cod_alerta"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["bioma", "biome"],
            "detalhes": {
                # Mapeamento EXATO do CSV que você enviou
                "Ano": ["detected_year", "year", "ano"],
                "Detecção": ["detected_at", "data_deteccao"],
                "Área (ha)": ["area_ha"]
            }
        }
    },
    {
        "nome": "Áreas Antropizadas (SICAR/Dinamizada)", 
        "tipo_fonte": "REST", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/CAR/Insumos/MapServer/1/query", 
        "colunas_nome": ["Class_Name", "CLASS", "OBJECTID"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["Class_Name", "CLASS"],
            "detalhes": {"Área (m2)": ["Shape.STArea()", "shape_area"]}
        }
    },
]

BASES_LICENCAS = [
    {
        "nome": "Licenças Emitidas (Siriema/IMASUL)", 
        "url": "https://www.pinms.ms.gov.br/arcgis/rest/services/IMASUL/licencas_ambientais/FeatureServer/16/query", 
        "colunas_nome": ["num_processo", "processo", "n_processo", "emp_id"], 
        "tipo": "poligono",
        "mapeamento": {
            "legenda": ["atividade", "desc_ativ", "tipologia"],
            "detalhes": {
                "Núm. Licença": ["num_autorizacao", "numero_autorizacao"],
                "Tipo": ["tipo_licenca", "desc_tiple"],
                "Situação": ["status_licenca", "situacao"],
                "Emissão": ["data_expedicao", "data_emissao"],
                "Validade": ["validade", "data_validade"]
            }
        }
    }
]


BASES_RELEVO = [
    {
        "nome": "Declividade 25° a 45° (Uso Restrito)",
        "url": "https://github.com/chirugaiteiro/bases_ambientais/raw/refs/heads/main/restrito_25_45.zip",
        "tipo_arquivo": "zip",
        "colunas_nome": ["classe", "gridcode", "declividade"], # Possíveis nomes de coluna
        "mapeamento": {
            "legenda": ["classe"],
            "detalhes": {"Fonte": "Base Vetorial 25-45"}
        }
    },
    {
        "nome": "Declividade > 45° (Uso Restrito/APP)",
        "url": "https://github.com/chirugaiteiro/bases_ambientais/raw/main/acima_45.geojson",
        "tipo_arquivo": "geojson",
        "colunas_nome": ["classe", "gridcode", "dn"], 
        "mapeamento": {
            "legenda": ["classe"],
            "detalhes": {"Fonte": "Base Vetorial >45"}
        }
    },
    {
        "nome": "APP Topo de Morro",
        "url": "https://github.com/chirugaiteiro/bases_ambientais/raw/main/app_topo_morro.geojson",
        "tipo_arquivo": "geojson",
        "colunas_nome": ["classe", "tipo", "nome"],
        "mapeamento": {
            "legenda": ["tipo"],
            "detalhes": {"Fonte": "Base Vetorial Topo"}
        }
    }
]

BASES_LICENCAS_FEDERAL = [
    {
        "nome": "Autex Sinaflor (Base GeoJSON)",
        "url": "https://raw.githubusercontent.com/chirugaiteiro/bases_ambientais/main/Autex_Sinaflor.geojson",
        "tipo_fonte": "FEDERAL_GEOJSON",
        
        "colunas_chave": {
            "num_licenca": "NRO_DA_AUTORIZACAO_ORIGINAL",
            "status": "SITUACAO_ATUAL",
            "validade": "DATA_DE_VALIDADE_DA_AUTEX",
            "emissao": "ANO",
            
            # --- NOVAS COLUNAS SOLICITADAS ---
            "origem": "NOME_DA_ORIGEM",
            "produto": "TIPO_DE_PRODUTO",
            "cientifico": "NOME_CIENTIFICO",
            "volume": "RESUMO_VOLUME",
            
            # Mantendo mapeamentos auxiliares caso precise
            "processo": "COD_AUTEX",
            "tipo": "_PADRAO_", 
            "detentor": "NOME_RAZAO_SOCIAL_DO_DETENTOR"
        }
    }
]


# --- BASES OFFLINE / GITHUB ---
BASES_GITHUB = [
    {"nome": "Focos Históricos (INPE - Parquet)", "url": URL_FOCOS_PARQUET, "tipo_fonte": "PARQUET"},
    {"nome": "Hidrografia MS (Offline - ZIP)", "url": URL_HIDRO_OFFLINE, "tipo_fonte": "ZIP"},
    {"nome": "Dados Agrupados (Autex - ZIP)", "url": URL_AUTEX_IBAMA, "tipo_fonte": "ZIP"},
    {"nome": "Dados Convertidos (Parquet)", "url": URL_PARQUET_CONVERTED, "tipo_fonte": "PARQUET"}
]
