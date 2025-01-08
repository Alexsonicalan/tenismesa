import pandas as pd
import streamlit as st
import base64

# Certifique-se de ter o openpyxl instalado
# pip install openpyxl

# Inicializar a base de dados (persistência entre execuções)
if 'dados' not in st.session_state:
    st.session_state.dados = []

# Função para registrar atleta individual
def registrar_atleta(atleta):
    try:
        idade = int(atleta['Idade'].split('-')[0]) if '-' in atleta['Idade'] else int(atleta['Idade'].replace('Acima de ', ''))
        categorias = {
            range(20, 31): '20-30',
            range(35, 41): '35-40',
            range(40, 50): '40-49',
            range(50, 60): '50-59',
            range(60, 65): '60-64',
            range(65, 70): '65-69',
            range(70, 75): '70-74',
            range(75, 80): '75-79',
            range(80, 85): '80-84'
        }
        for faixa, categoria in categorias.items():
            if idade in faixa:
                atleta['Categoria'] = categoria
                break
        else:
            atleta['Categoria'] = 'Acima de 85' if idade >= 85 else 'Fora de categoria'

        # Adicionar atleta ao estado e exibir sucesso
        st.session_state.dados.append(atleta)
        st.success(f"Atleta {atleta['Nome']} registrado com sucesso!")
    except ValueError:
        st.error("Erro ao processar a idade. Verifique o campo.")
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")

# Função para registrar atletas em lote
def registrar_atletas_em_lote():
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Usando openpyxl para leitura de arquivos Excel
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            for _, row in df.iterrows():
                atleta = {
                    'Nome': row['Nome'],
                    'Idade': row['Idade'],
                    'Sexo': row['Sexo'],
                    'Equipe': row['Equipe']
                }
                registrar_atleta(atleta)
            st.success("Todos os atletas foram registrados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.warning("Nenhum arquivo foi carregado.")

# Função para exportar dados para CSV
def exportar_dados():
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="atletas.csv">Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.warning("Nenhum dado para exportar.")

# Função para organizar chaves
def organizar_chaves():
    if st.session_state.dados:
        df = pd.DataFrame(st.session_state.dados)
        for sexo in df['Sexo'].unique():
            df_sexo = df[df['Sexo'] == sexo]
            categorias = df_sexo['Categoria'].unique()
            for categoria in categorias:
                if categoria != 'Fora de categoria':
                    st.write(f"\nSexo: {sexo}, Categoria: {categoria}")
                    competidores = df_sexo[df_sexo['Categoria'] == categoria]
                    if len(competidores) < 2:
                        st.write("Não há competidores suficientes para formar chaves nesta categoria.")
                        continue
                    competidores = competidores.sample(frac=1).reset_index(drop=True)
                    chaves = [competidores.iloc[i:i + 2] for i in range(0, len(competidores), 2)]
                    for i, chave in enumerate(chaves):
                        st.write(f"Chave {i + 1}:")
                        st.dataframe(chave)
                else:
                    st.write(f"\nCompetidores Fora de Categoria do sexo {sexo} não serão incluídos nas chaves.")
    else:
        st.warning("Nenhum dado disponível para organizar chaves.")

# Interface Streamlit
st.title("Registro de Atletas")

# Formulário para registro individual
with st.form("registro_form"):
    st.text_input("Nome:", key="nome")
    opcoes_idade = ['20-30', '35-40', '40-49', '50-59', '60-64', '65-69', '70-74', '75-79', '80-84', 'Acima de 85']
    st.selectbox("Idade:", opcoes_idade, key="idade")
    st.selectbox("Sexo:", ['M', 'F'], key="sexo")
    st.selectbox("Equipe:", ['BRASIL', 'CHILE', 'EQUADOR', 'VENEZUELA'], key="equipe")
    submitted = st.form_submit_button("Registrar Atleta")
    if submitted:
        atleta = {
            'Nome': st.session_state.nome,
            'Idade': st.session_state.idade,
            'Sexo': st.session_state.sexo,
            'Equipe': st.session_state.equipe
        }
        registrar_atleta(atleta)

# Botão para registrar atletas em lote
st.subheader("Registrar Atletas em Lote")
registrar_atletas_em_lote()

# Exibir tabela de atletas registrados
if st.session_state.dados:
    st.subheader("Atletas Registrados:")
    st.dataframe(pd.DataFrame(st.session_state.dados))

# Botões de Exportar e Organizar Chaves
col1, col2 = st.columns(2)
with col1:
    if st.button("Exportar Dados"):
        exportar_dados()
with col2:
    if st.button("Organizar Chaves"):
        organizar_chaves()

st.markdown("---")
st.markdown("Preencha os campos acima para registrar atletas individualmente ou carregue um arquivo Excel para registro em lote.")
st.markdown("Use os botões para exportar dados ou organizar os competidores em chaves.")
