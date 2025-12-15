import streamlit as st
import requests
from config_bases import (
    URL_FOCOS_PARQUET, URL_HIDRO_OFFLINE, URL_AUTEX_IBAMA, URL_PARQUET_CONVERTED,
    URL_LANDSAT_2008_EXPORT, URL_SENTINEL_2025_EXPORT, URL_DECLIVIDADE_EXPORT, URL_HIDRO_EXPORT,
    BASES_ADMINISTRATIVAS, BASES_CAR, BASES_CLASSIFICACAO, BASES_GERAIS,
    BASES_HIDRO, BASES_FISCALIZACAO, BASES_LICENCAS, BASES_RELEVO, BASES_LICENCAS_FEDERAL,
    BASES_GITHUB
)
# --- 1. Função para Verificar URL ---

@st.cache_data(ttl=3600) # Cacha o resultado por 1 hora para evitar requisições excessivas
def check_url_status(url):
    """Verifica o status HTTP de uma URL."""
    try:
        # Usar HEAD é mais rápido e só verifica os cabeçalhos,
        # mas para alguns serviços (como os do ArcGIS) GET é mais confiável.
        # Ajuste o timeout conforme a sua necessidade.
        response = requests.get(url, timeout=10) 
        
        # Códigos 2xx (Sucesso) indicam que a URL está OK
        if 200 <= response.status_code < 300:
            return "🟢 ONLINE (200 OK)", response.status_code
        # Códigos 3xx (Redirecionamento) também podem ser considerados OK
        elif 300 <= response.status_code < 400:
            return f"🟡 REDIRECIONAMENTO ({response.status_code})", response.status_code
        # Códigos 4xx (Erro do Cliente) e 5xx (Erro do Servidor) indicam problemas
        else:
            return f"🔴 ERRO HTTP ({response.status_code})", response.status_code

    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, SSL, etc.
        return f"❌ ERRO DE CONEXÃO", str(e)


# --- 2. Função para Extrair e Coletar URLs ---

def collect_urls_from_config():
    """Extrai todas as URLs do arquivo de configuração e as agrupa."""
    urls = []

    # URLs Globais
    grupo = "URLs Globais (Estáticas/GitHub)"
    urls.append({"Grupo": grupo, "Nome da Base": "Focos Históricos (PARQUET)", "URL": URL_FOCOS_PARQUET})
    urls.append({"Grupo": grupo, "Nome da Base": "Hidrografia MS (ZIP)", "URL": URL_HIDRO_OFFLINE})
    urls.append({"Grupo": grupo, "Nome da Base": "Autex IBAMA (GEOJSON)", "URL": URL_AUTEX_IBAMA})
    urls.append({"Grupo": grupo, "Nome da Base": "Dados Convertidos (PARQUET)", "URL": URL_PARQUET_CONVERTED})

    # URLs de Serviços de Imagem (Export)
    grupo = "Serviços de Imagem (ArcGIS Export)"
    urls.append({"Grupo": grupo, "Nome da Base": "Landsat 2008 Export", "URL": URL_LANDSAT_2008_EXPORT})
    urls.append({"Grupo": grupo, "Nome da Base": "Sentinel 2025 Export", "URL": URL_SENTINEL_2025_EXPORT})
    urls.append({"Grupo": grupo, "Nome da Base": "Declividade Export", "URL": URL_DECLIVIDADE_EXPORT})
    urls.append({"Grupo": grupo, "Nome da Base": "Hidrografia MapServer Export", "URL": URL_HIDRO_EXPORT})
    
    # Extrair URLs das listas de BASES
    listas_bases = {
        "BASES_ADMINISTRATIVAS": BASES_ADMINISTRATIVAS,
        "BASES_CAR": BASES_CAR,
        "BASES_CLASSIFICACAO": BASES_CLASSIFICACAO,
        "BASES_GERAIS": BASES_GERAIS,
        "BASES_HIDRO": BASES_HIDRO,
        "BASES_FISCALIZACAO": BASES_FISCALIZACAO,
        "BASES_LICENCAS": BASES_LICENCAS,
        "BASES_RELEVO": BASES_RELEVO,
        "BASES_LICENCAS_FEDERAL": BASES_LICENCAS_FEDERAL,
        "BASES_GITHUB (URLs Adicionais)": BASES_GITHUB
    }

    for grupo_nome, bases in listas_bases.items():
        for base in bases:
            # Acessa a URL, priorizando 'url', depois 'url' ou 'layer_name' + URL base (se WFS)
            url_a_checar = base.get("url", "")
            if url_a_checar:
                urls.append({
                    "Grupo": grupo_nome, 
                    "Nome da Base": base.get("nome", "N/A"), 
                    "URL": url_a_checar
                })
            # Nota: Para WFS/WMS que usam uma URL base + layer_name, 
            # talvez seja necessário um teste mais complexo (ex: GetCapabilities). 
            # Este código testa apenas a URL base.

    return urls

# --- 3. Script Principal do Streamlit ---

def main():
    st.set_page_config(page_title="Verificador de Status de Bases Geoespaciais", layout="wide")
    st.title("🌐 Verificador de Acessibilidade das Bases de Dados")
    st.markdown("Verifica se as URLs de serviços e arquivos estáticos definidos em `config_bases.py` estão online (código de status 200).")

    urls_to_check = collect_urls_from_config()

    if st.button("▶️ Iniciar Verificação das URLs"):
        st.info(f"Verificando {len(urls_to_check)} URLs...")
        
        # Inicializa a barra de progresso
        progress_bar = st.progress(0)
        status_results = []
        
        for i, item in enumerate(urls_to_check):
            # 1. Faz a checagem da URL
            status_message, status_code = check_url_status(item["URL"])
            
            # 2. Adiciona o resultado
            status_results.append({
                "Grupo": item["Grupo"],
                "Nome da Base": item["Nome da Base"],
                "URL": item["URL"],
                "Status": status_message,
                "Cód.": status_code # Inclui o código para depuração
            })
            
            # 3. Atualiza a barra de progresso
            progress_bar.progress((i + 1) / len(urls_to_check))

        # Finaliza a barra de progresso
        progress_bar.empty()
        st.success("Verificação concluída!")

        # Converte para DataFrame e exibe (necessita da biblioteca pandas)
        try:
            import pandas as pd
            df_results = pd.DataFrame(status_results)
            
            # Ordena e exibe a tabela interativa do Streamlit
            st.dataframe(df_results, use_container_width=True, hide_index=True)
            
            # Exibe um resumo
            online_count = df_results[df_results['Status'].str.contains('ONLINE')].shape[0]
            error_count = df_results[df_results['Status'].str.contains('ERRO')].shape[0]
            st.markdown(f"---")
            st.markdown(f"**Resumo:** **{online_count}** URLs Online de **{len(urls_to_check)}** checadas. (**{error_count}** com Erro/Falha de Conexão).")

        except ImportError:
            st.error("A biblioteca Pandas é necessária para exibir os resultados em formato de tabela. Instale com `pip install pandas`.")
            st.json(status_results)


if __name__ == "__main__":
    main()
