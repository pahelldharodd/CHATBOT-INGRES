import os
import re
from typing import List, Tuple
from utils.load_config import LoadConfig
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
import langchain

langchain.debug = True

APPCFG = LoadConfig()


def clean_sql_query(query: str) -> str:
    """
    Cleans Gemini's SQL output:
    - Removes Markdown fences and explanations
    - Strips trailing semicolons
    - Quotes table/column names with invalid chars (hyphens, spaces, etc.)
    """
    query = query.strip()

    # Remove markdown fences like ```sql ... ```
    if query.startswith("```"):
        parts = query.split("```")
        if len(parts) >= 2:
            query = parts[1]
    query = query.replace("sql", "").replace("```", "").strip()

    # Strip trailing semicolon
    if query.endswith(";"):
        query = query[:-1]

    # Quote table names after FROM/JOIN/UPDATE/INTO
    query = re.sub(
        r'\b(FROM|JOIN|UPDATE|INTO)\s+([A-Za-z0-9_\-]+)',
        lambda m: f'{m.group(1)} "{m.group(2)}"' if not m.group(2).isidentifier() else m.group(0),
        query,
        flags=re.IGNORECASE
    )

    # Quote column names in SELECT/DISTINCT/ORDER BY if they contain hyphen/space
    query = re.sub(
        r'\b(SELECT|DISTINCT|ORDER BY|GROUP BY)\s+([A-Za-z0-9_\-]+)',
        lambda m: f'{m.group(1)} "{m.group(2)}"' if not m.group(2).isidentifier() else m.group(0),
        query,
        flags=re.IGNORECASE
    )

    return query.strip()


class ChatBot:
    """
    A ChatBot class capable of responding to messages using different modes of operation.
    Works with Gemini for SQL Q&A and RAG.
    """

    @staticmethod
    def respond(chatbot: List, message: str, chat_type: str, app_functionality: str) -> Tuple:
        if app_functionality == "Chat":

            # # 1. Q&A with stored SQL DB (.sql schema)
            # if chat_type == "Q&A with stored SQL-DB":
            #     if os.path.exists(APPCFG.sqldb_directory):
            #         db = SQLDatabase.from_uri(f"sqlite:///{APPCFG.sqldb_directory}")

            #         # Step 1: Ask Gemini to generate SQL query
            #         prompt = f"""
            #         You are an AI that ONLY writes SQL queries.
            #         Database tables: {db.get_usable_table_names()}.
            #         User question: {message}
            #         Return ONLY a valid SQL query. No explanations, no Markdown.
            #         """
            #         sql_response = APPCFG.gemini_llm.generate_content(prompt)
            #         sql_query = clean_sql_query(sql_response.text)
            #         print("Generated SQL:", sql_query)

            #         # Step 2: Execute SQL
            #         try:
            #             result = db.run(sql_query)
            #         except Exception as e:
            #             chatbot.append((message, f"Error running SQL: {e}"))
            #             return "", chatbot, None

            #         # Step 3: Ask Gemini to format final answer
            #         answer_prompt = f"""
            #         User question: {message}
            #         SQL Query: {sql_query}
            #         SQL Result: {result}
            #         Answer the user question clearly.
            #         """
            #         answer_response = APPCFG.gemini_llm.generate_content(answer_prompt)
            #         response = answer_response.text

            #     else:
            #         chatbot.append((message, "SQL DB does not exist. Please first create the 'sqldb.db'."))
            #         return "", chatbot, None

            # 2. Q&A with Uploaded/Stored CSV/XLSX → SQL DB
            if chat_type in ["Q&A with Uploaded CSV/XLSX SQL-DB", "Q&A with stored CSV/XLSX SQL-DB"]:
                if chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB":
                    if os.path.exists(APPCFG.uploaded_files_sqldb_directory):
                        engine = create_engine(f"sqlite:///{APPCFG.uploaded_files_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                    else:
                        chatbot.append((message, "Uploaded SQL DB not found. Please upload CSV/XLSX first."))
                        return "", chatbot, None

                elif chat_type == "Q&A with stored CSV/XLSX SQL-DB":
                    if os.path.exists(APPCFG.stored_csv_xlsx_sqldb_directory):
                        engine = create_engine(f"sqlite:///{APPCFG.stored_csv_xlsx_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                    else:
                        chatbot.append((message, "Stored SQL DB not found. Please run `prepare_csv_xlsx_sqlitedb.py`."))
                        return "", chatbot, None

                # Same 3-step SQL process
                prompt = f"""
                You are an AI that ONLY writes SQL queries.
                Database tables: {db.get_usable_table_names()}.
                User question: {message}
                Return ONLY a valid SQL query. No explanations, no Markdown.
                """
                sql_response = APPCFG.gemini_llm.generate_content(prompt)
                sql_query = clean_sql_query(sql_response.text)
                print("Generated SQL:", sql_query)

                try:
                    result = db.run(sql_query)
                except Exception as e:
                    chatbot.append((message, f"Error running SQL: {e}"))
                    return "", chatbot, None

                answer_prompt = f"""
                User question: {message}
                SQL Query: {sql_query}
                SQL Result: {result}
                Answer the user question clearly.
                """
                answer_response = APPCFG.gemini_llm.generate_content(answer_prompt)
                response = answer_response.text

            # # 3. RAG with stored ChromaDB
            # elif chat_type == "RAG with stored CSV/XLSX ChromaDB":
            #     # Step 1: Get embeddings from Gemini
            #     embed = APPCFG.gemini_embed.embed_content(
            #         model=APPCFG.embedding_model_name,
            #         content=message
            #     )
            #     query_embeddings = embed["embedding"]

            #     # Step 2: Search Chroma
            #     vectordb = APPCFG.chroma_client.get_collection(name=APPCFG.collection_name)
            #     results = vectordb.query(query_embeddings=query_embeddings, n_results=APPCFG.top_k)

            #     # Step 3: Ask Gemini to answer with context
            #     prompt = f"""
            #     User's question: {message} 
            #     Search results: {results}
            #     Answer the question using the results.
            #     """
            #     llm_response = APPCFG.gemini_llm.generate_content(
            #         [APPCFG.rag_llm_system_role, prompt],
            #         generation_config={"temperature": APPCFG.temperature}
            #     )
            #     response = llm_response.text

            # Append response
            chatbot.append((message, response))
            return "", chatbot

        else:
            return "", chatbot
