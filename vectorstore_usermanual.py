import chromadb
import numpy as np
import json
import logging
import hashlib
from typing import List, Dict, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import re
from datetime import datetime
from pathlib import Path
import sys
import argparse

# Import the chunker classes from the user manual chunker module
# (Adjusted: original import referenced a non-existent 'gec2015_chunker' module)
from chunking_usermanual import DocumentChunk, ChunkType, ComponentType, ChunkMetadata, GEC2015DocumentChunker

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation and vector store operations."""
    model_name: str = "all-MiniLM-L6-v2"  # Lightweight, fast, good performance
    collection_name: str = "gec2015_groundwater_docs"
    chunk_size_limit: int = 8000  # Character limit for embeddings
    overlap_size: int = 200  # Overlap for large chunks
    persist_directory: str = "./chroma_db"
    distance_function: str = "cosine"  # cosine, l2, ip
    embedding_dimension: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # GEC-2015 specific configurations
    formula_weight: float = 1.5  # Boost formula importance
    methodology_weight: float = 1.3  # Boost methodology content
    template_weight: float = 1.2  # Boost template references
    technical_term_weight: float = 1.4  # Boost technical terms

@dataclass
class SearchResult:
    """Container for search results with enhanced metadata."""
    chunk_id: str
    content: str
    score: float
    chunk_type: ChunkType
    metadata: ChunkMetadata
    highlights: List[str] = None
    related_chunks: List[str] = None

class GEC2015VectorStore:
    """Vector store implementation for GEC-2015 Ground Water Assessment documentation."""
    
    def __init__(self, config: EmbeddingConfig = None):
        self.config = config or EmbeddingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.config.persist_directory)
        
        # Initialize sentence transformer model
        self.embedding_model = SentenceTransformer(self.config.model_name)
        
        # Create or get collection
        self.collection = self._initialize_collection()
        
        # GEC-2015 specific patterns and weights
        self.technical_patterns = self._initialize_technical_patterns()
        self.content_weights = self._initialize_content_weights()
        
        # Cache for frequently used embeddings
        self.embedding_cache = {}
        
    def _initialize_collection(self) -> chromadb.Collection:
        """Initialize ChromaDB collection with proper configuration."""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=self.config.collection_name,
                embedding_function=self._chromadb_embedding_function
            )
            self.logger.info(f"Loaded existing collection: {self.config.collection_name}")
        except:
            # Create new collection
            collection = self.client.create_collection(
                name=self.config.collection_name,
                embedding_function=self._chromadb_embedding_function,
                metadata={
                    "description": "GEC-2015 Ground Water Assessment Documentation",
                    "model": self.config.model_name,
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0"
                }
            )
            self.logger.info(f"Created new collection: {self.config.collection_name}")
        
        return collection
    
    def _chromadb_embedding_function(self, texts: List[str]) -> List[List[float]]:
        """Custom embedding function for ChromaDB."""
        return [self.generate_embedding(text) for text in texts]
    
    def _initialize_technical_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for identifying technical content."""
        return {
            'formulas': [
                r'Formula\s+\d+', r'Equation\s+\d+', r'Where\s*:',
                r'[A-Z]+\s*=\s*', r'∑', r'Σ', r'∆', r'×', r'÷'
            ],
            'methodology': [
                r'GEC-2015', r'methodology', r'assessment', r'classification',
                r'water\s+balance', r'recharge', r'extraction', r'safe\s+yield'
            ],
            'units': [
                r'BCM', r'Ha\.m', r'Lpcd', r'm³', r'mm', r'%', r'MCM',
                r'cubic\s+meter', r'hectare\s+meter', r'liter\s+per\s+capita'
            ],
            'aquifer_terms': [
                r'unconfined', r'semi-confined', r'confined', r'aquifer',
                r'groundwater', r'water\s+table', r'piezometric', r'hydraulic'
            ],
            'assessment_categories': [
                r'SAFE', r'SEMI-CRITICAL', r'CRITICAL', r'OVER-EXPLOITED',
                r'stage\s+of\s+development', r'assessment\s+unit'
            ],
            'templates': [
                r'Template\s+\d+', r'Excel\s+template', r'Form\s+\d+',
                r'worksheet', r'data\s+entry', r'input\s+form'
            ]
        }
    
    def _initialize_content_weights(self) -> Dict[ChunkType, float]:
        """Initialize content type weights for embedding enhancement."""
        return {
            ChunkType.METHODOLOGY: self.config.methodology_weight,
            ChunkType.FORMULA: self.config.formula_weight,
            ChunkType.TEMPLATE: self.config.template_weight,
            ChunkType.TECHNICAL_SPEC: self.config.technical_term_weight,
            ChunkType.WORKFLOW: 1.1,
            ChunkType.USER_ROLE: 1.05,  # slight boost so role-based queries surface
            ChunkType.VISUAL: 0.9,
            ChunkType.GLOSSARY: 1.2,
            ChunkType.REPORT: 1.0
        }
    
    def enhance_text_for_embedding(self, text: str, chunk_type: ChunkType, metadata: ChunkMetadata) -> str:
        """Enhance text content for better embedding representation."""
        enhanced_text = text
        
        # Add context prefixes based on chunk type
        type_prefixes = {
            ChunkType.METHODOLOGY: "GEC-2015 Methodology: ",
            ChunkType.FORMULA: "Mathematical Formula: ",
            ChunkType.TEMPLATE: "Data Input Template: ",
            ChunkType.TECHNICAL_SPEC: "Technical Specification: ",
            ChunkType.WORKFLOW: "User Workflow: ",
            ChunkType.USER_ROLE: "User Role Definition: ",
            ChunkType.VISUAL: "Visual Documentation: ",
            ChunkType.GLOSSARY: "Technical Definition: ",
            ChunkType.REPORT: "Report Format: "
        }
        
        if chunk_type in type_prefixes:
            enhanced_text = type_prefixes[chunk_type] + enhanced_text
        
        # Add metadata context
        context_additions = []
        
        if metadata.section_number:
            context_additions.append(f"Section {metadata.section_number}")
        
        if metadata.component_type:
            context_additions.append(f"Component: {metadata.component_type.value}")
        
        if metadata.assessment_categories:
            context_additions.append(f"Assessment: {', '.join(metadata.assessment_categories)}")
        
        if metadata.aquifer_types:
            context_additions.append(f"Aquifer: {', '.join(metadata.aquifer_types)}")
        
        if metadata.user_roles:
            context_additions.append(f"Users: {', '.join(metadata.user_roles)}")
        
        # Add formula and template references for context
        if metadata.formula_references:
            context_additions.append(f"Formulas: {', '.join(metadata.formula_references)}")
        
        if metadata.template_references:
            context_additions.append(f"Templates: {', '.join(metadata.template_references)}")
        
        if context_additions:
            enhanced_text += " | Context: " + " | ".join(context_additions)
        
        return enhanced_text
    
    def generate_embedding(self, text: str, chunk_type: ChunkType = None) -> List[float]:
        """Generate embedding with caching and enhancement."""
        # Create cache key
        cache_key = hashlib.md5(text.encode('utf-8')).hexdigest()
        
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        # Apply content-specific preprocessing
        processed_text = self.preprocess_text_for_embedding(text, chunk_type)
        
        # Generate embedding
        embedding = self.embedding_model.encode(processed_text, normalize_embeddings=True).tolist()
        
        # Apply content type weighting
        if chunk_type and chunk_type in self.content_weights:
            weight = self.content_weights[chunk_type]
            embedding = [x * weight for x in embedding]
            # Re-normalize after weighting
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = [x / norm for x in embedding]
        
        # Cache the result
        self.embedding_cache[cache_key] = embedding
        
        return embedding
    
    def preprocess_text_for_embedding(self, text: str, chunk_type: ChunkType = None) -> str:
        """Preprocess text to enhance embedding quality for GEC-2015 content."""
        processed_text = text
        
        # Clean up formatting
        processed_text = re.sub(r'\s+', ' ', processed_text)  # Normalize whitespace
        processed_text = re.sub(r'\n+', ' ', processed_text)  # Remove line breaks
        
        # Enhance technical terms for better matching
        technical_replacements = {
            r'\bBCM\b': 'Billion Cubic Meters BCM',
            r'\bHa\.m\b': 'Hectare meters Ha.m',
            r'\bLpcd\b': 'Liters per capita per day Lpcd',
            r'\bGEC-2015\b': 'Groundwater Estimation Committee 2015 GEC-2015',
            r'\bCGWB\b': 'Central Ground Water Board CGWB'
        }
        
        for pattern, replacement in technical_replacements.items():
            processed_text = re.sub(pattern, replacement, processed_text, flags=re.IGNORECASE)
        
        # Enhance formula content
        if chunk_type == ChunkType.FORMULA:
            # Add context words for mathematical content
            if re.search(r'[=+\-*/]', processed_text):
                processed_text = "mathematical calculation formula equation " + processed_text
        
        # Enhance methodology content
        if chunk_type == ChunkType.METHODOLOGY:
            processed_text = "groundwater assessment methodology procedure " + processed_text
        
        return processed_text.strip()
    
    def add_chunks_to_vector_store(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """Add document chunks to the vector store with comprehensive metadata."""
        self.logger.info(f"Adding {len(chunks)} chunks to vector store...")
        
        # Prepare data for batch insertion
        chunk_ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        successful_adds = 0
        failed_adds = 0
        
        for chunk in chunks:
            try:
                # Handle large chunks by splitting if necessary
                sub_chunks = self._split_large_chunk(chunk) if len(chunk.content) > self.config.chunk_size_limit else [chunk]
                
                for i, sub_chunk in enumerate(sub_chunks):
                    # Generate unique ID for sub-chunks
                    chunk_id = f"{sub_chunk.chunk_id}_{i}" if len(sub_chunks) > 1 else sub_chunk.chunk_id
                    
                    # Enhance text for embedding
                    enhanced_text = self.enhance_text_for_embedding(
                        sub_chunk.content, 
                        sub_chunk.chunk_type, 
                        sub_chunk.metadata
                    )
                    
                    # Generate embedding
                    embedding = self.generate_embedding(enhanced_text, sub_chunk.chunk_type)
                    
                    # Prepare metadata for ChromaDB
                    chroma_metadata = self._prepare_chroma_metadata(sub_chunk)
                    
                    chunk_ids.append(chunk_id)
                    embeddings.append(embedding)
                    documents.append(sub_chunk.content)
                    metadatas.append(chroma_metadata)
                    
                    successful_adds += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to process chunk {chunk.chunk_id}: {str(e)}")
                failed_adds += 1
                continue
        
        # Batch insert into ChromaDB
        try:
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            self.logger.info(f"Successfully added {successful_adds} chunks to vector store")
        except Exception as e:
            self.logger.error(f"Failed to batch insert chunks: {str(e)}")
            raise
        
        return {
            "successful_adds": successful_adds,
            "failed_adds": failed_adds,
            "total_processed": len(chunks),
            "collection_size": self.collection.count()
        }
    
    def _split_large_chunk(self, chunk: DocumentChunk) -> List[DocumentChunk]:
        """Split large chunks while preserving context."""
        if len(chunk.content) <= self.config.chunk_size_limit:
            return [chunk]
        
        sub_chunks = []
        text = chunk.content
        start = 0
        
        while start < len(text):
            end = start + self.config.chunk_size_limit
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('!', start, end)
                if sentence_end == -1:
                    sentence_end = text.rfind('?', start, end)
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            # Create sub-chunk
            sub_content = text[start:end]
            
            # Add overlap for context continuity (except for first chunk)
            if start > 0:
                overlap_start = max(0, start - self.config.overlap_size)
                overlap_text = text[overlap_start:start]
                sub_content = f"[...{overlap_text}] {sub_content}"
            
            # Add continuation indicator (except for last chunk)
            if end < len(text):
                sub_content += " [continued...]"
            
            sub_chunk = DocumentChunk(
                chunk_id=chunk.chunk_id,
                chunk_type=chunk.chunk_type,
                title=chunk.title,
                content=sub_content,
                metadata=chunk.metadata,
                dependencies=chunk.dependencies,
                related_chunks=chunk.related_chunks,
                size_bytes=len(sub_content.encode('utf-8'))
            )
            
            sub_chunks.append(sub_chunk)
            start = end - self.config.overlap_size if end < len(text) else end
        
        return sub_chunks
    
    def _prepare_chroma_metadata(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Prepare metadata for ChromaDB storage with proper types."""
        metadata = {
            "chunk_type": chunk.chunk_type.value,
            "title": chunk.title,
            "size_bytes": chunk.size_bytes,
            "section_number": chunk.metadata.section_number or "",
            "hierarchy_level": chunk.metadata.hierarchy_level,
        }
        
        # Add list fields as JSON strings (ChromaDB limitation)
        if chunk.metadata.figure_references:
            metadata["figure_references"] = json.dumps(chunk.metadata.figure_references)
        
        if chunk.metadata.template_references:
            metadata["template_references"] = json.dumps(chunk.metadata.template_references)
        
        if chunk.metadata.formula_references:
            metadata["formula_references"] = json.dumps(chunk.metadata.formula_references)
        
        if chunk.metadata.user_roles:
            metadata["user_roles"] = json.dumps(chunk.metadata.user_roles)
        
        if chunk.metadata.assessment_categories:
            metadata["assessment_categories"] = json.dumps(chunk.metadata.assessment_categories)
        
        if chunk.metadata.aquifer_types:
            metadata["aquifer_types"] = json.dumps(chunk.metadata.aquifer_types)
        
        if chunk.metadata.component_type:
            metadata["component_type"] = chunk.metadata.component_type.value
        
        if chunk.dependencies:
            metadata["dependencies"] = json.dumps(chunk.dependencies)
        
        if chunk.related_chunks:
            metadata["related_chunks"] = json.dumps(chunk.related_chunks)

        # Persist data relationships if present (previously omitted, broke related lookups)
        if getattr(chunk.metadata, 'data_relationships', None):
            try:
                metadata["data_relationships"] = json.dumps(chunk.metadata.data_relationships)
            except Exception:
                pass
        
        return metadata
    
    def semantic_search(self, 
                       query: str, 
                       n_results: int = 10, 
                       chunk_types: List[ChunkType] = None,
                       component_types: List[ComponentType] = None,
                       user_roles: List[str] = None,
                       include_related: bool = True) -> List[SearchResult]:
        """Perform semantic search with advanced filtering."""
        
        # Enhance query for better matching
        enhanced_query = self._enhance_query(query)
        
        # Build filters
        where_filter = self._build_search_filter(chunk_types, component_types, user_roles)
        
        try:
            # Perform vector search
            results = self.collection.query(
                query_texts=[enhanced_query],
                n_results=min(n_results * 2, 50),  # Get more for filtering
                where=where_filter,
                include=["documents", "metadatas", "distances"]
            )
            
            search_results = []
            
            for i in range(len(results['ids'][0])):
                # Reconstruct metadata
                metadata_dict = results['metadatas'][0][i]
                metadata = self._reconstruct_metadata(metadata_dict)
                
                # Calculate relevance score (ChromaDB returns distances, convert to similarity)
                distance = results['distances'][0][i]
                similarity_score = 1 - distance if self.config.distance_function == 'cosine' else 1 / (1 + distance)
                
                search_result = SearchResult(
                    chunk_id=results['ids'][0][i],
                    content=results['documents'][0][i],
                    score=similarity_score,
                    chunk_type=ChunkType(metadata_dict['chunk_type']),
                    metadata=metadata,
                    highlights=self._extract_highlights(results['documents'][0][i], query)
                )
                
                search_results.append(search_result)
            
            # Sort by score and limit results
            search_results.sort(key=lambda x: x.score, reverse=True)
            search_results = search_results[:n_results]
            
            # Add related chunks if requested
            if include_related:
                search_results = self._add_related_chunks(search_results)
            
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []
    
    def _enhance_query(self, query: str) -> str:
        """Enhance query for better semantic matching."""
        enhanced_query = query
        
        # Add GEC-2015 context terms
        gec_terms = ['groundwater', 'assessment', 'methodology', 'water balance']
        query_lower = query.lower()
        
        for term in gec_terms:
            if term not in query_lower:
                enhanced_query += f" {term}"
        
        # Expand technical abbreviations
        abbreviations = {
            'bcm': 'billion cubic meters',
            'ha.m': 'hectare meters',
            'lpcd': 'liters per capita per day',
            'cgwb': 'central ground water board'
        }
        
        for abbr, expansion in abbreviations.items():
            if abbr in query_lower:
                enhanced_query += f" {expansion}"
        
        return enhanced_query
    
    def _build_search_filter(self, 
                           chunk_types: List[ChunkType] = None,
                           component_types: List[ComponentType] = None,
                           user_roles: List[str] = None) -> Dict[str, Any]:
        """Build ChromaDB where filter for search."""
        filters = []
        
        if chunk_types:
            chunk_type_values = [ct.value for ct in chunk_types]
            filters.append({"chunk_type": {"$in": chunk_type_values}})
        
        if component_types:
            component_values = [ct.value for ct in component_types]
            filters.append({"component_type": {"$in": component_values}})
        
        # For user roles, we need to check JSON strings (limitation of ChromaDB)
        if user_roles:
            # This is a simplified filter - in practice, you might need custom logic
            role_filters = []
            for role in user_roles:
                role_filters.append({"user_roles": {"$contains": role}})
            if role_filters:
                filters.append({"$or": role_filters})
        
        return {"$and": filters} if len(filters) > 1 else filters[0] if filters else {}
    
    def _extract_highlights(self, text: str, query: str, max_highlights: int = 3) -> List[str]:
        """Extract relevant highlights from text based on query."""
        query_terms = query.lower().split()
        sentences = re.split(r'[.!?]+', text)
        highlights = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                # Limit sentence length for highlights
                if len(sentence) > 200:
                    sentence = sentence[:200] + "..."
                highlights.append(sentence.strip())
                
                if len(highlights) >= max_highlights:
                    break
        
        return highlights
    
    def _reconstruct_metadata(self, metadata_dict: Dict[str, Any]) -> ChunkMetadata:
        """Reconstruct ChunkMetadata from ChromaDB metadata."""
        metadata = ChunkMetadata(
            section_number=metadata_dict.get('section_number', ''),
            hierarchy_level=metadata_dict.get('hierarchy_level', 0)
        )
        
        # Reconstruct list fields from JSON strings
        json_fields = [
            'figure_references', 'template_references', 'formula_references',
            'user_roles', 'assessment_categories', 'aquifer_types', 'data_relationships'
        ]
        
        for field in json_fields:
            if field in metadata_dict and metadata_dict[field]:
                try:
                    setattr(metadata, field, json.loads(metadata_dict[field]))
                except json.JSONDecodeError:
                    pass
        
        # Reconstruct component type
        if 'component_type' in metadata_dict and metadata_dict['component_type']:
            try:
                metadata.component_type = ComponentType(metadata_dict['component_type'])
            except ValueError:
                pass
        
        return metadata
    
    def _add_related_chunks(self, search_results: List[SearchResult], max_related: int = 2) -> List[SearchResult]:
        """Add related chunks to search results."""
        enhanced_results = []
        
        for result in search_results:
            enhanced_results.append(result)
            
            # Add related chunks based on metadata
            if hasattr(result.metadata, 'data_relationships') and result.metadata.data_relationships:
                related_chunks = self._find_related_chunks(result.metadata.data_relationships, max_related)
                result.related_chunks = [chunk.chunk_id for chunk in related_chunks]
                enhanced_results.extend(related_chunks[:max_related])
        
        return enhanced_results
    
    def _find_related_chunks(self, relationships: List[str], limit: int) -> List[SearchResult]:
        """Find chunks related by data relationships."""
        # This is a simplified implementation
        # In practice, you might want more sophisticated relationship tracking
        related_results = []
        
        for relationship in relationships[:limit]:
            try:
                results = self.collection.query(
                    query_texts=[relationship],
                    n_results=1,
                    include=["documents", "metadatas", "distances"]
                )
                
                if results['ids'][0]:
                    metadata = self._reconstruct_metadata(results['metadatas'][0][0])
                    related_result = SearchResult(
                        chunk_id=results['ids'][0][0],
                        content=results['documents'][0][0],
                        score=0.8,  # Related chunk score
                        chunk_type=ChunkType(results['metadatas'][0][0]['chunk_type']),
                        metadata=metadata
                    )
                    related_results.append(related_result)
            except:
                continue
        
        return related_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the vector collection."""
        try:
            total_count = self.collection.count()
            
            # Get sample of documents to analyze
            sample_size = min(100, total_count)
            sample_results = self.collection.get(limit=sample_size, include=["metadatas"])
            
            stats = {
                "total_documents": total_count,
                "embedding_dimension": self.config.embedding_dimension,
                "model_name": self.config.model_name,
                "chunk_type_distribution": {},
                "component_type_distribution": {},
                "average_chunk_size": 0,
                "collection_health": "good"
            }
            
            if sample_results['metadatas']:
                # Analyze chunk types
                chunk_types = [meta['chunk_type'] for meta in sample_results['metadatas']]
                for chunk_type in set(chunk_types):
                    stats["chunk_type_distribution"][chunk_type] = chunk_types.count(chunk_type)
                
                # Analyze component types
                component_types = [meta.get('component_type', '') for meta in sample_results['metadatas']]
                component_types = [ct for ct in component_types if ct]
                for comp_type in set(component_types):
                    stats["component_type_distribution"][comp_type] = component_types.count(comp_type)
                
                # Average chunk size
                sizes = [meta.get('size_bytes', 0) for meta in sample_results['metadatas']]
                stats["average_chunk_size"] = sum(sizes) / len(sizes) if sizes else 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {str(e)}")
            return {"error": str(e)}
    
    def delete_collection(self):
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.config.collection_name)
            self.logger.info(f"Deleted collection: {self.config.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to delete collection: {str(e)}")

# Usage Example and Testing
class GEC2015VectorManager:
    """High-level manager for GEC-2015 vector operations."""
    
    def __init__(self, persist_directory: str = "./gec2015_vectors"):
        self.config = EmbeddingConfig(persist_directory=persist_directory)
        self.vector_store = GEC2015VectorStore(self.config)
        self.chunker = GEC2015DocumentChunker()
        self.logger = logging.getLogger(__name__)
    
    def process_and_store_document(self, document_text: str) -> Dict[str, Any]:
        """Complete pipeline: chunk document and store in vector database."""
        self.logger.info("Starting document processing pipeline...")
        
        # Step 1: Chunk the document
        chunks = self.chunker.process_document(document_text)
        self.logger.info(f"Created {len(chunks)} chunks")
        
        # Step 2: Store in vector database
        storage_result = self.vector_store.add_chunks_to_vector_store(chunks)
        self.logger.info(f"Stored chunks in vector database: {storage_result}")
        
        return {
            "chunks_created": len(chunks),
            "storage_result": storage_result,
            "collection_stats": self.vector_store.get_collection_stats()
        }
    
    def search_knowledge(self, 
                        query: str, 
                        search_type: str = "comprehensive",
                        n_results: int = 10) -> List[SearchResult]:
        """Search the knowledge base with different search strategies."""
        
        if search_type == "methodology":
            return self.vector_store.semantic_search(
                query, n_results, 
                chunk_types=[ChunkType.METHODOLOGY, ChunkType.FORMULA]
            )
        elif search_type == "templates":
            return self.vector_store.semantic_search(
                query, n_results,
                chunk_types=[ChunkType.TEMPLATE]
            )
        elif search_type == "workflows":
            return self.vector_store.semantic_search(
                query, n_results,
                chunk_types=[ChunkType.WORKFLOW, ChunkType.USER_ROLE]
            )
        else:  # comprehensive
            return self.vector_store.semantic_search(query, n_results)

    # ---------------- Utility: Load chunks from previously exported JSON ---------------- #
    def load_chunks_from_json(self, json_path: Union[str, Path]) -> List[DocumentChunk]:
        """Load chunks exported by chunking_usermanual.export_chunks_to_json.

        The JSON is a list of serialized chunk dicts.
        """
        path = Path(json_path)
        if not path.exists():
            raise FileNotFoundError(f"Chunk JSON not found: {json_path}")
        data = json.loads(path.read_text(encoding='utf-8'))
        chunks: List[DocumentChunk] = []
        for item in data:
            meta_dict = item.get('metadata', {})
            component_type = meta_dict.get('component_type')
            if component_type:
                try:
                    meta_dict['component_type'] = ComponentType(component_type)
                except ValueError:
                    meta_dict['component_type'] = None
            metadata = ChunkMetadata(**{k: v for k, v in meta_dict.items() if k in ChunkMetadata.__annotations__})
            chunk = DocumentChunk(
                chunk_id=item['chunk_id'],
                chunk_type=ChunkType(item['chunk_type']),
                title=item.get('title', ''),
                content=item.get('content', ''),
                metadata=metadata,
                dependencies=item.get('dependencies', []),
                related_chunks=item.get('related_chunks', []),
                size_bytes=item.get('size_bytes', len(item.get('content', '').encode('utf-8')))
            )
            chunks.append(chunk)
        return chunks

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    
    parser = argparse.ArgumentParser(description="GEC-2015 Vector Store Operations")
    parser.add_argument('--action', choices=['init', 'ingest', 'search', 'stats'], 
                       default='init', help='Action to perform')
    parser.add_argument('--chunks-json', default='gec_usermanual_chunks.json', 
                       help='Path to chunks JSON file for ingestion')
    parser.add_argument('--query', help='Search query for testing')
    parser.add_argument('--search-type', default='comprehensive',
                       choices=['comprehensive', 'methodology', 'templates', 'workflows'],
                       help='Type of search to perform')
    parser.add_argument('--results', type=int, default=5, help='Number of search results')
    
    args = parser.parse_args()
    
    try:
        # Initialize the vector manager
        manager = GEC2015VectorManager()
        print("GEC-2015 Vector Store System initialized successfully!")
        
        if args.action == 'stats':
            stats = manager.vector_store.get_collection_stats()
            print(f"Collection Stats: {json.dumps(stats, indent=2)}")
            
        elif args.action == 'ingest':
            if not Path(args.chunks_json).exists():
                print(f"❌ Chunks file not found: {args.chunks_json}")
                print("Run: python chunking_usermanual.py to generate chunks first")
                sys.exit(1)
                
            print(f"📥 Loading chunks from {args.chunks_json}...")
            chunks = manager.load_chunks_from_json(args.chunks_json)
            print(f"✅ Loaded {len(chunks)} chunks")
            
            print("🔄 Adding chunks to vector store...")
            result = manager.vector_store.add_chunks_to_vector_store(chunks)
            print(f"✅ Ingestion complete: {result}")
            
            stats = manager.vector_store.get_collection_stats()
            print(f"📊 Final collection size: {stats.get('total_documents', 0)} documents")
            
        elif args.action == 'search':
            if not args.query:
                print("❌ Please provide --query for search")
                sys.exit(1)
                
            print(f"🔍 Searching: '{args.query}' (type: {args.search_type})")
            results = manager.search_knowledge(args.query, args.search_type, args.results)
            
            print(f"\n📋 Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.title} (Score: {result.score:.3f})")
                print(f"   Type: {result.chunk_type.value}")
                print(f"   ID: {result.chunk_id}")
                if result.highlights:
                    print(f"   Highlights: {result.highlights[0][:200]}...")
                print(f"   Content: {result.content[:300]}...")
                
        else:  # init
            stats = manager.vector_store.get_collection_stats()
            print(f"📊 Current collection: {stats.get('total_documents', 0)} documents")
            print("\nNext steps:")
            print("1. Generate chunks: python chunking_usermanual.py")
            print("2. Ingest chunks: python vectorstore_usermanual.py --action ingest")
            print("3. Test search: python vectorstore_usermanual.py --action search --query 'water balance'")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise