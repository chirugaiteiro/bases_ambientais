# config_assistant_app.py

import streamlit as st
import pandas as pd
import json
import requests
import sys

# Ajustar o path para poder importar config e utils
# Supondo que config.py e utils.py estão no mesmo diretório ou acessíveis via PYTHONPATH
try:
    # Tenta importar os módulos
    # Se estiver rodando como app separado, pode precisar de um ajuste no sys.path
    from config import TODAS_AS_BASES 
    from utils import coletar_atributos_de_todas_bases
except ImportError:
    st.error("Erro de Importação: Certifique-se de que 'config.py' e 'utils.py' estão no mesmo diretório do 'config_assistant_app.py' ou no seu PYTHONPATH.")
    st.stop()


# --- CONFIGURAÇÕES DO APLICATIVO ---
st.set_page_config(page_title="Mutum - Assistente de Configuração", page_icon="🛠️", layout="wide")

st.title("🛠️ Mutum - Assistente de Configuração de Bases")
st.info("Use esta ferramenta para consultar uma amostra de cada base geoespacial (REST/WFS) e definir o mapeamento de atributos para a plataforma Mutum. Bases de arquivos (ZIP) são ignoradas.")

# --- FUNÇÃO PRINCIPAL DE RENDERIZAÇÃO ---

def render_config_assistente():
    
    # 1. Botão de Ação: Coletar Amostras
    if st.button("🔍 Coletar Amostras de Atributos de TODAS as Bases", type="primary", use_container_width=True):
        st.session_state['atributos_config_assistente'] = None
        with st.spinner("🐦 O Mutum está voando baixo para inspecionar cada base..."):
            
            # 1. Consolida todas as listas de bases em uma única lista e adiciona a categoria
            lista_bases_unificada = []
            for categoria, bases in TODAS_AS_BASES.items():
                for base in bases:
                    base_copy = base.copy()
                    # Só adiciona bases consultáveis via API para a amostragem
                    tipo = base_copy.get('tipo_fonte', 'REST')
                    if tipo in ['REST', 'WFS']:
                        base_copy['categoria'] = categoria 
                        lista_bases_unificada.append(base_copy)

            # 2. Chama a função de utilitário para consultar
            resultados_amostra = coletar_atributos_de_todas_bases(lista_bases_unificada)
            
            # 3. Salva no Session State, incluindo o dicionário original completo das bases
            st.session_state['atributos_config_assistente'] = resultados_amostra
            st.session_state['bases_originais'] = lista_bases_unificada
            
            contagem_ok = sum(1 for d in resultados_amostra.values() if not d.get('erro') and d.get('atributos'))
            st.toast(f"Amostragem concluída: {contagem_ok} bases OK de {len(resultados_amostra)} consultadas.", icon="✅")
            st.rerun() 

    st.divider()

    # 2. Exibição e Configuração (Se houver resultados)
    if st.session_state.get('atributos_config_assistente'):
        st.markdown("##### 📝 Mapeamento e Geração do Código de Configuração")
        resultados = st.session_state['atributos_config_assistente']
        bases_originais = st.session_state['bases_originais']

        for nome_base in sorted(resultados.keys()):
            dados = resultados[nome_base]
            
            # Encontra a configuração original
            base_original = next((b for b in bases_originais if b['nome'] == nome_base), None)
            categoria_base = base_original['categoria'] if base_original else "Desconhecida"

            with st.container(border=True):
                if dados['erro'] or not dados['atributos']:
                    status_icon = "❌"
                    st.error(f"{status_icon} **{nome_base}** (Categoria: {categoria_base}) - Erro na Conexão/Amostra.")
                    with st.expander("Detalhes do Erro"): 
                        st.write(dados.get('erro', 'Resposta da API Vazia ou Inválida.'))
                    continue

                atributos = dados['atributos']
                status_icon = "✅"
                st.success(f"{status_icon} **{nome_base}** (Categoria: {categoria_base} | Tipo Fonte: {dados['tipo_fonte']})")
                
                # --- Configuração ---
                colunas_originais = list(atributos.keys())
                
                with st.expander(f"Configurar e Gerar Código para {nome_base} ({len(colunas_originais)} atributos)", expanded=True):
                    
                    st.markdown("###### 1. Seleção dos Campos")

                    # Tenta carregar defaults baseados na config.py
                    defaults_ident = base_original.get('colunas_nome', [])
                    defaults_legis = base_original.get('coluna_legis', [])
                    
                    # Filtra defaults para garantir que existam na lista atual de colunas
                    defaults_ident = [c for c in defaults_ident if c in colunas_originais]
                    defaults_legis = [c for c in defaults_legis if c in colunas_originais]

                    col_ident, col_legis = st.columns(2)
                    
                    with col_ident:
                        ident_selecionadas = st.multiselect(
                            "Campos de **Identificação** (Nome, ID, Número)",
                            options=colunas_originais,
                            key=f'ident_{nome_base}',
                            default=defaults_ident
                        )
                    
                    with col_legis:
                        legis_selecionadas = st.multiselect(
                            "Campos de **Detalhes/Legislação** (Datas, Situações, Leis)",
                            options=colunas_originais,
                            key=f'legis_{nome_base}',
                            default=defaults_legis
                        )
                    
                    st.markdown("---")
                    
                    # --- Geração do Código ---
                    st.markdown("###### 2. Código para Substituir em `config.py`")
                    
                    # Cria a nova estrutura
                    nova_config = base_original.copy()
                    nova_config['colunas_nome'] = ident_selecionadas
                    nova_config['coluna_legis'] = legis_selecionadas

                    # Remove metadados temporários
                    if 'categoria' in nova_config: del nova_config['categoria']
                    
                    # Formatação final do dicionário como string Python
                    config_str = (
                        "{"
                        f"'nome': '{nova_config.get('nome')}', "
                        f"'url': '{nova_config.get('url')}', "
                        f"'colunas_nome': {json.dumps(nova_config.get('colunas_nome')).replace('"', "'")}, "
                        f"'coluna_legis': {json.dumps(nova_config.get('coluna_legis')).replace('"', "'")}, "
                        f"'tipo': '{nova_config.get('tipo')}'"
                    )
                    
                    if nova_config.get('tipo_fonte'): config_str += f", 'tipo_fonte': '{nova_config.get('tipo_fonte')}'"
                    if nova_config.get('layer_name'): config_str += f", 'layer_name': '{nova_config.get('layer_name')}'"
                    
                    config_str += "}"


                    st.code(config_str, language='python')
                    st.caption(f"👆 Copie este dicionário e substitua o original na lista **{categoria_base}** em `config.py`.")
                    
                    st.markdown("---")
                    
                    # --- Tabela de Amostra ---
                    st.markdown("###### 3. Amostra de Atributos Encontrados")
                    df_atributos = pd.DataFrame(atributos.items(), columns=['Nome Original (API)', 'Valor Amostra'])
                    st.dataframe(df_atributos, use_container_width=True, hide_index=True)
            
            st.divider()
            
# --- INÍCIO DA EXECUÇÃO ---
if __name__ == "__main__":
    render_config_assistente()
