import streamlit as st
from zelda_kg import ZeldaKG

kg = ZeldaKG()

st.set_page_config(layout="wide")

st.title("Zelda Knowledge RAG with Knowledge Graph")

with st.expander("View system instructions"):
    st.markdown(kg._get_system_message())

if prompt := st.chat_input("Enter a prompt"):
    st.chat_message("user").write(prompt)
    bot_response = kg.get_proposed_cypher(prompt)
    if "MATCH" in bot_response:
        try:
            result = kg.query_database(bot_response)
            st.chat_message("assistant").markdown(f"""The Cypher query generated is:
```cypher
{bot_response}
```
            """)
            st.chat_message("assistant").write(result)
        except Exception as e:
            st.chat_message("assistant").write(f"Error: {e}")
            st.chat_message("assistant").write(bot_response)
    else:
        st.chat_message("assistant").write(bot_response)
