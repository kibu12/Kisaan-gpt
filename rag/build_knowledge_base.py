import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rag.supabase_client import get_supabase


def build_rag_db():
    supabase = get_supabase()

    print("Clearing existing RAG documents...", flush=True)
    supabase.table("rag_documents").delete().neq("id", 0).execute()
    print("Cleared.", flush=True)

    doc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
    txt_files = sorted([f for f in os.listdir(doc_dir) if f.endswith(".txt")])
    print(f"Found {len(txt_files)} documents.\n", flush=True)

    total = 0
    for filename in txt_files:
        print(f"  Processing {filename}...", flush=True)
        filepath = os.path.join(doc_dir, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Split into chunks of 5 lines each — no RAM-heavy list building
        chunk_size = 5
        for i in range(0, len(lines), chunk_size):
            chunk = "".join(lines[i:i + chunk_size]).strip()
            if len(chunk) < 10:
                continue

            # Insert one row at a time — minimal memory footprint
            # No embedding — store as plain text, retrieve by keyword match
            supabase.table("rag_documents").insert({
                "source":    filename,
                "content":   chunk,
                "embedding": [0.0] * 384,  # dummy vector — we use keyword search
            }).execute()
            total += 1
            print(f"    Inserted chunk {total}", flush=True)

    print(f"\nDone — {total} chunks stored in Supabase.", flush=True)
    print("RAG will use keyword search instead of vector search.", flush=True)


def retrieve(query, k=4, threshold=0.0):
    """
    Keyword-based retrieval — searches content column directly.
    No embedding model needed. Works on any RAM.
    """
    supabase = get_supabase()

    # Extract keywords from query (words longer than 3 chars)
    keywords = [w.lower() for w in query.split() if len(w) > 3]

    all_chunks = (
        supabase.table("rag_documents")
        .select("source, content")
        .execute()
    )

    if not all_chunks.data:
        return "No guidelines found in knowledge base."

    # Score each chunk by keyword matches
    scored = []
    for row in all_chunks.data:
        content_lower = row["content"].lower()
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            scored.append((score, row["source"], row["content"]))

    # Sort by score, return top k
    scored.sort(reverse=True)
    top = scored[:k]

    if not top:
        # Fallback — return first k chunks
        top = [(0, r["source"], r["content"]) for r in all_chunks.data[:k]]

    return "\n\n---\n\n".join(
        f"[Source: {src}]\n{content}"
        for _, src, content in top
    )


if __name__ == "__main__":
    build_rag_db()