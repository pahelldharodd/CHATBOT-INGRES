import os
import re
from typing import List, Tuple
from utils.load_config import LoadConfig
from utils.canonical_schema import ensure_canonical_views, build_schema_context
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


def rewrite_sql_to_use_views(sql: str, base_tables: List[str], canonical_views: List[str]) -> str:
    """
    Replace base table references with their v_* view equivalents if present.
    This allows queries that use canonical column names to work even if the LLM
    incorrectly targeted a base table.
    """
    view_set = set(canonical_views)
    mapping = {}
    for t in base_tables:
        v = f"v_{t}"
        if v in view_set:
            mapping[t] = v

    def repl_table(match: re.Match) -> str:
        kw = match.group(1)
        name = match.group(2)
        # Strip quotes if present
        unquoted = name.strip('"')
        repl = mapping.get(unquoted)
        if repl:
            return f'{kw} "{repl}"'
        return match.group(0)

    # FROM/JOIN replacements (case-insensitive)
    sql = re.sub(r'\b(FROM|JOIN)\s+"?([A-Za-z0-9_\-\.]+)"?', repl_table, sql, flags=re.IGNORECASE)
    return sql


def normalize_where_filters(sql: str) -> str:
    """
    Make common filters robust against dataset formatting:
    - STATE/DISTRICT equality becomes case-insensitive using UPPER(...)=UPPER('...')
    - YEAR = 'YYYY' becomes a fuzzy match for textual ranges like 'YYYY-YYYY+1'
    Applies to both canonical (lowercase) and original (uppercase) column names.
    """
    def ci_equal(m: re.Match) -> str:
        col = m.group(1)
        val = m.group(2)
        return f"UPPER({col}) = UPPER({val})"

    # Case-insensitive equality on state/district
    sql = re.sub(r"\b(STATE|state|DISTRICT|district)\s*=\s*('(?:[^']|'' )*')", ci_equal, sql)

    # YEAR matching: if equality against 4-digit year, turn into LIKE-based match
    def year_match(m: re.Match) -> str:
        col = m.group(1)
        year = m.group(2)
        return f"({col} LIKE '{year}%' OR {col} LIKE '%{year}%')"

    sql = re.sub(r"\b(YEAR|year)\s*=\s*'((?:19|20)\d{2})'", year_match, sql)
    return sql


class ChatBot:
    """
    A ChatBot class capable of responding to messages using different modes of operation.
    Works with Gemini for SQL Q&A and RAG.
    """

    @staticmethod
    def respond(chatbot: List, message: str, chat_type: str, app_functionality: str) -> Tuple:
        # Use LLM to detect greetings/small talk and handle them gracefully
        greeting_check_prompt = f"""
        You are an intent classifier for a chatbot. Classify the following user message as either 'greeting', 'goodbye', 'thanks', or 'data_query'.
        Only output one of: greeting, goodbye, thanks, data_query.
        User message: {message}
        """
        intent_response = APPCFG.gemini_llm.generate_content(greeting_check_prompt)
        intent = intent_response.text.strip().lower()
        
        if intent == "greeting":
            response = "Hello! How can I help you with groundwater data or queries today?"
            chatbot.append({"role": "user", "content": message})
            chatbot.append({"role": "assistant", "content": response})
            return "", chatbot
        elif intent == "goodbye":
            response = "Goodbye! If you have more questions, feel free to ask anytime."
            chatbot.append({"role": "user", "content": message})
            chatbot.append({"role": "assistant", "content": response})
            return "", chatbot
        elif intent == "thanks":
            response = "You're welcome! Let me know if you need anything else."
            chatbot.append({"role": "user", "content": message})
            chatbot.append({"role": "assistant", "content": response})
            return "", chatbot
        # ...existing code...
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
            if chat_type in ["📊 Database Query Assistant - INGRES SQL Data", "Q&A with Uploaded CSV/XLSX SQL-DB", "Q&A with stored CSV/XLSX SQL-DB"]:
                if chat_type == "Q&A with Uploaded CSV/XLSX SQL-DB":
                    if os.path.exists(APPCFG.uploaded_files_sqldb_directory):
                        engine = create_engine(f"sqlite:///{APPCFG.uploaded_files_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                    else:
                        error_msg = "Uploaded SQL DB not found. Please upload CSV/XLSX first."
                        chatbot.append({"role": "user", "content": message})
                        chatbot.append({"role": "assistant", "content": error_msg})
                        return "", chatbot

                elif chat_type in ["📊 Database Query Assistant - INGRES SQL Data", "Q&A with stored CSV/XLSX SQL-DB"]:
                    if os.path.exists(APPCFG.stored_csv_xlsx_sqldb_directory):
                        engine = create_engine(f"sqlite:///{APPCFG.stored_csv_xlsx_sqldb_directory}")
                        db = SQLDatabase(engine=engine)
                    else:
                        error_msg = "Stored SQL DB not found. Please run `prepare_csv_xlsx_sqlitedb.py`."
                        chatbot.append({"role": "user", "content": message})
                        chatbot.append({"role": "assistant", "content": error_msg})
                        return "", chatbot

                # Ensure canonical views exist for this DB (uses header_flat_csv/INGRES_header_canonical_map.json)
                try:
                    from pathlib import Path
                    # Prefer NL-friendly canonical names if available
                    canonical_map_nl = Path(__file__).resolve().parents[2] / "header_flat_csv" / "INGRES_header_canonical_map_nl.json"
                    canonical_map_default = Path(__file__).resolve().parents[2] / "header_flat_csv" / "INGRES_header_canonical_map.json"
                    canonical_map_path = canonical_map_nl if canonical_map_nl.exists() else canonical_map_default
                    header_map_path = Path(__file__).resolve().parents[2] / "header_flat_csv" / "INGRES_header_map.json"
                    created_views = ensure_canonical_views(engine, str(canonical_map_path), str(header_map_path))
                    schema_ctx = build_schema_context(engine, str(canonical_map_path), str(header_map_path))
                except Exception as e:
                    created_views = []
                    schema_ctx = {}

                # Same 3-step SQL process
                # Prefer querying canonical views if available; expose both for flexibility
                usable_tables = db.get_usable_table_names()
                canonical_views = [t for t in usable_tables if str(t).startswith("v_")]
                base_tables = [t for t in usable_tables if not str(t).startswith("v_")]

                # Keep this as a plain string so braces are not interpreted by f-strings
                synonyms_hint = """
                {
                    "rain|rainfall|precipitation|rf": "rainfall_mm_total",
                    "average rainfall|avg rainfall": "AVG(rainfall_mm_total)",
                    "groundwater recharge|recharge": "groundwater_recharge_total_ham",
                    "recharge from rain|rain recharge": "groundwater_recharge_from_rain_total_ham",
                    "extraction|withdrawal|pumpage": "groundwater_extraction_irrigation_total_ham + groundwater_extraction_domestic_total_ham + groundwater_extraction_industrial_total_ham",
                    "stage of extraction|exploitation": "groundwater_extraction_stage_total_percent",
                    "area|geographical area": "area_total_ha"
                }
                """

                prompt = f"""
                                You are an AI that ONLY writes SQL queries.

                                Available tables (use EXACT identifiers, nothing else): {canonical_views}
                                IMPORTANT:
                                - Only use the tables listed above (v_* views). Do NOT query base tables.
                                - Do not add extra words like 'database' or 'table' around identifiers.
                                - Use only canonical column names when selecting from v_* views.

                                Natural language → columns and defaults:
                                - If the user doesn't specify C/NC/PQ, default to the Total column for that metric.
                                - Rainfall / precipitation → rainfall_mm_total (or rainfall_mm_c / rainfall_mm_nc / rainfall_mm_pq if explicitly requested).
                                - Geographical area → area_total_ha; Hilly area → area_hilly_ha; Recharge-worthy area → area_recharge_worthy_*_ha.
                                - Groundwater recharge (overall) → groundwater_recharge_total_ham.
                                  • From rainfall → groundwater_recharge_from_rain_total_ham
                                  • From canals → groundwater_recharge_from_canals_total_ham
                                  • From surface water irrigation → groundwater_recharge_from_surface_irrigation_total_ham
                                  • From groundwater irrigation → groundwater_recharge_from_groundwater_irrigation_total_ham
                                  • From tanks/ponds → groundwater_recharge_from_tanks_ponds_total_ham
                                  • From water conservation structures → groundwater_recharge_from_wcs_total_ham
                                  • From pipelines → groundwater_recharge_from_pipelines_total_ham
                                  • From sewage/flash flood channels → groundwater_recharge_from_sewage_flood_total_ham
                                - Base flow → base_flow_total_ham; Stream recharge → stream_recharge_total_ham; Lateral/Vertical flows → lateral_flow_total_ham / vertical_flow_total_ham.
                                - Evaporation / Transpiration / Evapotranspiration → evaporation_total_ham / transpiration_total_ham / evapotranspiration_total_ham.
                                - Annual recharge → annual_groundwater_recharge_total_ham; Environmental flows → environmental_flows_total_ham; Extractable resource → extractable_groundwater_resource_total_ham.
                                - Groundwater extraction (uses): domestic → groundwater_extraction_domestic_total_ham; industrial → groundwater_extraction_industrial_total_ham; irrigation → groundwater_extraction_irrigation_total_ham.
                                  • If user asks for total extraction across uses, SUM the three sector totals in SQL.
                                - Stage of extraction / exploitation → groundwater_extraction_stage_total_percent.
                                - Net available groundwater → groundwater_available_future_total_ham.
                                - Unconfined storage (fresh/saline) → unconfined_groundwater_total_fresh_ham / unconfined_groundwater_total_saline_ham.
                                - Semi-confined storage (fresh/saline) → semi_confined_groundwater_total_fresh_ham / semi_confined_groundwater_total_saline_ham.
                                - Total groundwater availability in area (fresh/saline) → groundwater_total_in_area_fresh_ham / groundwater_total_in_area_saline_ham.

                                Aggregations and units (be precise):
                                - Words like average/avg → use AVG(); total/sum → SUM(); maximum → MAX(); minimum → MIN().
                                - Units: rainfall in mm, areas in ha, volumes/stocks/flows in ha.m (ham), stage in percent.
                                - Prefer COALESCE() inside aggregates to ignore NULLs.

                                Synonyms (map user phrasing to columns):
                                {synonyms_hint}

                                Querying tips to avoid empty results:
                                - STATE and DISTRICT values are stored as uppercase strings. For equality, use case-insensitive match, e.g.:
                                    WHERE UPPER(STATE) = UPPER('Andhra Pradesh')
                                    or append COLLATE NOCASE:
                                    WHERE STATE = 'Andhra Pradesh' COLLATE NOCASE
                                - YEAR is stored as text like '2022-2023'. If user asks for year 2022, match using LIKE:
                                    WHERE YEAR LIKE '2022-%' OR YEAR LIKE '%2022%'
                                - Geography defaults: if the user mentions only STATE, filter STATE and aggregate across districts; if they say "by district/state", add GROUP BY DISTRICT or STATE accordingly. If they say "by year", add GROUP BY YEAR.

                                Schema context (column mapping):
                                The following JSON-like mapping lists, per view, the columns with their canonical name, original column key, and human-readable label.
                                Use the canonical column names shown here when selecting from v_* views.
                                {schema_ctx}

                                User question: {message}
                                Return ONLY a valid SQL query. No explanations, no Markdown.
                                """
                # Use robust fallback generation to avoid model version 404s
                sql_response = APPCFG.generate_content_with_fallback(prompt)
                sql_query = clean_sql_query(sql_response.text)
                # Safety: rewrite any lingering base table references to v_* views
                sql_query = rewrite_sql_to_use_views(sql_query, base_tables, canonical_views)
                # Normalize common filters to avoid empty-result pitfalls
                sql_query = normalize_where_filters(sql_query)
                print("Generated SQL:", sql_query)

                try:
                    result = db.run(sql_query)
                except Exception as e:
                    # Retry once: if the error could be due to table targeting, try rewritten SQL
                    try:
                        sql_query_retry = rewrite_sql_to_use_views(sql_query, base_tables, canonical_views)
                        if sql_query_retry != sql_query:
                            result = db.run(sql_query_retry)
                            sql_query = sql_query_retry
                        else:
                            raise e
                    except Exception:
                        error_msg = f"Error running SQL: {e}"
                        chatbot.append({"role": "user", "content": message})
                        chatbot.append({"role": "assistant", "content": error_msg})
                        return "", chatbot

                answer_prompt = f"""
                User question: {message}
                SQL Query: {sql_query}
                SQL Result: {result}
                Answer the user question clearly.
                """
                answer_response = APPCFG.generate_content_with_fallback(answer_prompt)
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

            # 3. Knowledge Assistant for CGWB Reports & Terms
            elif chat_type == "📚 Knowledge Assistant - CGWB Reports & Terms":
                # Simple knowledge-based responses for now
                knowledge_prompt = f"""
                You are a knowledgeable assistant specializing in CGWB (Central Ground Water Board) reports and groundwater technical terms.
                
                User question: {message}
                
                Please provide a comprehensive answer about groundwater terminology, CGWB assessment procedures, hydrogeological concepts, or related technical information.
                Focus on being educational and informative while maintaining accuracy.
                """
                knowledge_response = APPCFG.generate_content_with_fallback(knowledge_prompt)
                response = knowledge_response.text
            
            else:
                # Fallback for unknown chat types
                response = "I'm sorry, I don't understand that mode. Please select either 'Database Query Assistant' or 'Knowledge Assistant' from the settings."

            # Append response
            chatbot.append({"role": "user", "content": message})
            chatbot.append({"role": "assistant", "content": response})
            return "", chatbot

        else:
            return "", chatbot
