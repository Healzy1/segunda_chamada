import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import re
import io
import zipfile
from io import BytesIO

def extrair_data(texto_prova):
    """Extrai a data (ex: 30/10) de um texto (ex: PROVA 30/10)."""
    if not isinstance(texto_prova, str):
        return 'DATA_NAO_ENCONTRADA'
        
    match = re.search(r'(\d{2}/\d{2})', texto_prova)
    if match:
        return match.group(1)
    return 'DATA_NAO_ENCONTRADA'

def limpar_nome_arquivo(nome):
    """Remove caracteres inválidos do nome do aluno para salvar o arquivo."""
    if not isinstance(nome, str):
        nome = str(nome)
    nome_limpo = re.sub(r'[\\/*?:"<>|]', "", nome)
    return nome_limpo.replace(' ', '_')

def simplificar_turma(nome_turma):
    """Tenta simplificar nomes longos de turma para um formato curto (ex: 6ºA)."""
    # Remove "Ensino Fundamental" e "Ensino Médio" (e variações)
    nome_limpo = re.sub(r'ensino (fundamental|m[eé]dio)', '', nome_turma, flags=re.IGNORECASE)
    
    # Remove a palavra "ano"
    nome_limpo = re.sub(r'ano', '', nome_limpo, flags=re.IGNORECASE)
    
    # Tenta extrair o padrão "Nº LETRA" (ex: 6º A -> 6ºA)
    match = re.search(r'(\d+[ºª°])\s*([A-Z])', nome_limpo, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)}{match.group(2).upper()}"
    
    # Se não encontrar, apenas limpa os espaços extras e retorna
    return re.sub(r'\s+', '', nome_limpo).strip()


def processar_convocacoes_streamlit(excel_file_buffer, template_file_buffer, data_limite_assinatura):
    """
    Função principal que lê os arquivos, processa os alunos e retorna um zip.
    AGORA LÊ TODAS AS PLANILHAS (ABAS) DO ARQUIVO EXCEL.
    """
    logs = ["Iniciando o processo..."]
    arquivos_gerados = []
    alunos_processados_total = 0

    try:
        # Carrega o arquivo Excel inteiro
        xls = pd.ExcelFile(excel_file_buffer)
        
        # Itera (passa por) CADA planilha (aba) no arquivo Excel
        for sheet_name in xls.sheet_names:
            logs.append(f"--- 📄 Processando Planilha: {sheet_name} ---")
            
            try:
                # Carrega a planilha atual do buffer em memória
                df_completo = pd.read_excel(xls, sheet_name=sheet_name, header=None)

                # --- Extração de Informações Gerais (da planilha atual) ---
                turma_a = str(df_completo.iloc[0, 0]) if not pd.isna(df_completo.iloc[0, 0]) else ""
                turma_b = str(df_completo.iloc[0, 1]) if not pd.isna(df_completo.iloc[0, 1]) else ""
                turma_c = str(df_completo.iloc[0, 2]) if not pd.isna(df_completo.iloc[0, 2]) else ""
                turma = re.sub(r'\s+', ' ', f"{turma_a} {turma_b} {turma_c}").strip()
                
                if not turma:
                    logs.append(f"AVISO: Turma não identificada na planilha '{sheet_name}'. Pulando esta planilha.")
                    continue
                
                turma_simplificada = simplificar_turma(turma)
                
                texto_prova = df_completo.iloc[0, 9] # Célula J1
                data_prova = extrair_data(texto_prova)

                logs.append(f"Turma identificada: {turma_simplificada} (Original: {turma})")
                logs.append(f"Data das provas identificada: {data_prova}")

                # --- Extração das Matérias ---
                materias_linha = df_completo.iloc[1]
                colunas_materias = {}
                for i, materia in enumerate(materias_linha[9:]): # Começa da coluna J
                    if materia and not pd.isna(materia):
                        coluna_indice = 9 + i
                        colunas_materias[coluna_indice] = str(materia).strip().upper()
                
                logs.append(f"Matérias identificadas: {', '.join(colunas_materias.values())}")

                # --- Processamento dos Alunos (da planilha atual) ---
                alunos_processados_planilha = 0
                for index, row in df_completo.iloc[2:].iterrows():
                    nome_aluno = row[2] # Coluna C
                    if not nome_aluno or pd.isna(nome_aluno):
                        continue 

                    provas_pendentes_texto = [] 
                    for col_idx, nome_materia in colunas_materias.items():
                        if str(row[col_idx]).strip().upper() == 'F':
                            # *** ATUALIZAÇÃO AQUI ***
                            # Adiciona \t\t para inserir dois "TABs"
                            provas_pendentes_texto.append(
                                f"Matéria: {nome_materia}\t\tData da prova: {data_prova}"
                            )

                    # Se o aluno tiver provas pendentes, gera o documento
                    if provas_pendentes_texto:
                        logs.append(f"Gerando convocação para: {nome_aluno}")
                        alunos_processados_planilha += 1
                        
                        template_file_buffer.seek(0)
                        doc = DocxTemplate(template_file_buffer)
                        
                        # Juntamos a lista de provas em um único bloco de texto
                        # O \n é um "Enter" que separa as linhas
                        texto_final_provas = "\n".join(provas_pendentes_texto)
                        
                        context = {
                            'nome_aluno': str(nome_aluno).strip(),
                            'turma': str(turma_simplificada).strip(),
                            'provas_texto': texto_final_provas, # Nova variável para o template
                            'data_limite': data_limite_assinatura
                        }
                        
                        doc.render(context)
                        
                        file_stream = BytesIO()
                        doc.save(file_stream) 
                        file_stream.seek(0) 
                        
                        nome_arquivo_limpo = limpar_nome_arquivo(nome_aluno)
                        nome_arquivo_final = f"Convocacao_{str(turma_simplificada).strip()}_{nome_arquivo_limpo}.docx"
                        
                        arquivos_gerados.append((nome_arquivo_final, file_stream))

                if alunos_processados_planilha == 0:
                    logs.append(f"Nenhum aluno com 'F' encontrado na planilha '{sheet_name}'.")
                
                alunos_processados_total += alunos_processados_planilha

            except Exception as e:
                logs.append(f"ERRO ao processar a planilha '{sheet_name}': {e}. Esta planilha pode estar mal formatada. Pulando...")


    except Exception as e:
        logs.append(f"Ocorreu um erro inesperado ao ler o arquivo Excel: {e}")
        st.error(f"Erro no processamento: {e}")

    # --- Criação do Arquivo ZIP ---
    if arquivos_gerados:
        logs.append(f"--- ✅ Processo finalizado. {len(arquivos_gerados)} arquivos gerados no total. ---")
        
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for nome_arquivo, file_stream in arquivos_gerados:
                zip_file.writestr(nome_arquivo, file_stream.getvalue())
        
        zip_buffer.seek(0)
        return zip_buffer, logs

    logs.append("Nenhum arquivo de convocação foi gerado.")
    return None, logs

# --- Interface do Streamlit ---
st.set_page_config(page_title="Gerador de Convocações", layout="wide")
st.title("Gerador de Convocações de 2ª Chamada 📄")
st.markdown("Faça o upload da planilha de faltas e do modelo Word para gerar as convocações.")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Configurações")
    
    uploaded_excel = st.file_uploader("1. Planilha de Alunos (.xlsx)", type="xlsx")
    uploaded_template = st.file_uploader("2. Modelo de Convocação (.docx)", type="docx")
    data_limite = st.text_input("3. Data Limite para Assinatura", "ex: 29/10/2025")
    
    gerar_button = st.button("Gerar Convocações")

# --- Área Principal ---
if gerar_button:
    if uploaded_excel and uploaded_template and data_limite:
        with st.spinner("Processando... Por favor, aguarde."):
            # Converte os arquivos uploadados para BytesIO
            excel_buffer = BytesIO(uploaded_excel.getvalue())
            template_buffer = BytesIO(uploaded_template.getvalue())
            
            zip_file_buffer, logs = processar_convocacoes_streamlit(
                excel_buffer, 
                template_buffer, 
                data_limite
            )
            
            st.success("Processamento concluído!")
            
            # Expander para os logs
            with st.expander("Log de Processamento", expanded=True):
                for log_entry in logs:
                    if "ERRO" in log_entry:
                        st.error(log_entry)
                    elif "AVISO" in log_entry:
                        st.warning(log_entry)
                    else:
                        st.info(log_entry)
            
            if zip_file_buffer:
                st.download_button(
                    label="Baixar Arquivos .ZIP",
                    data=zip_file_buffer,
                    file_name="convocacoes_geradas.zip",
                    mime="application/zip"
                )
    else:
        st.warning("Por favor, faça o upload de ambos os arquivos e preencha a data limite.")