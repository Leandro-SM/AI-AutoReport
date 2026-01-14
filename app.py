import streamlit as st
from llm import get_llm
from langchain.prompts import PromptTemplate

st.set_page_config(page_title="AI-AutoReport", layout="centered")

st.title("AI-AutoReport")
st.write("Transforme dados técnicos em relatórios claros e objetivos.")

user_input = st.text_area(
    "Cole os dados técnicos abaixo:",
    height=250
)

if st.button("Gerar Relatório") and user_input.strip():
    llm = get_llm()

    with open("prompt.txt", "r", encoding="utf-8") as f:
        template = f.read()

    prompt = PromptTemplate(
        input_variables=["input"],
        template=template
    )

    with st.spinner("Gerando relatório..."):
        response = llm.invoke(prompt.format(input=user_input))

    st.subheader("Relatório Gerado")
    st.markdown(response.content)
