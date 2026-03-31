# Web Mining & Semantics — Knowledge Graph Construction, Alignment, Reasoning & RAG

Final project for **ESILV — DIA A4 (2026)** on **football / FIFA governance & institutional documentation**.

This repository contains the full pipeline developed for the Web Mining & Semantics project:
- web crawling and text extraction
- named entity recognition
- RDF knowledge graph construction
- ontology-based reasoning
- knowledge graph embeddings
- retrieval over RDF/SPARQL with a local LLM through **Ollama**

The repository structure and project scope below are aligned with the current project tree and report content.  

---

## Project Overview

The goal of this project is to build a **domain-specific knowledge graph** from official and encyclopedic football governance sources, then use it for:
- **entity extraction**
- **knowledge graph construction**
- **entity alignment / expansion**
- **symbolic reasoning**
- **embedding-based reasoning**
- **RAG-like question answering over SPARQL**

The chosen domain is **FIFA governance and institutional football documentation**.

Main source families used in the project:
- official FIFA publications
- Laws of the Game documentation
- encyclopedic references related to FIFA, IFAB, UEFA, World Cup, VAR, etc.

---

## Repository Structure

```text
.
├── Notebook
│   ├── Lab1_Crawling_NLP.ipynb
│   ├── Lab4_KB_Construction.ipynb
│   ├── Lab5_Knowledge_Graph.ipynb
│   ├── Lab6_rag_sparql_gen.py
│   ├── family.owl
│   └── requirements.txt
├── data
│   ├── Lab 1
│   │   ├── crawler_output.jsonl
│   │   └── extracted_knowledge.csv
│   ├── Lab 5
│   │   ├── test.txt
│   │   ├── test_sub.txt
│   │   ├── train_sub.txt
│   │   ├── valid.txt
│   │   └── valid_sub.txt
│   └── dossier sans titre
└── kg_artifacts
    ├── alignment.ttl
    ├── alignment_mapping.csv
    ├── evaluation_results.json
    ├── expanded_kb.nt
    ├── ontology.ttl
    └── statistics_report.json
```

---

## What Each File Does

### `Notebook/`

#### `Lab1_Crawling_NLP.ipynb`
Notebook for:
- crawling seed URLs
- checking crawl permissions / robots logic
- extracting main text content
- running NER
- exporting raw extraction outputs

#### `Lab4_KB_Construction.ipynb`
Notebook for:
- transforming extracted entities and relations into RDF triples
- defining classes and predicates
- building the private knowledge graph
- exporting graph artifacts

#### `Lab5_Knowledge_Graph.ipynb`
Notebook for:
- entity linking
- predicate alignment
- KG expansion
- training / evaluating embedding models
- generating metrics and graph artifacts

#### `Lab6_rag_sparql_gen.py`
Python script for:
- connecting a local LLM through **Ollama**
- prompting the model to generate SPARQL
- querying the RDF graph
- evaluating generated answers against gold SPARQL queries

#### `family.owl`
Small ontology used for SWRL / rule-based reasoning experiments.

#### `requirements.txt`
Python dependencies for the project.

---

### `data/`

#### `data/Lab 1/crawler_output.jsonl`
Raw or semi-processed crawl output.

#### `data/Lab 1/extracted_knowledge.csv`
Extracted entities / knowledge candidates from Lab 1.

#### `data/Lab 5/`
Contains train / validation / test splits used for KG embedding experiments.

Files:
- `train_sub.txt`
- `valid.txt`
- `valid_sub.txt`
- `test.txt`
- `test_sub.txt`

---

### `kg_artifacts/`

#### `alignment.ttl`
RDF/Turtle serialization of aligned graph information.

#### `alignment_mapping.csv`
Mapping table between private entities / predicates and external aligned resources.

#### `evaluation_results.json`
Evaluation outputs for SPARQL / RAG testing.

#### `expanded_kb.nt`
Final expanded knowledge graph in N-Triples format.

#### `ontology.ttl`
Ontology / schema-level graph description.

#### `statistics_report.json`
Summary statistics for triples, entities, relations, alignment, etc.

---

## Main Pipeline

## 1) Crawl and extract content
The project starts by crawling a small curated set of URLs related to FIFA governance and football institutional knowledge.

Typical tasks:
- fetch page content
- clean boilerplate
- keep only the main textual zone
- store extracted text

---

## 2) Perform NER and relation extraction
The text is processed with **spaCy** to detect entities such as:
- `PERSON`
- `ORG`
- `GPE`

These entities are then normalized and reused in the knowledge graph construction stage.

---

## 3) Build the RDF knowledge graph
The project creates a private namespace and models:
- persons
- organizations
- places
- relations extracted from text

The graph is serialized into RDF files for later reasoning and querying.

---

## 4) Align and expand the graph
A subset of entities is linked to external resources (for example Wikidata), then the graph is expanded with additional triples.

This step improves:
- graph coverage
- graph connectivity
- downstream embedding performance

---

## 5) Apply reasoning
Two reasoning paradigms are explored:
- **rule-based reasoning** with ontology / SWRL logic
- **embedding-based reasoning** with KGE models such as TransE and DistMult

---

## 6) Query the graph with SPARQL + local LLM
The final step uses a **local LLM served by Ollama** to translate natural language questions into SPARQL queries.

The generated SPARQL is then executed on the RDF graph.

---

## Installation

## 1) Clone the repository

```bash
git clone https://github.com/Bvder92/Projet-chatbot-fifa
cd Projet-chatbot-fifa
```

If you created the repo manually on GitHub and already have the folder locally:

```bash
cd /path/to/your/project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/Bvder92/Projet-chatbot-fifa
git push -u origin main
```

---

## 2) Create a virtual environment

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 3) Install Python dependencies

```bash
pip install --upgrade pip
pip install -r Notebook/requirements.txt
```

If your `requirements.txt` is elsewhere, adapt the path.

---

## 4) Install Jupyter support

If needed:

```bash
pip install notebook jupyterlab ipykernel
```

Then launch:

```bash
jupyter lab
```

or

```bash
jupyter notebook
```

---

## Ollama Installation

This project uses a **local LLM via Ollama** for SPARQL generation.

### What is Ollama?
Ollama is a local runtime that lets you download and serve open LLMs directly on your machine.

The project report indicates usage of:
- **`llama3.2:1b`**
- local endpoint: `http://localhost:11434`

---

## Install Ollama on macOS

### Option 1 — official installer
1. Go to the official Ollama website
2. Download the macOS installer
3. Install the app
4. Open Ollama once so the service starts

### Option 2 — Homebrew
```bash
brew install ollama
```

Then start the service if needed:

```bash
ollama serve
```

---

## Install Ollama on Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then:

```bash
ollama serve
```

---

## Install Ollama on Windows

1. Download Ollama from the official website
2. Install it
3. Open the app / service
4. Verify it is running

---

## Pull the model used in the project

```bash
ollama pull llama3.2:1b
```

You can verify installed models with:

```bash
ollama list
```

Test the model:

```bash
ollama run llama3.2:1b
```

If your script expects the default Ollama endpoint, make sure this works:

```bash
curl http://localhost:11434/api/tags
```

If it returns model information, Ollama is running correctly.

---

## Recommended alternatives

The report shows that `llama3.2:1b` is too weak for reliable NL-to-SPARQL generation.  
If your machine allows it, try:

```bash
ollama pull llama3:8b
```

or

```bash
ollama pull mistral:7b
```

Then update the model name in the Python script.

---

## Running the Project

## Step 1 — Run crawling / extraction
Open and run:

```bash
jupyter lab
```

Then execute:

- `Notebook/Lab1_Crawling_NLP.ipynb`

Expected outputs:
- crawl results
- extracted entities
- cleaned textual data

---

## Step 2 — Build the KG
Run:

- `Notebook/Lab4_KB_Construction.ipynb`

Expected outputs:
- RDF triples
- ontology artifacts
- graph serializations

---

## Step 3 — Expand / align / evaluate KG
Run:

- `Notebook/Lab5_Knowledge_Graph.ipynb`

Expected outputs:
- aligned entities
- expanded graph
- embedding training data
- evaluation metrics

---

## Step 4 — Launch local RAG / SPARQL generation
Make sure:
- Ollama is running
- the model is pulled
- the graph file exists
- Python dependencies are installed

Then run:

```bash
python Notebook/Lab6_rag_sparql_gen.py
```

---

## Expected Inputs / Outputs

### Inputs
- crawled FIFA / football governance pages
- extracted entity files
- alignment resources
- ontology files
- KG split files

### Outputs
- RDF graph files (`.ttl`, `.nt`)
- statistics reports
- alignment mappings
- evaluation JSON results
- SPARQL / RAG evaluation outputs

---

## Dependencies

Typical dependencies for this kind of pipeline include:

- `trafilatura`
- `spacy`
- `pandas`
- `rdflib`
- `owlready2`
- `pykeen`
- `requests`
- `httpx`
- `scikit-learn`
- `matplotlib`
- `jupyter`

Install a spaCy model if needed:

```bash
python -m spacy download en_core_web_sm
```

If the project specifically requires another model, adapt accordingly.

---

## Example End-to-End Setup

```bash
git clone https://github.com/Bvder92/Projet-chatbot-fifa
cd Projet-chatbot-fifa

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r Notebook/requirements.txt
pip install notebook jupyterlab ipykernel

python -m spacy download en_core_web_sm

brew install ollama          # macOS with Homebrew
ollama serve                 # in a separate terminal if needed
ollama pull llama3.2:1b

jupyter lab
```

Then:
1. run the notebooks in order
2. verify that `kg_artifacts/expanded_kb.nt` exists
3. run:

```bash
python Notebook/Lab6_rag_sparql_gen.py
```

## Ollama does not answer
Check that the service is running:

```bash
ollama list
curl http://localhost:11434/api/tags
```

If not:

```bash
ollama serve
```

---

## The LLM generates invalid SPARQL
This is expected with very small models like `llama3.2:1b`.  
Use a stronger model such as:
- `llama3:8b`
- `mistral:7b`

---

## Jupyter kernel / package issues
Always verify that your notebook runs inside the correct environment:

```bash
which python
python --version
pip --version
```

Install the environment as a Jupyter kernel if needed:

```bash
python -m ipykernel install --user --name webdm_env --display-name "Python (webdm_env)"
```

---

## Suggested README Improvements You Can Add Later

You can still strengthen this repo by adding:
- screenshots of notebook outputs
- a schema diagram of the ontology
- sample SPARQL queries
- one screenshot of Ollama running locally
- one table of embedding results
- a short “Results” section with the main project numbers

---

## Results Summary

From the project report, the repository reaches the following outcomes:
- a private + expanded football governance KB
- RDF artifacts and ontology files
- entity linking and predicate alignment
- embedding experiments with TransE and DistMult
- local SPARQL generation tests with Ollama

A key takeaway is that the graph pipeline works, but the **1B LLM is the main bottleneck** for reliable SPARQL generation.

---

## Authors

- **Badr Agrad**
- **Ilyes Ben Younes**

ESILV — DIA A4 — 2026

---

## License

Add the license chosen for your repository here.

Example:

```text
MIT License
```

Or, if this is only for academic submission:

```text
Academic project — ESILV, 2026
```
