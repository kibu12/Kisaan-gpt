"""
agents/rag_retriever_agent.py
Supports both soil-param based retrieval and free-form NL query retrieval.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from rag.build_knowledge_base import retrieve


class RAGRetrieverAgent:

    def retrieve(self, soil_params: dict, top_crop: str) -> str:
        """Original method — retrieves based on soil params + crop name."""
        query = (
            f"Crop recommendation and fertilizer guidelines for {top_crop}. "
            f"Soil pH: {soil_params.get('ph')}, "
            f"Nitrogen: {soil_params.get('N')} kg/ha, "
            f"Phosphorus: {soil_params.get('P')} kg/ha, "
            f"Potassium: {soil_params.get('K')} kg/ha. "
            f"Soil management and nutrient application advice."
        )
        return retrieve(query, k=4, threshold=0.25)

    def retrieve_by_query(self, query: str) -> str:
        """New method — retrieves based on any free-form NL query."""
        return retrieve(query, k=4, threshold=0.1)
