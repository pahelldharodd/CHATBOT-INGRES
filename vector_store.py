import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from sentence_transformers import SentenceTransformer
import faiss
import pickle
from pathlib import Path
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Metadata structure for each chunk"""
    chunk_id: str
    chunk_type: str  # 'text', 'table', 'image'
    content_type: str  # 'state_summary', 'district_comparison', etc.
    state: Optional[str] = None
    district: Optional[str] = None
    assessment_unit: Optional[str] = None
    year: Optional[str] = None
    page_number: Optional[int] = None
    table_id: Optional[str] = None
    image_id: Optional[str] = None
    source_section: Optional[str] = None

@dataclass
class EmbeddedChunk:
    """Structure for chunks with embeddings"""
    chunk_id: str
    content: str
    embedding: np.ndarray
    metadata: ChunkMetadata
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'embedding': self.embedding.tolist(),  # Convert numpy array to list
            'metadata': asdict(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            chunk_id=data['chunk_id'],
            content=data['content'],
            embedding=np.array(data['embedding']),
            metadata=ChunkMetadata(**data['metadata'])
        )

class GroundwaterEmbeddingPipeline:
    """Main embedding pipeline for groundwater data"""
    
    def __init__(self, 
                 model_name: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 embedding_dim: int = 384):
        """
        Initialize the embedding pipeline
        
        Args:
            model_name: Sentence transformer model name
            embedding_dim: Dimension of embeddings
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model = SentenceTransformer(model_name)
        self.embedded_chunks: List[EmbeddedChunk] = []
        self.index = None
        self.chunk_lookup: Dict[int, str] = {}  # Maps index position to chunk_id
        
        logger.info(f"Initialized embedding pipeline with model: {model_name}")
    
    def load_chunks_from_json(self, json_file_path: str) -> Dict:
        """
        Load chunks from JSON file created by chunking process
        
        Args:
            json_file_path: Path to the JSON file containing chunks
            
        Returns:
            Dictionary containing all chunks organized by type
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
            
            logger.info(f"Loaded chunks from {json_file_path}")
            logger.info(f"Found chunk types: {list(chunks_data.keys())}")
            return chunks_data
            
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            raise
    
    def process_text_chunks(self, text_chunks: List[Dict]) -> List[EmbeddedChunk]:
        """Process text chunks and create embeddings"""
        embedded_chunks = []
        
        logger.info(f"Processing {len(text_chunks)} text chunks")
        
        for chunk in text_chunks:
            try:
                # Extract content for embedding
                content = chunk.get('content', '')
                if not content.strip():
                    continue
                
                # Create metadata
                metadata = ChunkMetadata(
                    chunk_id=chunk['chunk_id'],
                    chunk_type='text',
                    content_type=chunk.get('content_type', 'general'),
                    state=chunk.get('state'),
                    district=chunk.get('district'),
                    assessment_unit=chunk.get('assessment_unit'),
                    year=chunk.get('year'),
                    page_number=chunk.get('page_number'),
                    source_section=chunk.get('source_section')
                )
                
                # Generate embedding
                embedding = self.model.encode(content)
                
                embedded_chunk = EmbeddedChunk(
                    chunk_id=chunk['chunk_id'],
                    content=content,
                    embedding=embedding,
                    metadata=metadata
                )
                
                embedded_chunks.append(embedded_chunk)
                
            except Exception as e:
                logger.error(f"Error processing text chunk {chunk.get('chunk_id')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(embedded_chunks)} text chunks")
        return embedded_chunks
    
    def process_table_chunks(self, table_chunks: List[Dict]) -> List[EmbeddedChunk]:
        """Process table chunks and create embeddings"""
        embedded_chunks = []
        
        logger.info(f"Processing {len(table_chunks)} table chunks")
        
        for chunk in table_chunks:
            try:
                # Create searchable text from table data
                content = self._create_table_searchable_text(chunk)
                
                if not content.strip():
                    continue
                
                # Create metadata
                metadata = ChunkMetadata(
                    chunk_id=chunk['chunk_id'],
                    chunk_type='table',
                    content_type=chunk.get('table_type', 'general'),
                    state=chunk.get('state'),
                    district=chunk.get('district'),
                    assessment_unit=chunk.get('assessment_unit'),
                    year=chunk.get('year'),
                    page_number=chunk.get('page_number'),
                    table_id=chunk.get('table_id')
                )
                
                # Generate embedding
                embedding = self.model.encode(content)
                
                embedded_chunk = EmbeddedChunk(
                    chunk_id=chunk['chunk_id'],
                    content=content,
                    embedding=embedding,
                    metadata=metadata
                )
                
                embedded_chunks.append(embedded_chunk)
                
            except Exception as e:
                logger.error(f"Error processing table chunk {chunk.get('chunk_id')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(embedded_chunks)} table chunks")
        return embedded_chunks
    
    def process_image_chunks(self, image_chunks: List[Dict]) -> List[EmbeddedChunk]:
        """Process image chunks (metadata) and create embeddings"""
        embedded_chunks = []
        
        logger.info(f"Processing {len(image_chunks)} image chunks")
        
        for chunk in image_chunks:
            try:
                # Create searchable text from image metadata
                content = self._create_image_searchable_text(chunk)
                
                if not content.strip():
                    continue
                
                # Create metadata
                metadata = ChunkMetadata(
                    chunk_id=chunk['chunk_id'],
                    chunk_type='image',
                    content_type=chunk.get('image_type', 'general'),
                    state=chunk.get('state'),
                    district=chunk.get('district'),
                    year=chunk.get('year'),
                    page_number=chunk.get('page_number'),
                    image_id=chunk.get('image_id')
                )
                
                # Generate embedding
                embedding = self.model.encode(content)
                
                embedded_chunk = EmbeddedChunk(
                    chunk_id=chunk['chunk_id'],
                    content=content,
                    embedding=embedding,
                    metadata=metadata
                )
                
                embedded_chunks.append(embedded_chunk)
                
            except Exception as e:
                logger.error(f"Error processing image chunk {chunk.get('chunk_id')}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(embedded_chunks)} image chunks")
        return embedded_chunks
    
    def _create_table_searchable_text(self, table_chunk: Dict) -> str:
        """Create searchable text from table data"""
        searchable_parts = []
        
        # Add table metadata
        if table_chunk.get('table_type'):
            searchable_parts.append(f"Table type: {table_chunk['table_type']}")
        
        if table_chunk.get('state'):
            searchable_parts.append(f"State: {table_chunk['state']}")
        
        if table_chunk.get('district'):
            searchable_parts.append(f"District: {table_chunk['district']}")
        
        # Add table content
        table_data = table_chunk.get('table_data', {})
        
        # Handle different table formats
        if isinstance(table_data, dict):
            # Handle structured table data
            if 'headers' in table_data and 'rows' in table_data:
                headers = table_data['headers']
                rows = table_data['rows']
                
                # Add headers
                searchable_parts.append(f"Columns: {', '.join(headers)}")
                
                # Add sample row data (first few rows to avoid too much text)
                for i, row in enumerate(rows[:3]):  # Only first 3 rows
                    row_text = []
                    for j, cell in enumerate(row):
                        if j < len(headers):
                            row_text.append(f"{headers[j]}: {cell}")
                    searchable_parts.append(' | '.join(row_text))
            
            # Handle key-value table data
            else:
                for key, value in table_data.items():
                    if isinstance(value, (str, int, float)):
                        searchable_parts.append(f"{key}: {value}")
        
        # Add remarks if available
        if table_chunk.get('remarks'):
            searchable_parts.append(f"Remarks: {table_chunk['remarks']}")
        
        return ' | '.join(searchable_parts)
    
    def _create_image_searchable_text(self, image_chunk: Dict) -> str:
        """Create searchable text from image metadata"""
        searchable_parts = []
        
        # Add image metadata
        if image_chunk.get('caption'):
            searchable_parts.append(f"Caption: {image_chunk['caption']}")
        
        if image_chunk.get('image_type'):
            searchable_parts.append(f"Image type: {image_chunk['image_type']}")
        
        if image_chunk.get('state'):
            searchable_parts.append(f"State: {image_chunk['state']}")
        
        if image_chunk.get('district'):
            searchable_parts.append(f"District: {image_chunk['district']}")
        
        if image_chunk.get('data_type'):
            searchable_parts.append(f"Data type: {image_chunk['data_type']}")
        
        if image_chunk.get('temporal_scope'):
            searchable_parts.append(f"Time period: {image_chunk['temporal_scope']}")
        
        # Add extracted text if available
        if image_chunk.get('extracted_text'):
            searchable_parts.append(f"Text content: {image_chunk['extracted_text']}")
        
        return ' | '.join(searchable_parts)
    
    def create_embeddings_from_json(self, json_file_path: str) -> None:
        """
        Main method to create embeddings from JSON chunks file
        
        Args:
            json_file_path: Path to JSON file containing chunks
        """
        logger.info("Starting embedding creation process")
        
        # Load chunks from JSON
        chunks_data = self.load_chunks_from_json(json_file_path)
        
        all_embedded_chunks = []
        
        # Process different chunk types
        if 'text_chunks' in chunks_data:
            text_embedded = self.process_text_chunks(chunks_data['text_chunks'])
            all_embedded_chunks.extend(text_embedded)
        
        if 'table_chunks' in chunks_data:
            table_embedded = self.process_table_chunks(chunks_data['table_chunks'])
            all_embedded_chunks.extend(table_embedded)
        
        if 'image_chunks' in chunks_data:
            image_embedded = self.process_image_chunks(chunks_data['image_chunks'])
            all_embedded_chunks.extend(image_embedded)
        
        self.embedded_chunks = all_embedded_chunks
        logger.info(f"Total embedded chunks created: {len(self.embedded_chunks)}")
    
    def build_faiss_index(self, index_type: str = 'flat') -> None:
        """
        Build FAISS index from embeddings
        
        Args:
            index_type: Type of FAISS index ('flat', 'ivf', 'hnsw')
        """
        if not self.embedded_chunks:
            raise ValueError("No embedded chunks available. Run create_embeddings_from_json first.")
        
        logger.info(f"Building FAISS index with {len(self.embedded_chunks)} chunks")
        
        # Create embedding matrix
        embeddings = np.array([chunk.embedding for chunk in self.embedded_chunks])
        embeddings = embeddings.astype('float32')  # FAISS requires float32
        
        # Build index based on type
        if index_type == 'flat':
            # Simple flat index - exact search
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product similarity
        elif index_type == 'ivf':
            # Inverted file index - faster approximate search
            nlist = min(100, len(self.embedded_chunks) // 4)  # Number of clusters
            quantizer = faiss.IndexFlatIP(self.embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, nlist)
            self.index.train(embeddings)
        elif index_type == 'hnsw':
            # Hierarchical NSW - very fast approximate search
            self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
            self.index.hnsw.efConstruction = 64
        else:
            raise ValueError(f"Unsupported index type: {index_type}")
        
        # Add embeddings to index
        self.index.add(embeddings)
        
        # Create chunk lookup
        self.chunk_lookup = {i: chunk.chunk_id for i, chunk in enumerate(self.embedded_chunks)}
        
        logger.info(f"FAISS index built successfully. Index size: {self.index.ntotal}")
    
    def search_similar_chunks(self, 
                            query: str, 
                            k: int = 5,
                            chunk_types: Optional[List[str]] = None,
                            state_filter: Optional[str] = None,
                            district_filter: Optional[str] = None,
                            year_filter: Optional[str] = None) -> List[Tuple[EmbeddedChunk, float]]:
        """
        Search for similar chunks using FAISS
        
        Args:
            query: Search query
            k: Number of results to return
            chunk_types: Filter by chunk types ('text', 'table', 'image')
            state_filter: Filter by state name
            district_filter: Filter by district name
            year_filter: Filter by year
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        if self.index is None:
            raise ValueError("FAISS index not built. Run build_faiss_index first.")
        
        # Generate query embedding
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search in FAISS (get more results for filtering)
        search_k = min(k * 10, self.index.ntotal)  # Get extra results for filtering
        distances, indices = self.index.search(query_embedding, search_k)
        
        results = []
        
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid index
                continue
            
            chunk = self.embedded_chunks[idx]
            
            # Apply filters
            if chunk_types and chunk.metadata.chunk_type not in chunk_types:
                continue
            
            if state_filter and chunk.metadata.state != state_filter:
                continue
            
            if district_filter and chunk.metadata.district != district_filter:
                continue
            
            if year_filter and chunk.metadata.year != year_filter:
                continue
            
            results.append((chunk, float(distance)))
            
            if len(results) >= k:
                break
        
        return results
    
    def save_embeddings(self, save_path: str) -> None:
        """Save embeddings and index to disk"""
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        if self.index is not None:
            faiss.write_index(self.index, str(save_dir / "faiss_index.bin"))
            logger.info("FAISS index saved")
        
        # Save embedded chunks (without embeddings to save space)
        chunks_data = []
        for chunk in self.embedded_chunks:
            chunk_dict = chunk.to_dict()
            chunk_dict.pop('embedding', None)  # Remove embedding to save space
            chunks_data.append(chunk_dict)
        
        with open(save_dir / "embedded_chunks.json", 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        
        # Save chunk lookup
        with open(save_dir / "chunk_lookup.pkl", 'wb') as f:
            pickle.dump(self.chunk_lookup, f)
        
        # Save pipeline metadata
        metadata = {
            'model_name': self.model_name,
            'embedding_dim': self.embedding_dim,
            'num_chunks': len(self.embedded_chunks),
            'created_at': datetime.now().isoformat()
        }
        
        with open(save_dir / "pipeline_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Embeddings saved to {save_path}")
    
    def load_embeddings(self, load_path: str) -> None:
        """Load embeddings and index from disk"""
        load_dir = Path(load_path)
        
        if not load_dir.exists():
            raise FileNotFoundError(f"Load path not found: {load_path}")
        
        # Load FAISS index
        if (load_dir / "faiss_index.bin").exists():
            self.index = faiss.read_index(str(load_dir / "faiss_index.bin"))
            logger.info("FAISS index loaded")
        
        # Load chunk lookup
        with open(load_dir / "chunk_lookup.pkl", 'rb') as f:
            self.chunk_lookup = pickle.load(f)
        
        # Load embedded chunks (without embeddings)
        with open(load_dir / "embedded_chunks.json", 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        self.embedded_chunks = []
        for chunk_dict in chunks_data:
            # Create dummy embedding (not needed for search)
            chunk_dict['embedding'] = np.zeros(self.embedding_dim)
            self.embedded_chunks.append(EmbeddedChunk.from_dict(chunk_dict))
        
        logger.info(f"Embeddings loaded from {load_path}")


# Usage Example
def main():
    """Example usage of the embedding pipeline"""
    
    # Initialize pipeline
    pipeline = GroundwaterEmbeddingPipeline()
    
    # Create embeddings from chunks JSON file
    pipeline.create_embeddings_from_json("groundwater_chunks.json")
    
    # Build FAISS index
    pipeline.build_faiss_index(index_type='flat')
    
    # Save embeddings for future use
    pipeline.save_embeddings("./embeddings_data")
    
    # Example searches
    queries = [
        "Which districts in Maharashtra improved in 2024?",
        "Over-exploited groundwater areas",
        "State wise summary of assessment units",
        "Groundwater extraction percentage changes"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = pipeline.search_similar_chunks(query, k=3)
        
        for i, (chunk, score) in enumerate(results, 1):
            print(f"  {i}. Score: {score:.4f}")
            print(f"     Type: {chunk.metadata.chunk_type}")
            print(f"     Content: {chunk.content[:200]}...")
            if chunk.metadata.state:
                print(f"     State: {chunk.metadata.state}")
            if chunk.metadata.district:
                print(f"     District: {chunk.metadata.district}")

if __name__ == "__main__":
    main()