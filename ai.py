import os
import json
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from dotenv import load_dotenv
import google.generativeai as genai
from vector_store import GroundwaterEmbeddingPipeline, EmbeddedChunk

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """Structure for RAG responses"""
    answer: str
    sources: List[Dict]
    confidence: float
    query_type: str
    retrieved_chunks: int

class GroundwaterRAGChatbot:
    """RAG Chatbot using Gemini 2.0 Flash for groundwater data analysis"""
    
    def __init__(self, 
                 embedding_pipeline: GroundwaterEmbeddingPipeline,
                 model_name: str = "gemini-2.0-flash"):
        """
        Initialize the RAG chatbot
        
        Args:
            embedding_pipeline: Initialized embedding pipeline
            model_name: Gemini model name
        """
        self.embedding_pipeline = embedding_pipeline
        self.model_name = model_name
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config for consistent, analytical responses
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.05,  # Very low temperature for factual, numerical responses
            top_p=0.7,
            top_k=20,
            max_output_tokens=2048,
        )
        
        logger.info(f"Initialized Gemini RAG chatbot with model: {model_name}")
    
    def classify_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify the user query to determine search strategy
        
        Args:
            query: User query
            
        Returns:
            Dictionary with query classification
        """
        classification_prompt = f"""
Analyze this groundwater-related query and classify it. Return a JSON response.

Query: "{query}"

Classify the query based on these categories:

1. GEOGRAPHIC_SCOPE: "state", "district", "unit", "national", "multi_state"
2. TEMPORAL_SCOPE: "2023", "2024", "comparison", "trend", "general"
3. DATA_TYPE: "statistical", "categorical", "comparative", "explanatory", "visual"
4. CONTENT_PREFERENCE: "table", "text", "image", "mixed"
5. QUERY_COMPLEXITY: "simple_lookup", "aggregation", "analysis", "complex"

Also extract:
- ENTITIES: List of geographic entities (states, districts)
- KEYWORDS: Key technical terms
- INTENT: Brief description of what user wants

Return only valid JSON format:
{{
    "geographic_scope": "...",
    "temporal_scope": "...", 
    "data_type": "...",
    "content_preference": "...",
    "query_complexity": "...",
    "entities": [...],
    "keywords": [...],
    "intent": "..."
}}
"""
        
        try:
            response = self.model.generate_content(
                classification_prompt,
                generation_config=self.generation_config
            )
            
            # Clean and parse JSON response
            response_text = response.text.strip()
            
            # Try to extract JSON from response if it's wrapped in markdown or other text
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            classification = json.loads(response_text)
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'No response'}")
            # Return default classification
            return {
                "geographic_scope": "general",
                "temporal_scope": "general",
                "data_type": "mixed",
                "content_preference": "mixed",
                "query_complexity": "simple_lookup",
                "entities": [],
                "keywords": [],
                "intent": "General groundwater information request"
            }
    
    def retrieve_relevant_chunks(self, 
                                query: str, 
                                classification: Dict[str, Any],
                                k: int = 12) -> List[Tuple[EmbeddedChunk, float]]:
        """
        Retrieve relevant chunks with enhanced entity matching and disambiguation
        
        Args:
            query: User query
            classification: Query classification
            k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with similarity scores
        """
        # Determine chunk types to search
        chunk_types = None
        if classification.get("content_preference") == "table":
            chunk_types = ["table"]
        elif classification.get("content_preference") == "text":
            chunk_types = ["text"]
        elif classification.get("content_preference") == "image":
            chunk_types = ["image"]
        
        # Enhanced entity matching with common variations
        state_variations = {
            "maharashtra": "Maharashtra", "mh": "Maharashtra", "mumbai": "Maharashtra",
            "rajasthan": "Rajasthan", "rj": "Rajasthan", "jaipur": "Rajasthan",
            "gujarat": "Gujarat", "gj": "Gujarat", "ahmedabad": "Gujarat",
            "karnataka": "Karnataka", "ka": "Karnataka", "bangalore": "Karnataka", "bengaluru": "Karnataka",
            "tamil nadu": "Tamil Nadu", "tn": "Tamil Nadu", "chennai": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
            "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh", "hyderabad": "Andhra Pradesh",
            "telangana": "Telangana", "ts": "Telangana",
            "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh", "lucknow": "Uttar Pradesh",
            "madhya pradesh": "Madhya Pradesh", "mp": "Madhya Pradesh", "bhopal": "Madhya Pradesh",
            "west bengal": "West Bengal", "wb": "West Bengal", "kolkata": "West Bengal", "westbengal": "West Bengal",
            "bihar": "Bihar", "br": "Bihar", "patna": "Bihar",
            "odisha": "Odisha", "or": "Odisha", "orissa": "Odisha", "bhubaneswar": "Odisha",
            "punjab": "Punjab", "pb": "Punjab", "chandigarh": "Punjab",
            "haryana": "Haryana", "hr": "Haryana",
            "himachal pradesh": "Himachal Pradesh", "hp": "Himachal Pradesh",
            "uttarakhand": "Uttarakhand", "uk": "Uttarakhand", "uttaranchal": "Uttarakhand",
            "jharkhand": "Jharkhand", "jh": "Jharkhand", "ranchi": "Jharkhand",
            "chhattisgarh": "Chhattisgarh", "cg": "Chhattisgarh", "chattisgarh": "Chhattisgarh",
            "assam": "Assam", "as": "Assam", "guwahati": "Assam",
            "kerala": "Kerala", "kl": "Kerala", "kochi": "Kerala", "trivandrum": "Kerala",
            "goa": "Goa", "ga": "Goa",
            "delhi": "Delhi", "dl": "Delhi", "new delhi": "Delhi"
        }
        
        # Extract filters from entities and query
        state_filter = None
        district_filter = None
        year_filter = None
        
        entities = classification.get("entities", [])
        query_lower = query.lower()
        
        # Check for state mentions in query and entities
        for variation, standard_name in state_variations.items():
            if variation in query_lower or any(variation in entity.lower() for entity in entities):
                state_filter = standard_name
                break
        
        # Also check entities directly
        for entity in entities:
            if entity in state_variations.values():
                state_filter = entity
                break
        
        # Temporal filter
        temporal_scope = classification.get("temporal_scope")
        if temporal_scope in ["2023", "2024"]:
            year_filter = temporal_scope
        elif "2023" in query:
            year_filter = "2023"
        elif "2024" in query:
            year_filter = "2024"
        
        # Log what filters are being applied
        logger.info(f"Search filters - State: {state_filter}, Year: {year_filter}, Chunk types: {chunk_types}")
        
        # Retrieve chunks with higher k for better filtering
        results = self.embedding_pipeline.search_similar_chunks(
            query=query,
            k=k,
            chunk_types=chunk_types,
            state_filter=state_filter,
            district_filter=district_filter,
            year_filter=year_filter
        )
        
        # If no results with filters, try without filters as fallback
        if not results and (state_filter or year_filter or chunk_types):
            logger.info("No results with filters, trying without filters...")
            results = self.embedding_pipeline.search_similar_chunks(
                query=query,
                k=k,
                chunk_types=None,
                state_filter=None,
                district_filter=None,
                year_filter=None
            )
            logger.info(f"Fallback search returned {len(results)} chunks")
        
        return results
    
    def create_context_from_chunks(self, chunks: List[Tuple[EmbeddedChunk, float]]) -> str:
        """
        Create context string from retrieved chunks (without source numbers for cleaner response)
        
        Args:
            chunks: List of (chunk, score) tuples
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant data found in the groundwater assessment report."
        
        context_parts = []
        
        for chunk, score in chunks:
            context_part = f"Data Type: {chunk.metadata.chunk_type.title()}\n"
            
            if chunk.metadata.state:
                context_part += f"Geographic Scope: {chunk.metadata.state}"
                if chunk.metadata.district:
                    context_part += f" > {chunk.metadata.district}"
                context_part += "\n"
            
            if chunk.metadata.year:
                context_part += f"Time Period: {chunk.metadata.year}\n"
            
            if chunk.metadata.content_type:
                context_part += f"Data Category: {chunk.metadata.content_type}\n"
            
            context_part += f"Content: {chunk.content}\n"
            context_part += "-" * 60 + "\n"
            
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def generate_response_prompt(self, 
                                query: str, 
                                context: str, 
                                classification: Dict[str, Any]) -> str:
        """
        Generate the main prompt for Gemini response generation
        
        Args:
            query: Original user query
            context: Retrieved context from chunks
            classification: Query classification
            
        Returns:
            Formatted prompt for Gemini
        """
        
        prompt = f"""You are a specialized groundwater data analyst for India with access to official 2023-2024 groundwater assessment data from a single authoritative PDF report.

STRICT GUARDRAILS:
- Answer ONLY using data from the provided context below
- If the context doesn't contain sufficient data to answer, respond with "The available data does not contain sufficient information to answer this query."
- NEVER use external knowledge, estimates, or assumptions
- NEVER hallucinate numbers, percentages, or district/state names not in the context
- If you make assumptions about ambiguous queries, end with "Please confirm if this addresses your question about [your interpretation]"

QUERY: "{query}"
QUERY INTENT: {classification.get('intent', 'General inquiry')}

AVAILABLE DATA:
{context}

GROUNDWATER CATEGORIES (ESTABLISHED THRESHOLDS):
- Safe: Extraction < 70% of annual recharge
- Semi-Critical: Extraction 70-90% of annual recharge  
- Critical: Extraction 90-100% of annual recharge
- Over-Exploited: Extraction > 100% of annual recharge

RESPONSE REQUIREMENTS:
1. **NUMERICAL FOCUS**: Lead with specific numbers, percentages, and quantified insights
2. **TABULAR FORMAT**: Present data in tables when showing multiple entities
3. **INSIGHTS**: Explain what the numbers mean and their significance
4. **TREND ANALYSIS**: For 2023 vs 2024 comparisons, highlight:
   - Absolute changes in numbers
   - Percentage improvements/deteriorations
   - Category transitions (e.g., Critical → Semi-Critical)
5. **NO CITATIONS**: Don't reference sources, focus on data presentation
6. **CONFIRMATION**: If query was ambiguous, ask confirmation at the end

TABLE FORMAT EXAMPLE:
| District | 2023 Extraction (%) | 2024 Extraction (%) | Category Change | Status |
|----------|--------------------|--------------------|----------------|--------|
| District A | 85.2 | 78.4 | Critical → Semi-Critical | Improved |

RESPONSE STRUCTURE:
1. **Direct Answer**: Lead with key numbers/findings
2. **Data Table**: Present relevant data in tabular format
3. **Key Insights**: 3-4 bullet points explaining what the data reveals
4. **Trend Analysis**: If applicable, highlight changes and patterns
5. **Confirmation**: If query was interpreted, ask for confirmation

Remember: Be precise, numerical, and analytical. Focus on extracting actionable insights from the data patterns.
"""
        
        return prompt
    
    def generate_response(self, 
                         query: str, 
                         context: str, 
                         classification: Dict[str, Any]) -> str:
        """
        Generate response using Gemini
        
        Args:
            query: User query
            context: Context from retrieved chunks
            classification: Query classification
            
        Returns:
            Generated response
        """
        prompt = self.generate_response_prompt(query, context, classification)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error while processing your query. Please try rephrasing your question or contact support. Error: {str(e)}"
    
    def chat(self, query: str, max_chunks: int = 10) -> RAGResponse:
        """
        Main chat method - complete RAG pipeline with enhanced disambiguation
        
        Args:
            query: User query
            max_chunks: Maximum number of chunks to retrieve
            
        Returns:
            RAGResponse object with answer and metadata
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Classify query
        classification = self.classify_query_intent(query)
        logger.info(f"Query classification: {classification.get('intent', 'Unknown')}")
        
        # Step 2: Retrieve relevant chunks with enhanced filtering
        retrieved_chunks = self.retrieve_relevant_chunks(query, classification, k=max_chunks)
        logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
        
        if not retrieved_chunks:
            return RAGResponse(
                answer="The available groundwater assessment data does not contain sufficient information to answer this query. Please try rephrasing your question or asking about different states/districts/years covered in the report.",
                sources=[],
                confidence=0.0,
                query_type=classification.get('intent', 'Unknown'),
                retrieved_chunks=0
            )
        
        # Step 3: Create context without source citations
        context = self.create_context_from_chunks(retrieved_chunks)
        
        # Step 4: Generate response with strong guardrails
        answer = self.generate_response(query, context, classification)
        
        # Step 5: Prepare simplified sources (for internal tracking, not shown to user)
        sources = []
        for i, (chunk, score) in enumerate(retrieved_chunks, 1):
            source = {
                "chunk_id": chunk.chunk_id,
                "type": chunk.metadata.chunk_type,
                "state": chunk.metadata.state,
                "district": chunk.metadata.district,
                "year": chunk.metadata.year,
                "relevance_score": float(score)
            }
            sources.append(source)
        
        # Calculate confidence based on relevance scores and data availability
        if retrieved_chunks:
            avg_score = sum(score for _, score in retrieved_chunks) / len(retrieved_chunks)
            # Higher confidence if we have good matches
            confidence = min(avg_score / 0.7, 1.0)  # Normalize to 0-1 range
        else:
            confidence = 0.0
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            query_type=classification.get('intent', 'Unknown'),
            retrieved_chunks=len(retrieved_chunks)
        )
    
    def batch_chat(self, queries: List[str]) -> List[RAGResponse]:
        """
        Process multiple queries in batch
        
        Args:
            queries: List of user queries
            
        Returns:
            List of RAGResponse objects
        """
        responses = []
        for query in queries:
            try:
                response = self.chat(query)
                responses.append(response)
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                error_response = RAGResponse(
                    answer=f"Error processing query: {str(e)}",
                    sources=[],
                    confidence=0.0,
                    query_type="error",
                    retrieved_chunks=0
                )
                responses.append(error_response)
        
        return responses


# Usage Example and Testing
def main():
    """Example usage of the RAG chatbot"""
    
    # Initialize embedding pipeline (assuming it's already set up)
    embedding_pipeline = GroundwaterEmbeddingPipeline()
    
    # Load existing embeddings or create new ones
    try:
        embedding_pipeline.load_embeddings("./embeddings_data")
        logger.info("Loaded existing embeddings")
    except FileNotFoundError:
        logger.info("Creating new embeddings...")
        embedding_pipeline.create_embeddings_from_json("groundwater_chunks.json")
        embedding_pipeline.build_faiss_index(index_type='flat')
        embedding_pipeline.save_embeddings("./embeddings_data")
    
    # Initialize RAG chatbot
    chatbot = GroundwaterRAGChatbot(embedding_pipeline)
    
    # Test queries focused on numerical insights
    test_queries = [
        "How many districts in Maharashtra improved from 2023 to 2024?",
        "What percentage of Rajasthan's groundwater units are over-exploited in 2024?",
        "Show me the numerical breakdown of assessment units that deteriorated across all states",
        "Which 5 states had the most districts move from Critical to Semi-Critical category?",
        "What are the exact extraction percentages for Punjab districts in 2024?",
        "Compare the number of Safe vs Over-exploited units between 2023 and 2024 nationally"
    ]
    
    print("🌊 Groundwater Data Analysis Chatbot - Numerical Insights")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            response = chatbot.chat(query)
            
            print(f"📊 Analysis:\n{response.answer}")
            print(f"\n📈 Data Confidence: {response.confidence:.2f}")
            print(f"📚 Chunks Analyzed: {response.retrieved_chunks}")
            print(f"🎯 Query Classification: {response.query_type}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()