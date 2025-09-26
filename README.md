# 🌊 AI-Driven ChatBOT for Groundwater Data (INGRES)

## 📖 Background
The **Assessment of Dynamic Ground Water Resources of India** is conducted annually by the  
**Central Ground Water Board (CGWB)** and **State/UT Ground Water Departments**, under the coordination of the **Central Level Expert Group (CLEG), DoWR, RD & GR, MoJS**.  

This assessment is managed through **INGRES** (India Ground Water Resource Estimation System), a GIS-based web application developed by **CGWB and IIT Hyderabad** → [INGRES Portal](https://ingres.iith.ac.in/home).  

It provides estimates for:
- Annual groundwater recharge  
- Extractable resources  
- Total extraction  
- Stage of groundwater extraction  

Each **assessment unit (Block/Mandal/Taluk)** is categorized as:  
✔️ Safe  
⚠️ Semi-Critical  
❌ Critical  
🚨 Over-Exploited  

Currently, results are published via the INGRES portal, but retrieving historical data and detailed results is often **challenging** due to the vast dataset.

---

## 💡 Proposed Solution
To improve accessibility, we propose an **AI-driven ChatBOT for INGRES**.  

This intelligent assistant will allow users to:  
- Query groundwater data in **natural language**  
- Access **historical & current assessment results** instantly  
- Get **insights without navigating complex datasets**

---

## ✨ Key Features
- 🤖 **Intelligent Query Handling** – Natural language interface for groundwater estimation data  
- 📊 **Real-time Data Access** – Both current and historical assessments  
- 📈 **Interactive Visualizations** – Graphs, charts, and comparative trends  
- 🌍 **Multilingual Support** – Including Indian regional languages  
- ⚡ **Seamless Integration** – Direct connection with the INGRES database  

---

## 🌟 Impact
The AI-powered ChatBOT will:  
- Simplify **access to groundwater resource data**  
- Support **informed decision-making** for policymakers, researchers, and planners  
- Enhance **public engagement** with accessible insights  
- Make the **INGRES portal more user-friendly, accessible, and effective**  

By combining **AI, data visualization, and multilingual support**, this project aims to **democratize access to groundwater information** in India.  

---

## 🚀 Project Modules (Planned)
1. **Data Preparation** – Collecting, cleaning, and structuring datasets (AY 2024–25 + historical)  
2. **Database & API** – Building a FastAPI backend to serve groundwater data  
3. **AI Query Engine** – Natural language query handling using LLMs & SQL agents  
4. **Frontend Chat Interface** – Interactive chatbot UI with tables & visualizations  
5. **Visualization Layer** – Charts & dashboards for better interpretation  

---

## 📌 Status
🟢 Project Initiation Phase  
- Dataset collection (AY 2024–25)  
- Backend + database setup in progress  

---

## 🤝 Contributing
Contributions are welcome!  
- Fork this repo  
- Create a new branch (`feature/your-feature`)  
- Commit changes  
- Open a Pull Request 🎉  

---

## 📜 License
This project is intended for research and educational purposes.  
Final deployment will follow policies and guidelines from **MoJS, CGWB, and IIT Hyderabad**.  

---

## Canonical header names (LLM-friendly, no synonyms)

To make SQL generation more robust, we derive deterministic, human-readable column names from the original headers and expose them as SQLite views.

- Generator: `src/utils/generate_canonical_header_map.py`
- Output map: `header_flat_csv/INGRES_header_canonical_map.json`
- Convention:
	- Join original header parts (split by `|`) as snake_case
	- Append dimension suffix: `_c`, `_nc`, `_pq`, `_total`
	- Append unit suffix: `_mm`, `_ha_m`, `_percent`
- At runtime, the chatbot creates `v_<table>` views where columns are aliased to the canonical names, and prompts the LLM to prefer these views.

If you update the original header map, re-run the generator to refresh the canonical map.
