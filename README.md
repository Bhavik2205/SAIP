# SAIP
Smart Autonomous Intelligence Platform


### 🧠 Smart Autonomous Intelligence Platform Blueprint

**Platform Goal:** To generate unique, actionable intelligence by autonomously discovering, filtering, synthesizing, and visualizing complex public data streams, unmasking realities hidden by information complexity and obfuscation.

**Core USP (Unique Selling Proposition):** Generating **"Real Intel"** by connecting disparate, low-visibility data points (e.g., obscure regulatory filings, archived legal documents, subtle changes in vessel patterns) to expose full, hidden networks and activities across multiple sectors.

---

## 🛠️ I. System Architecture & Foundation

The platform is built on reusable, containerized components for portability and stability (local on Mac Mini M4, or future cloud deployment).

| Component | Purpose | Tools | Connection to Intelligence |
| :--- | :--- | :--- | :--- |
| **Docker Ecosystem** | Containerizes all services (Database, Crawler, UI) for isolated, reliable local execution. | Docker / `docker-compose.yml` | **Reliability:** Ensures the intelligence pipeline is never down due to dependency conflicts. |
| **Core Database (Data Lake)** | Persistent, structured storage for all raw and processed data (text, entities, alerts). | PostgreSQL | **Foundation:** The central "brain" where all connections and network maps are stored for rapid querying. |
| **Configuration Layer** | Externalizes all sector-specific targets, keywords, and seed URLs. | `crawler_config.yml` | **Agility:** Allows instantaneous pivot to any sector (Energy, Biotech, Finance) without rewriting code. |

---

## 🤖 II. The Smart Crawler: Autonomous Discovery (The "Eyes and Ears")

This component moves beyond simple scraping to intelligently find and access deep-web content that the public rarely sees.

| Feature | Detailed Functionality | Connection to Intelligence |
| :--- | :--- | :--- |
| **A. Intelligent Seed Injection** | Starts with a small, general set of seed URLs (e.g., major stock exchanges, regulatory bodies, key institutional archives) defined in the config. | **Autonomous Discovery:** Does not rely on a user-provided list of articles; it finds the *sources* itself. |
| **B. Link Filtering Middleware** | **Crucial Logic:** Filters all discovered links, only pursuing those containing high-value keywords (`/filing/`, `arbitration`, `sanctions`, `patent`, `indictment`) or date/version numbers in the URL structure. | **Precision & Efficiency:** Directs the crawler away from noise (login pages, ads) and towards buried documents (legal PDFs, regulatory updates). |
| **C. Deep Recursion Logic** | Configured to dive up to **4 levels deep** within high-value domains (e.g., ICSID archives, SEC EDGAR). | **Non-Public Access:** Necessary to find documents intentionally nested several layers deep, avoiding surface-level reporting. |
| **D. Generalized Extractor** | Uses a cascading hierarchy of generic CSS/XPath selectors to locate the main content body on any site, standardizing the raw text output. | **Reusability & Scale:** Ensures accurate text extraction from any document type, regardless of sector-specific web design. |

---

## 🧠 III. Intelligence Processor: Synthesis and Unmasking (The "Brain")

This component uses AI/ML to transform clean text data into actionable connections, generating the "real intel" by highlighting anomalies and networks.

| Feature | Detailed Functionality | Connection to Intelligence (USP) |
| :--- | :--- | :--- |
| **A. Named Entity Recognition (NER)** | Uses a fine-tuned spaCy model to extract and categorize all **Organizations (ORGs), People (PEOPLE), Geopolitical Entities (GPE), and Dates** from every document. | **Connection Mapping:** Creates the nodes for the network graph, revealing the *actors* involved in a hidden event. |
| **B. Relationship Extraction (RE)** | Advanced NLP to identify the *relationship* between two extracted entities (e.g., "Company X **filed a lawsuit against** Official Y"). | **Unmasking Reality:** Automatically determines *how* entities are connected (legal, financial, political) without human reading. |
| **C. Anomaly Detection Engine** | Scans the database for sudden, sharp changes in keyword frequency, sentiment, or network connections. *Example:* A 500% spike in documents mentioning "Shell Company" and "Panama" in 48 hours. | **Hidden Activity Alert:** This is the core signal for **non-public events** (e.g., rapid setup of sanctions evasion networks) before they hit the news. |
| **D. Cross-Sector Correlation** | Logic to compare entity mentions across different sectors. *Example:* An individual mentioned in a **Biotech patent suit** is also a Director in an **Energy trading firm**. | **Full Picture:** Reveals conflicts of interest, lobbying efforts, or organized activity spanning multiple industries. |

---

## 🖥️ IV. Visualization and Alerting (The "Interface")

The final layer translates complex database connections into descriptive, intuitive visual intelligence, ready for action.

| Component | Task | Tool/Language | Descriptive Visualization Output |
| :--- | :--- | :--- | :--- |
| **Streamlit Dashboard** | Local, browser-based UI displaying key insights, connected directly to the PostgreSQL database. | Streamlit | **Intuitive Interface:** Allows interactive exploration of complex data without needing SQL expertise. |
| **Risk Network Graph** | Displays a real-time graph of connected entities, filtered by sector and risk score. Nodes are ORGs/People; Edges are the relationships (from RE). | Python / NetworkX / Pyvis | **Visual Intelligence:** Visually demonstrates the "real intel"—a hidden network of individuals/companies involved in a single, undisclosed activity.  |
| **Trended Sentiment & Risk Score** | Line charts showing the rolling aggregate sentiment and risk score for a specific entity or sector (e.g., "All Biotech Companies") over the last 90 days. | Python / Plotly | **Investment Signal:** Allows immediate identification of long-term sentiment shifts and growing regulatory risk. |
| **Priority Alert Feed** | A dedicated view showing the latest documents ranked by the **Anomaly Detection Engine's** score. | Streamlit Dataframe | **Actionable Intelligence:** Your daily "briefing" of the highest-value, non-public signals detected by the platform. |
