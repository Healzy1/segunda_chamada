# 📄 Gerador de Convocações de 2ª Chamada

Aplicação web simples para automatizar a geração de convocações de provas de 2ª chamada a partir de planilhas Excel.

## 🚀 Acesse Online

**[👉 Clique aqui para usar a aplicação](https://segundachamada.streamlit.app/)**

Não precisa instalar nada! Use direto no navegador.

## 🎯 O que faz

- Lê planilha Excel com faltas dos alunos
- Identifica quem precisa fazer 2ª chamada (marcado com "F")
- Gera um documento Word para cada aluno
- Baixa tudo em um arquivo ZIP

## 📖 Como Usar

1. **Baixe os arquivos exemplo** (neste repositório):
   - `exemplo_planilha.xlsx` - Modelo da planilha
   - `exemplo_template.docx` - Modelo do documento Word

2. **Prepare seus arquivos:**
   - Preencha a planilha com seus alunos e faltas
   - **Personalize como quiser:** adicione mais matérias, mais alunos, quantas abas precisar!
   - Personalize o template Word se necessário

3. **Use a aplicação online:**
   - Acesse o link acima
   - Faça upload da planilha (.xlsx)
   - Faça upload do template (.docx)
   - Digite a data limite para assinatura
   - Clique em "Gerar Convocações"
   - Baixe o ZIP com todos os documentos

## 📊 Formato da Planilha

**Pontos importantes:**
- **Coluna A1, B1, C1:** Turma (ex: "6º ano Ensino Fundamental     C")
- **Coluna C a partir da linha 3:** Nomes dos alunos
- **Célula J1:** Texto com a data (ex: "PROVA 30/10")
- **Linha 2, coluna J em diante:** Nomes das matérias
- **Use "F"** para marcar falta (gerará convocação)
- **Deixe vazio** para presença (não gera convocação)

💡 **Dica:** Você pode adicionar quantas matérias e alunos quiser! Basta continuar preenchendo as colunas.

**📥 Baixe o arquivo `exemplo_planilha.xlsx` neste repositório para ver o formato completo!**

## 📝 Template Word

Crie um documento Word simples usando estas variáveis:

- `{{ nome_aluno }}` - Nome do estudante
- `{{ turma }}` - Turma simplificada (ex: 6ºC)
- `{{ provas_texto }}` - Lista das matérias e datas (gerado automaticamente)
- `{{ data_limite }}` - Data limite para assinatura

### Exemplo:

```
CONVOCAÇÃO PARA 2ª CHAMADA

Aluno(a): {{ nome_aluno }}
Turma: {{ turma }}

Provas pendentes:
{{ provas_texto }}

Data limite para assinatura: {{ data_limite }}

_______________________________
Assinatura do Responsável
```

**📥 Baixe o arquivo `exemplo_template.docx` neste repositório para usar como base!**

O sistema gera automaticamente o texto no formato:
```
Matéria: PORTUGUÊS		Data da prova: 30/10
Matéria: CIÊNCIAS		Data da prova: 30/10
```

## 🔍 O que o sistema faz automaticamente

✅ Identifica a turma (ex: "6º ano Ensino Fundamental C" → "6ºC")  
✅ Extrai a data da prova (ex: "PROVA 30/10" → "30/10")  
✅ Lista todas as matérias encontradas  
✅ Gera documento apenas para alunos com "F"  
✅ Formata o texto das provas  
✅ Nomeia os arquivos: `Convocacao_6ºC_NOME_ALUNO.docx`

## 🐛 Problemas Comuns

**"Nenhum arquivo gerado"**
- Verifique se há letras "F" nas colunas das matérias
- Confira se a coluna C tem os nomes dos alunos (a partir da linha 3)

**"Turma não identificada"**
- Verifique que no modelo foi usado uma mescla de células A1, B1 e C1

**"Data não encontrada"**
- Célula J1 deve ter texto como "PROVA 30/10"
- Formato da data: DD/MM

## 📦 Arquivos de Exemplo

Neste repositório você encontra:
- 📄 `exemplo_planilha.xlsx` - Planilha modelo
- 📄 `exemplo_template.docx` - Template Word modelo
- 🐍 `app.py` - Código da aplicação
- 📋 `requirements.txt` - Dependências

## 🛠️ Tecnologias

- Streamlit
- Pandas
- docxtpl
- openpyxl

## 📄 Licença

MIT License - use livremente!

---

⭐ Gostou? Deixe uma estrela no GitHub!