import os
import faiss
import pickle
import logging
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserType(Enum):
    RESEARCHER = "researcher"
    POLICY_MAKER = "policy_maker"
    BASIC_USER = "basic_user"
    GENERAL = "general"

@dataclass
class QueryContext:
    """Store query context and conversation history"""
    user_type: UserType
    previous_queries: List[str]
    previous_responses: List[str]
    current_filters: Dict[str, Any]
    session_id: str
    timestamp: datetime

@dataclass
class SearchResult:
    """Enhanced search result with AI processing"""
    original_results: List[Dict[str, Any]]
    processed_summary: str
    key_findings: List[str]
    user_specific_insights: str
    confidence_score: float
    data_sources: List[str]

class INGRESGeminiAI:
    """
    Gemini-powered AI interface for INGRES groundwater data system
    Handles multi-user types with context-aware responses
    """
    
    def __init__(self, 
                 embedding_pipeline=None,
                 model_name: str = "gemini-2.0-flash",
                 max_context_history: int = 10):
        # Load environment variables from .env file
        load_dotenv()
        # Initialize Gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Initialize search components
        self.embedding_pipeline = embedding_pipeline
        self.search_interface = None
        if embedding_pipeline:
            self.search_interface = INGRESSearchInterface(embedding_pipeline)
        
        # Context management
        self.max_context_history = max_context_history
        self.active_sessions: Dict[str, QueryContext] = {}
        
        # User type configurations
        self.user_configs = self._setup_user_configurations()
        
        # Query patterns for different search strategies
        self.query_patterns = self._setup_query_patterns()
        
        # Load or initialize indexes
        self._initialize_search_system()
    
    def _setup_user_configurations(self) -> Dict[UserType, Dict[str, Any]]:
        """Configure response styles for different user types"""
        return {
            UserType.RESEARCHER: {
                "detail_level": "high",
                "include_methodology": True,
                "include_statistics": True,
                "technical_language": True,
                "response_format": "detailed",
                "preferred_search": "semantic"
            },
            UserType.POLICY_MAKER: {
                "detail_level": "high",
                "include_methodology": False,
                "include_statistics": True,
                "technical_language": False,
                "response_format": "executive_summary",
                "preferred_search": "semantic"
            },
            UserType.BASIC_USER: {
                "detail_level": "low",
                "include_methodology": False,
                "include_statistics": False,
                "technical_language": False,
                "response_format": "simple",
                "preferred_search": "keyword"
            },
            UserType.GENERAL: {
                "detail_level": "medium",
                "include_methodology": False,
                "include_statistics": True,
                "technical_language": False,
                "response_format": "balanced",
                "preferred_search": "hybrid"
            }
        }
    
    def _setup_query_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Setup patterns for different types of queries"""
        return {
            "location_query": {
                "patterns": [r"\b(in|at|from)\s+([A-Za-z\s]+(?:district|state|region))", 
                           r"\b([A-Za-z\s]+(?:district|state))\b"],
                "search_strategy": "location_based"
            },
            "comparison_query": {
                "patterns": [r"\b(compare|versus|vs|between)\b", 
                           r"\b(difference|differ)\b"],
                "search_strategy": "comparative"
            },
            "trend_query": {
                "patterns": [r"\b(trend|change|over time|temporal)\b",
                           r"\b(increase|decrease|decline|improve)\b"],
                "search_strategy": "temporal"
            },
            "issue_query": {
                "patterns": [r"\b(problem|issue|concern|critical)\b",
                           r"\b(over-exploit|contamination|pollution)\b"],
                "search_strategy": "issue_focused"
            },
            "recommendation_query": {
                "patterns": [r"\b(recommend|suggest|solution|manage)\b",
                           r"\b(what should|how to|best practice)\b"],
                "search_strategy": "recommendation"
            }
        }
    
    def _initialize_search_system(self):
        """Initialize or load existing search indexes"""
        try:
            if self.embedding_pipeline:
                # Try to load existing indexes
                if not self.embedding_pipeline.load_indexes_and_metadata():
                    logger.warning("No existing indexes found. You may need to run the embedding pipeline first.")
                else:
                    logger.info("Successfully loaded existing search indexes")
            else:
                logger.warning("No embedding pipeline provided. Search functionality will be limited.")
        except Exception as e:
            logger.error(f"Error initializing search system: {e}")
    
    def create_session(self, user_type: UserType = UserType.GENERAL, session_id: str = None) -> str:
        """Create a new user session with context management"""
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.active_sessions[session_id] = QueryContext(
            user_type=user_type,
            previous_queries=[],
            previous_responses=[],
            current_filters={},
            session_id=session_id,
            timestamp=datetime.now()
        )
        
        logger.info(f"Created new session {session_id} for user type {user_type.value}")
        return session_id
    
    def _detect_user_type(self, query: str) -> UserType:
        """Auto-detect user type based on query characteristics"""
        query_lower = query.lower()
        
        # Researcher indicators
        researcher_terms = ["analysis", "methodology", "statistical", "correlation", 
                          "regression", "variance", "hypothesis", "study", "research"]
        
        # Policy maker indicators
        policy_terms = ["policy", "regulation", "management", "framework", 
                       "governance", "strategy", "implementation", "compliance"]
        
        # Count matches
        researcher_score = sum(1 for term in researcher_terms if term in query_lower)
        policy_score = sum(1 for term in policy_terms if term in query_lower)
        
        if researcher_score >= 2:
            return UserType.RESEARCHER
        elif policy_score >= 2:
            return UserType.POLICY_MAKER
        elif len(query.split()) < 10 and any(word in query_lower for word in ["what", "where", "simple", "basic"]):
            return UserType.BASIC_USER
        else:
            return UserType.GENERAL
    
    def _analyze_query_intent(self, query: str, context: QueryContext) -> Dict[str, Any]:
        """Analyze query to determine search strategy and filters"""
        analysis = {
            "query_type": "general",
            "search_strategy": "hybrid",
            "extracted_filters": {},
            "priority_terms": [],
            "confidence": 0.0
        }
        
        # Check query patterns
        for pattern_type, config in self.query_patterns.items():
            for pattern in config["patterns"]:
                if re.search(pattern, query, re.IGNORECASE):
                    analysis["query_type"] = pattern_type
                    analysis["search_strategy"] = config["search_strategy"]
                    analysis["confidence"] = 0.8
                    break
        
        # Extract location filters
        location_matches = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:district|state)\b', query, re.IGNORECASE)
        if location_matches:
            analysis["extracted_filters"]["location"] = location_matches[0]
        
        # Extract technical terms
        technical_terms = ["recharge", "extraction", "sustainability", "quality", "contamination", 
                         "over-exploited", "critical", "safe", "semi-critical"]
        found_terms = [term for term in technical_terms if term in query.lower()]
        analysis["priority_terms"] = found_terms
        
        # Use user type to influence search strategy
        user_config = self.user_configs[context.user_type]
        if analysis["search_strategy"] == "hybrid":
            analysis["search_strategy"] = user_config["preferred_search"]
        
        return analysis
    
    def _perform_contextual_search(self, query: str, context: QueryContext, 
                                 query_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform search based on query analysis and context"""
        if not self.search_interface:
            return []
        
        search_strategy = query_analysis["search_strategy"]
        filters = query_analysis.get("extracted_filters", {})
        
        # Merge with context filters
        filters.update(context.current_filters)
        
        try:
            if search_strategy == "location_based" and "location" in filters:
                # Parse location
                location_parts = filters["location"].split()
                if len(location_parts) >= 2:
                    return self.search_interface.pipeline.search_by_location(
                        state=location_parts[-1] if "state" in query.lower() else None,
                        district=location_parts[0] if "district" in query.lower() else None,
                        top_k=15
                    )
            
            elif search_strategy == "comparative":
                # Handle comparison queries
                regions = self._extract_regions_for_comparison(query)
                if regions:
                    comparison_results = self.search_interface.compare_regions(
                        regions, comparison_aspect="sustainability"
                    )
                    # Flatten results for processing
                    flattened = []
                    for region, results in comparison_results.items():
                        for result in results:
                            result['comparison_region'] = region
                            flattened.append(result)
                    return flattened
            
            elif search_strategy == "issue_focused":
                # Search for specific issues
                issue_type = self._determine_issue_type(query)
                return self.search_interface.search_groundwater_issues(
                    issue_type, location=filters, top_k=12
                )
            
            elif search_strategy == "recommendation":
                # Get recommendations
                return self.search_interface.get_recommendations(
                    location=filters, focus_area="management"
                )
            
            else:
                # Default semantic/hybrid search
                search_type = "semantic" if search_strategy == "semantic" else "hybrid"
                return self.search_interface.search(
                    query, search_type=search_type, filters=filters, top_k=15
                )
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _extract_regions_for_comparison(self, query: str) -> List[Dict[str, str]]:
        """Extract regions mentioned in comparison queries"""
        # Simplified extraction - would need more sophisticated NLP in production
        regions = []
        # This is a basic implementation - enhance with better NLP
        location_mentions = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', query)
        for mention in location_mentions[:2]:  # Take first two as comparison targets
            regions.append({"district": mention, "state": ""})
        return regions
    
    def _determine_issue_type(self, query: str) -> str:
        """Determine the type of groundwater issue from query"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["over-exploit", "excessive", "unsustainable"]):
            return "over_exploitation"
        elif any(term in query_lower for term in ["quality", "contamination", "pollution"]):
            return "quality_problems"
        elif any(term in query_lower for term in ["decline", "falling", "dropping"]):
            return "declining_levels"
        elif any(term in query_lower for term in ["recharge", "insufficient", "low"]):
            return "recharge_issues"
        elif any(term in query_lower for term in ["saline", "salinity", "intrusion"]):
            return "saline_intrusion"
        else:
            return "over_exploitation"  # Default
    
    def _generate_ai_response(self, query: str, search_results: List[Dict[str, Any]], 
                            context: QueryContext, query_analysis: Dict[str, Any]) -> str:
        """Generate AI response using Gemini based on search results and context"""
        
        user_config = self.user_configs[context.user_type]
        
        # Prepare context for Gemini
        context_prompt = self._build_context_prompt(
            query, search_results, context, user_config, query_analysis
        )
        
        try:
            response = self.model.generate_content(context_prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_fallback_response(search_results, user_config)
    
    def _build_context_prompt(self, query: str, search_results: List[Dict[str, Any]], 
                            context: QueryContext, user_config: Dict[str, Any],
                            query_analysis: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Gemini"""
        
        # Prepare search results summary
        results_summary = ""
        if search_results:
            results_summary = "SEARCH RESULTS FROM DATABASE:\n"
            for i, result in enumerate(search_results[:5]):  # Limit to top 5
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                score = result.get('score', 0)
                
                results_summary += f"\nResult {i+1} (Relevance: {score:.3f}):\n"
                results_summary += f"Location: {metadata.get('state', 'Unknown')}, {metadata.get('district', 'Unknown')}\n"
                results_summary += f"Content: {content[:300]}...\n"
                results_summary += "---\n"
        else:
            results_summary = "NO RELEVANT DATA FOUND IN DATABASE"
        
        # Build conversation history
        history = ""
        if context.previous_queries:
            history = "PREVIOUS CONVERSATION:\n"
            for i, (prev_query, prev_response) in enumerate(zip(
                context.previous_queries[-3:], context.previous_responses[-3:]
            )):
                history += f"User {i+1}: {prev_query}\n"
                history += f"Assistant {i+1}: {prev_response[:200]}...\n\n"
        
        # User type specific instructions
        user_instructions = {
            UserType.RESEARCHER: """
            You are responding to a RESEARCHER. Provide:
            - Detailed technical analysis with specific data points
            - Statistical interpretations where relevant
            - Methodology notes if applicable
            - Academic tone with precise terminology
            - Include data confidence levels and limitations
            """,
            UserType.POLICY_MAKER: """
            You are responding to a POLICY MAKER. Provide:
            - Executive summary format
            - Key actionable insights
            - Policy implications and recommendations
            - Clear, professional language without excessive technical jargon
            - Focus on management and regulatory aspects
            """,
            UserType.BASIC_USER: """
            You are responding to a BASIC USER. Provide:
            - Simple, clear explanations
            - Avoid technical jargon
            - Use analogies where helpful
            - Focus on practical implications
            - Keep response concise and accessible
            """,
            UserType.GENERAL: """
            You are responding to a GENERAL USER. Provide:
            - Balanced detail level
            - Some technical information but explained clearly
            - Practical insights
            - Professional but accessible tone
            """
        }
        
        prompt = f"""You are an AI expert in groundwater resources and hydrogeology, specifically trained on INGRES (India-WRIS Groundwater Resource Estimation System) data.

{user_instructions[context.user_type]}

{history}

CURRENT USER QUERY: {query}

QUERY ANALYSIS:
- Query Type: {query_analysis.get('query_type', 'general')}
- Priority Terms: {', '.join(query_analysis.get('priority_terms', []))}

{results_summary}

IMPORTANT INSTRUCTIONS:
1. Base your response PRIMARILY on the search results provided above
2. If the search results are insufficient or "NO RELEVANT DATA FOUND", clearly state: "I don't have sufficient information on this specific query in the database. However, based on general groundwater knowledge..."
3. DO NOT fabricate specific data, statistics, or location-specific information
4. If you reference any data, it must come from the search results above
5. Maintain conversation context from previous exchanges
6. Provide natural language response with key findings highlighted
7. Include data source confidence when available
8. Be professional and precise in your response

Please provide a comprehensive response to the user's query."""

        return prompt
    
    def _generate_fallback_response(self, search_results: List[Dict[str, Any]], 
                                  user_config: Dict[str, Any]) -> str:
        """Generate fallback response when Gemini API fails"""
        if not search_results:
            return "I don't have sufficient information on this specific query in the database."
        
        # Simple summarization of search results
        summary = "Based on the available data:\n\n"
        
        for i, result in enumerate(search_results[:3]):
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            summary += f"Finding {i+1}: "
            summary += f"In {metadata.get('district', 'Unknown')}, {metadata.get('state', 'Unknown')}: "
            summary += content[:150] + "...\n\n"
        
        summary += "Please note: This is a simplified summary due to technical limitations."
        return summary
    
    def process_query(self, query: str, session_id: str = None, 
                     user_type: UserType = None) -> Dict[str, Any]:
        """Main method to process user queries"""
        
        # Handle session management
        if not session_id:
            detected_user_type = user_type or self._detect_user_type(query)
            session_id = self.create_session(detected_user_type)
        
        if session_id not in self.active_sessions:
            detected_user_type = user_type or self._detect_user_type(query)
            session_id = self.create_session(detected_user_type, session_id)
        
        context = self.active_sessions[session_id]
        
        # Update user type if explicitly provided
        if user_type:
            context.user_type = user_type
        
        # Analyze query intent
        query_analysis = self._analyze_query_intent(query, context)
        
        # Perform contextual search
        search_results = self._perform_contextual_search(query, context, query_analysis)
        
        # Generate AI response
        ai_response = self._generate_ai_response(query, search_results, context, query_analysis)
        
        # Update context
        context.previous_queries.append(query)
        context.previous_responses.append(ai_response)
        
        # Maintain context history limit
        if len(context.previous_queries) > self.max_context_history:
            context.previous_queries = context.previous_queries[-self.max_context_history:]
            context.previous_responses = context.previous_responses[-self.max_context_history:]
        
        # Prepare response
        response = {
            "session_id": session_id,
            "user_type": context.user_type.value,
            "query": query,
            "response": ai_response,
            "search_results_count": len(search_results),
            "query_analysis": query_analysis,
            "timestamp": datetime.now().isoformat(),
            "has_data": len(search_results) > 0
        }
        
        logger.info(f"Processed query for session {session_id}: {len(search_results)} results found")
        
        return response
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """Get conversation history for a session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}
        
        context = self.active_sessions[session_id]
        return {
            "session_id": session_id,
            "user_type": context.user_type.value,
            "query_count": len(context.previous_queries),
            "conversation_history": [
                {"query": q, "response": r} 
                for q, r in zip(context.previous_queries, context.previous_responses)
            ],
            "created": context.timestamp.isoformat()
        }
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleared session {session_id}")
            return True
        return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and capabilities"""
        return {
            "gemini_api": "connected" if self.api_key else "not_configured",
            "search_system": "available" if self.search_interface else "not_available",
            "active_sessions": len(self.active_sessions),
            "supported_user_types": [ut.value for ut in UserType],
            "search_capabilities": {
                "semantic_search": self.search_interface is not None,
                "location_search": self.search_interface is not None,
                "comparative_analysis": self.search_interface is not None,
                "recommendation_system": self.search_interface is not None
            }
        }


def main():
    index_file = os.path.join("faiss_indexes", "unified_index.faiss")
    metadata_file = os.path.join("faiss_indexes", "unified_metadata.pkl")
    if not (os.path.exists(index_file) and os.path.exists(metadata_file)):
        print("Index or metadata file missing. Please run the embedding/indexing pipeline first.")
        return

    # Load FAISS index and metadata directly
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        metadata = pickle.load(f)
    print(f"Loaded index with {index.ntotal} vectors and {len(metadata)} metadata entries.")

    # Example: prompt user for a query (no embedding, just shows data loaded)
    user_question = input("Enter your question (this version does not run search, just loads index): ")
    print("Index and metadata are loaded. Implement your search logic here.")

if __name__ == "__main__":
    main()