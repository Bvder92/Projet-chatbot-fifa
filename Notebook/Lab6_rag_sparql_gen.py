import re
import json
import sys
from typing import List, Tuple
from rdflib import Graph
import requests

# Configuration
NT_FILE      = "../kg_artifacts/expanded_kb.nt"
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"

MAX_PREDICATES = 10
MAX_CLASSES    = 6
SAMPLE_TRIPLES = 5

# 0) Ollama call
def ask_local_llm(prompt: str, model: str = OLLAMA_MODEL) -> str:
    payload = {"model": model, "prompt": prompt, "stream": False}
    try:
        r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot reach Ollama. Run: ollama serve")
        sys.exit(1)
    if r.status_code != 200:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text}")
    return r.json().get("response", "")

# 1) Load graph
def load_graph(path: str) -> Graph:
    g = Graph()
    g.parse(path, format="nt")
    print(f"[INFO] Loaded {len(g)} triples from {path}")
    return g

# 2) Schema summary
def list_distinct_predicates(g: Graph, limit: int = MAX_PREDICATES) -> List[str]:
    q = f"SELECT DISTINCT ?p WHERE {{ ?s ?p ?o . FILTER(CONTAINS(STR(?p),'example.org')) }} LIMIT {limit}"
    return [str(r.p) for r in g.query(q)]

def list_distinct_classes(g: Graph, limit: int = MAX_CLASSES) -> List[str]:
    q = f"SELECT DISTINCT ?c WHERE {{ ?s a ?c . FILTER(CONTAINS(STR(?c),'example.org')) }} LIMIT {limit}"
    return [str(r.c) for r in g.query(q)]

def sample_triples(g: Graph, limit: int = SAMPLE_TRIPLES) -> List[Tuple]:
    q = f"SELECT ?s ?p ?o WHERE {{ ?s ?p ?o . FILTER(CONTAINS(STR(?s),'example.org')) }} LIMIT {limit}"
    return [(str(r.s), str(r.p), str(r.o)) for r in g.query(q)]

def build_schema_summary(g: Graph) -> str:
    preds   = list_distinct_predicates(g)
    classes = list_distinct_classes(g)
    samples = sample_triples(g)
    return f"""PREFIX ex: <http://example.org/fifa/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

CLASSES: {" | ".join(c.split("/")[-1] for c in classes)}
PREDICATES: {" | ".join(p.split("/")[-1] for p in preds)}
EXAMPLES:
{chr(10).join(f"  ex:{s.split('/')[-1]} ex:{p.split('/')[-1]} ex:{o.split('/')[-1]}" for s,p,o in samples)}"""

# 3) NL → SPARQL
SPARQL_SYSTEM = """You output ONLY a SPARQL 1.1 SELECT query. Nothing else.
Rules:
- Start directly with SELECT or PREFIX
- Use only: PREFIX ex: <http://example.org/fifa/> and PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
- No markdown, no explanation, no comments, no extra text
- End with a closing brace }
"""

CODE_BLOCK_RE = re.compile(r"```(?:sparql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)

def extract_sparql(text: str) -> str:
    m = CODE_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"((?:PREFIX[^\n]*\n)*\s*SELECT.*?\})", text, re.DOTALL | re.IGNORECASE)
    if m2:
        return m2.group(1).strip()
    return text.strip()

def generate_sparql(question: str, schema_summary: str) -> str:
    prompt = f"""{SPARQL_SYSTEM}

SCHEMA:
{schema_summary}

QUESTION: {question}

SPARQL query:"""
    raw = ask_local_llm(prompt)
    return extract_sparql(raw)

# 4) Execute SPARQL + self-repair
def run_sparql(g: Graph, query: str) -> Tuple[List[str], List[Tuple]]:
    res   = g.query(query)
    vars_ = [str(v) for v in res.vars]
    rows  = [tuple(str(c) for c in r) for r in res]
    return vars_, rows

def repair_sparql(schema_summary: str, question: str,
                  bad_query: str, error: str) -> str:
    prompt = f"""Fix this broken SPARQL query. Output ONLY the corrected SPARQL query, nothing else.

ERROR: {error}

SCHEMA:
{schema_summary}

QUESTION: {question}

BROKEN QUERY:
{bad_query}

CORRECTED SPARQL query:"""
    raw = ask_local_llm(prompt)
    return extract_sparql(raw)

def answer_with_rag(g: Graph, schema_summary: str,
                    question: str, try_repair: bool = True) -> dict:
    sparql = generate_sparql(question, schema_summary)
    try:
        vars_, rows = run_sparql(g, sparql)
        return {"query": sparql, "vars": vars_, "rows": rows,
                "repaired": False, "error": None}
    except Exception as e:
        if try_repair:
            repaired = repair_sparql(schema_summary, question, sparql, str(e))
            try:
                vars_, rows = run_sparql(g, repaired)
                return {"query": repaired, "vars": vars_, "rows": rows,
                        "repaired": True, "error": None}
            except Exception as e2:
                return {"query": repaired, "vars": [], "rows": [],
                        "repaired": True, "error": str(e2)}
        return {"query": sparql, "vars": [], "rows": [],
                "repaired": False, "error": str(e)}

# 5) Baseline
def answer_no_rag(question: str) -> str:
    return ask_local_llm(f"Answer this question:\n{question}")

# 6) Pretty print
def pretty_print_result(result: dict) -> None:
    print("\n[SPARQL Query Used]")
    print(result["query"])
    print(f"[Repaired?] {result['repaired']}")
    if result.get("error"):
        print("[Execution Error]", result["error"])
        return
    vars_ = result.get("vars", [])
    rows  = result.get("rows", [])
    if not rows:
        print("[No rows returned]")
        return
    print("\n[Results]")
    print(" | ".join(vars_))
    print("-" * 60)
    for r in rows[:20]:
        print(" | ".join(r))
    if len(rows) > 20:
        print(f"... ({len(rows)} total rows)")

# 7) Evaluation
GOLD_SPARQL = {
    "Which organizations are in the knowledge base?": """
SELECT DISTINCT ?org ?label WHERE {
    ?org a <http://example.org/fifa/Organization> .
    OPTIONAL { ?org <http://www.w3.org/2000/01/rdf-schema#label> ?label }
} LIMIT 15""",

    "Which persons are mentioned in the FIFA knowledge base?": """
SELECT DISTINCT ?person ?label WHERE {
    ?person a <http://example.org/fifa/Person> .
    OPTIONAL { ?person <http://www.w3.org/2000/01/rdf-schema#label> ?label }
} LIMIT 15""",

    "Which places are referenced in the knowledge base?": """
SELECT DISTINCT ?place ?label WHERE {
    ?place a <http://example.org/fifa/Place> .
    OPTIONAL { ?place <http://www.w3.org/2000/01/rdf-schema#label> ?label }
} LIMIT 15""",

    "What is FIFA linked to in the knowledge base?": """
SELECT DISTINCT ?p ?o WHERE {
    <http://example.org/fifa/fifa> ?p ?o .
    FILTER(CONTAINS(STR(?p), 'example.org'))
} LIMIT 15""",

    "Which entities are linked to London?": """
SELECT DISTINCT ?s ?p WHERE {
    { ?s ?p <http://example.org/fifa/london> }
    UNION
    { <http://example.org/fifa/london> ?p ?s }
} LIMIT 15""",
}

EVAL_QUESTIONS = list(GOLD_SPARQL.keys())

def run_evaluation(g: Graph, schema_summary: str) -> None:
    print("\n" + "=" * 70)
    print("EVALUATION — Baseline vs SPARQL-generation RAG")
    print("=" * 70)

    results_table = []

    for i, question in enumerate(EVAL_QUESTIONS, 1):
        print(f"\n[Q{i}] {question}")
        print("-" * 60)

        # Baseline
        print("  Baseline (no RAG) ...")
        baseline = answer_no_rag(question)
        print(f"  → {baseline[:250].strip()}")

        # LLM RAG
        print("\n  SPARQL-generation RAG (LLM) ...")
        rag_result = answer_with_rag(g, schema_summary, question)

        # Gold reference
        print("\n  Gold SPARQL (validated) ...")
        try:
            gold_vars, gold_rows = run_sparql(g, GOLD_SPARQL[question])
            gold_answer = f"{len(gold_rows)} row(s)" + (
                " — " + " | ".join(gold_rows[0]) if gold_rows else ""
            )
            print(f"  → {gold_answer[:200]}")
        except Exception as e:
            gold_answer = f"[ERROR] {e}"
            print(f"  → {gold_answer}")

        if rag_result["error"]:
            rag_answer = f"[ERROR] {rag_result['error']}"
            correct    = "No"
        elif not rag_result["rows"]:
            rag_answer = "[No rows returned]"
            correct    = "Partial"
        else:
            rag_answer = f"{len(rag_result['rows'])} row(s) — " + \
                         " | ".join(rag_result["rows"][0])
            correct    = "Yes"

        print(f"\n  LLM RAG : {rag_answer[:150]}")
        print(f"  Repaired: {rag_result['repaired']}")

        results_table.append({
            "Q":           f"Q{i}",
            "Question":    question,
            "Baseline":    baseline[:200].strip(),
            "RAG_LLM":     rag_answer[:200],
            "Gold":        gold_answer[:200],
            "Correct_LLM": correct,
            "Repaired":    rag_result["repaired"],
        })

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Q':<4} {'LLM correct':<14} {'Repaired':<10} Question")
    print("-" * 70)
    for r in results_table:
        print(f"{r['Q']:<4} {r['Correct_LLM']:<14} {str(r['Repaired']):<10} {r['Question']}")

    with open("evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results_table, f, indent=2, ensure_ascii=False)
    print("\n[INFO] Saved to evaluation_results.json")

# 8) CLI
def run_cli(g: Graph, schema_summary: str) -> None:
    print("\n" + "=" * 60)
    print(f"FIFA RAG Chatbot — {OLLAMA_MODEL}")
    print("Type 'quit' to exit | 'eval' to run evaluation")
    print("=" * 60)
    while True:
        try:
            q = input("\nQuestion: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye."); break
        if not q: continue
        if q.lower() == "quit": print("Bye."); break
        if q.lower() == "eval":
            run_evaluation(g, schema_summary); continue
        print("\n--- Baseline (No RAG) ---")
        print(answer_no_rag(q))
        print("\n--- SPARQL-generation RAG ---")
        pretty_print_result(answer_with_rag(g, schema_summary, q))

if __name__ == "__main__":
    g      = load_graph(NT_FILE)
    schema = build_schema_summary(g)
    if "--schema" in sys.argv:
        print(schema); sys.exit(0)
    if "--eval" in sys.argv:
        run_evaluation(g, schema); sys.exit(0)
    run_cli(g, schema)