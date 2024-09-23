import os

import streamlit as st
from dotenv import load_dotenv
from zelda_kg import ZeldaKG, format_results_as_markdown_table

load_dotenv()

kg = ZeldaKG()

st.set_page_config(layout="wide")

st.title("Zelda Knowledge RAG with Knowledge Graph")


if prompt := st.text_input("Enter a question"):
    system_message = kg.get_cypher_system_prompt()
    cypher_query = kg.get_candidate_cypher_query(prompt)
    results_query = kg.query_database(cypher_query)
    formatted_results = format_results_as_markdown_table(results_query)
    response = kg.generate_response(prompt, formatted_results)

    st.markdown(response)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Cypher Query")
        st.code(cypher_query, language="cypher")

    with col2:
        st.markdown("### Results")
        st.markdown(formatted_results)
