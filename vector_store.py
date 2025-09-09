
import json
import numpy as np
import re
import faiss
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pickle
from sentence_transformers import SentenceTransformer



@dataclass
class EmbeddingConfig:
    model_name: str = "all-mpnet-base-v2"
    chunk_size_limit: int = 8000
    normalize_embeddings: bool = True

@dataclass
class FAISSConfig:
    index_type: str = "IVF"
    nlist: int = 100
    nprobe: int = 10
    dimension: int = 768
    metric: str = "COSINE"

class INGRESEmbeddingPipeline:
    def __init__(self, embedding_config: EmbeddingConfig = None, faiss_config: FAISSConfig = None):
        self.embedding_config = embedding_config or EmbeddingConfig()
        self.faiss_config = faiss_config or FAISSConfig()
        self.embedding_model = None
        self.base_path = Path("faiss_indexes")
        self.base_path.mkdir(exist_ok=True)
        self.indexes = {}
        self.chunk_metadata = {}

    def _initialize_embedding_model(self):
        self.embedding_model = SentenceTransformer(self.embedding_config.model_name)
        self.faiss_config.dimension = self.embedding_model.get_sentence_embedding_dimension()

    def _preprocess_text_for_embedding(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        if len(text) > self.embedding_config.chunk_size_limit:
            text = text[:self.embedding_config.chunk_size_limit] + "..."
        return text

    def _generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        if not texts:
            return np.array([])
        embeddings = self.embedding_model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=self.embedding_config.normalize_embeddings
        )
        return embeddings.astype(np.float32)

    def _create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        dimension = embeddings.shape[1]
        if self.faiss_config.index_type == "FLAT":
            if self.faiss_config.metric == "COSINE":
                index = faiss.IndexFlatIP(dimension)
            else:
                index = faiss.IndexFlatL2(dimension)
        elif self.faiss_config.index_type == "IVF":
            nlist = min(self.faiss_config.nlist, max(1, len(embeddings) // 10))
            quantizer = faiss.IndexFlatL2(dimension)
            if self.faiss_config.metric == "COSINE":
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
            else:
                index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
        else:
            index = faiss.IndexFlatL2(dimension)
        if self.faiss_config.metric == "COSINE":
            faiss.normalize_L2(embeddings)
        if hasattr(index, 'train'):
            index.train(embeddings)
        index.add(embeddings)
        return index

    def load_chunks_from_json(self, json_files: List[str]) -> List[Dict]:
        all_chunks = []
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for chunk_type in ['hierarchical_chunks', 'parameter_chunks', 'quality_chunks']:
                all_chunks.extend(data.get(chunk_type, []))
        return all_chunks

    def create_embeddings_and_index(self, chunks: List[Dict]) -> None:
        self._initialize_embedding_model()
        texts = [self._preprocess_text_for_embedding(chunk.get('content', '')) for chunk in chunks]
        embeddings = self._generate_embeddings(texts)
        if embeddings.size > 0:
            index = self._create_faiss_index(embeddings)
            self.indexes['unified'] = index
            self.chunk_metadata['unified'] = chunks
            self._save_index(index, 'unified')
            self._save_metadata(chunks, 'unified')

    def _save_index(self, index: faiss.Index, index_name: str):
        index_path = self.base_path / f"{index_name}_index.faiss"
        faiss.write_index(index, str(index_path))

    def _save_metadata(self, metadata: List[Dict], index_name: str):
        metadata_path = self.base_path / f"{index_name}_metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)

def main():
    config = EmbeddingConfig(
        model_name="all-mpnet-base-v2",
        chunk_size_limit=6000
    )
    faiss_config = FAISSConfig(
        index_type="IVF",
        nlist=200,
        nprobe=20
    )
    pipeline = INGRESEmbeddingPipeline(config, faiss_config)
    json_files = ["INGRES_2019-20_cleaned_chunks.json", "INGRES_2024-25_cleaned_chunks.json"]
    chunks = pipeline.load_chunks_from_json(json_files)
    pipeline.create_embeddings_and_index(chunks)

if __name__ == "__main__":
    main()
            
            # Hydrogeological info
    
    def load_chunks_from_json(self, json_files: List[str]) -> Dict[str, List[Dict]]:
        """Load and organize chunks from JSON files"""
        all_chunks = {
            'hierarchical': [],
            'parameter': [],
            'quality': []
        }
        
        total_chunks = 0
        
        for json_file in json_files:
            try:
                logger.info(f"Loading chunks from {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Categorize chunks
                hierarchical_chunks = data.get('hierarchical_chunks', [])
                parameter_chunks = data.get('parameter_chunks', [])
                quality_chunks = data.get('quality_chunks', [])
                
                all_chunks['hierarchical'].extend(hierarchical_chunks)
                all_chunks['parameter'].extend(parameter_chunks)
                all_chunks['quality'].extend(quality_chunks)
                
                file_total = len(hierarchical_chunks) + len(parameter_chunks) + len(quality_chunks)
                total_chunks += file_total
                
                logger.info(f"Loaded {file_total} chunks from {json_file}")
                
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        logger.info(f"Total chunks loaded: {total_chunks}")
        logger.info(f"Hierarchical: {len(all_chunks['hierarchical'])}, "
                   f"Parameter: {len(all_chunks['parameter'])}, "
                   f"Quality: {len(all_chunks['quality'])}")
        
        return all_chunks
    
    def create_embeddings_and_indexes(self, chunks_data: Dict[str, List[Dict]], 
                                    separate_indexes: bool = True) -> Dict[str, Any]:
        """Create embeddings and FAISS indexes for chunks"""
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        results = {
            'indexes_created': [],
            'total_embeddings': 0,
            'processing_stats': {}
        }
        
        if separate_indexes:
            # Create separate indexes for each chunk type
            for chunk_type, chunks in chunks_data.items():
                if not chunks:
                    logger.info(f"No chunks found for type: {chunk_type}")
                    continue
                
                logger.info(f"Processing {len(chunks)} chunks for type: {chunk_type}")
                
                # Extract features and prepare texts
                chunk_features = []
                texts_to_embed = []
                
                for i, chunk in enumerate(chunks):
                    features = self._extract_chunk_features(chunk)
                    chunk_features.append(features)
                    
                    # Prepare text for embedding
                    enhanced_text = self._preprocess_text_for_embedding(
                        features['content'], 
                        chunk.get('metadata')
                    )
                    texts_to_embed.append(enhanced_text)
                    
                    # Store chunk mapping
                    chunk_id = features['chunk_id'] or f"{chunk_type}_{i}"
                    self.id_to_chunk_mapping[chunk_id] = {
                        'chunk_type': chunk_type,
                        'original_chunk': chunk,
                        'features': features,
                        'index_id': i
                    }
                
                # Generate embeddings
                embeddings = self._generate_embeddings(texts_to_embed)
                
                if embeddings.size > 0:
                    # Create FAISS index
                    index = self._create_faiss_index(embeddings, chunk_type)
                    self.indexes[chunk_type] = index
                    self.chunk_metadata[chunk_type] = chunk_features
                    
                    # Save index and metadata
                    self._save_index(index, chunk_type)
                    self._save_metadata(chunk_features, chunk_type)
                    
                    results['indexes_created'].append(chunk_type)
                    results['total_embeddings'] += len(embeddings)
                    results['processing_stats'][chunk_type] = {
                        'chunks_processed': len(chunks),
                        'embeddings_created': len(embeddings),
                        'average_chunk_size': np.mean([f['chunk_size'] for f in chunk_features])
                    }
                    
                    logger.info(f"Created index for {chunk_type}: {len(embeddings)} embeddings")
        
        else:
            # Create single unified index
            logger.info("Creating unified index for all chunk types")
            
            all_chunks = []
            all_features = []
            texts_to_embed = []
            
            for chunk_type, chunks in chunks_data.items():
                for i, chunk in enumerate(chunks):
                    features = self._extract_chunk_features(chunk)
                    features['original_chunk_type'] = chunk_type
                    all_features.append(features)
                    
                    enhanced_text = self._preprocess_text_for_embedding(
                        features['content'], 
                        chunk.get('metadata')
                    )
                    texts_to_embed.append(enhanced_text)
                    
                    chunk_id = features['chunk_id'] or f"{chunk_type}_{i}"
                    self.id_to_chunk_mapping[chunk_id] = {
                        'chunk_type': chunk_type,
                        'original_chunk': chunk,
                        'features': features,
                        'index_id': len(all_chunks)
                    }
                    all_chunks.append(chunk)
            
            if texts_to_embed:
                embeddings = self._generate_embeddings(texts_to_embed)
                
                if embeddings.size > 0:
                    index = self._create_faiss_index(embeddings, 'unified')
                    self.indexes['unified'] = index
                    self.chunk_metadata['unified'] = all_features
                    
                    self._save_index(index, 'unified')
                    self._save_metadata(all_features, 'unified')
                    
                    results['indexes_created'].append('unified')
                    results['total_embeddings'] = len(embeddings)
                    results['processing_stats']['unified'] = {
                        'chunks_processed': len(all_chunks),
                        'embeddings_created': len(embeddings),
                        'average_chunk_size': np.mean([f['chunk_size'] for f in all_features])
                    }
        
        # Create TF-IDF index for hybrid search
        if texts_to_embed:
            logger.info("Creating TF-IDF index for hybrid search")
            self._create_tfidf_index(texts_to_embed)
        
        logger.info(f"Index creation completed. Total embeddings: {results['total_embeddings']}")
        return results
    
    def _create_tfidf_index(self, texts: List[str]):
        """Create TF-IDF index for keyword-based search"""
        try:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Save TF-IDF vectorizer and matrix
            tfidf_path = self.base_path / "tfidf_vectorizer.pkl"
            matrix_path = self.base_path / "tfidf_matrix.pkl"
            
            with open(tfidf_path, 'wb') as f:
                pickle.dump(self.tfidf_vectorizer, f)
            
            with open(matrix_path, 'wb') as f:
                pickle.dump(tfidf_matrix, f)
            
            logger.info(f"Created TF-IDF index with {tfidf_matrix.shape[0]} documents and {tfidf_matrix.shape[1]} features")
            
        except Exception as e:
            logger.error(f"Error creating TF-IDF index: {e}")
    
    def _save_index(self, index: faiss.Index, index_name: str):
        """Save FAISS index to disk"""
        try:
            index_path = self.base_path / f"{index_name}_index.faiss"
            faiss.write_index(index, str(index_path))
            logger.info(f"Saved {index_name} index to {index_path}")
        except Exception as e:
            logger.error(f"Error saving {index_name} index: {e}")
    
    def _save_metadata(self, metadata: List[Dict], index_name: str):
        """Save chunk metadata to disk"""
        try:
            metadata_path = self.base_path / f"{index_name}_metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            logger.info(f"Saved {index_name} metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Error saving {index_name} metadata: {e}")
    
    def load_indexes_and_metadata(self) -> bool:
        """Load existing indexes and metadata from disk"""
        try:
            index_files = list(self.base_path.glob("*_index.faiss"))
            
            for index_file in index_files:
                index_name = index_file.stem.replace("_index", "")
                metadata_file = self.base_path / f"{index_name}_metadata.pkl"
                
                if metadata_file.exists():
                    # Load FAISS index
                    index = faiss.read_index(str(index_file))
                    self.indexes[index_name] = index
                    
                    # Load metadata
                    with open(metadata_file, 'rb') as f:
                        metadata = pickle.load(f)
                    self.chunk_metadata[index_name] = metadata
                    
                    logger.info(f"Loaded {index_name} index with {index.ntotal} vectors")
            
            # Load TF-IDF components
            tfidf_path = self.base_path / "tfidf_vectorizer.pkl"
            if tfidf_path.exists():
                with open(tfidf_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                logger.info("Loaded TF-IDF vectorizer")
            
            # Load chunk mappings
            mapping_path = self.base_path / "chunk_mappings.pkl"
            if mapping_path.exists():
                with open(mapping_path, 'rb') as f:
                    self.id_to_chunk_mapping = pickle.load(f)
                logger.info(f"Loaded chunk mappings for {len(self.id_to_chunk_mapping)} chunks")
            
            # Initialize embedding model for search
            self._initialize_embedding_model()
            
            return len(self.indexes) > 0
            
        except Exception as e:
            logger.error(f"Error loading indexes: {e}")
            return False
    
    def similarity_search(self, query: str, top_k: int = 10, 
                         index_name: Optional[str] = None,
                         filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search using FAISS
        
        Args:
            query: Search query text
            top_k: Number of results to return
            index_name: Specific index to search (None for all)
            filters: Metadata filters to apply
        """
        
        if not self.indexes:
            logger.error("No indexes loaded. Please create or load indexes first.")
            return []
        
        # Generate query embedding
        enhanced_query = self._preprocess_text_for_embedding(query)
        query_embedding = self._generate_embeddings([enhanced_query])
        
        if query_embedding.size == 0:
            logger.error("Failed to generate query embedding")
            return []
        
        # Normalize for cosine similarity
        if self.faiss_config.metric == "COSINE":
            faiss.normalize_L2(query_embedding)
        
        results = []
        
        # Search specific index or all indexes
        indexes_to_search = [index_name] if index_name and index_name in self.indexes else list(self.indexes.keys())
        
        for idx_name in indexes_to_search:
            index = self.indexes[idx_name]
            metadata = self.chunk_metadata[idx_name]
            
            # Set search parameters for IVF indexes
            if hasattr(index, 'nprobe'):
                index.nprobe = self.faiss_config.nprobe
            
            # Perform search
            scores, indices = index.search(query_embedding, min(top_k * 2, index.ntotal))
            
            # Process results
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # Invalid index
                    continue
                
                if idx < len(metadata):
                    chunk_meta = metadata[idx]
                    
                    # Apply filters if provided
                    if filters and not self._apply_filters(chunk_meta, filters):
                        continue
                    
                    result = {
                        'score': float(score),
                        'chunk_id': chunk_meta.get('chunk_id', f"{idx_name}_{idx}"),
                        'content': chunk_meta.get('content', ''),
                        'index_name': idx_name,
                        'metadata': chunk_meta
                    }
                    
                    results.append(result)
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 10,
                     semantic_weight: float = 0.7,
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword-based search
        
        Args:
            query: Search query
            top_k: Number of results
            semantic_weight: Weight for semantic search (1-semantic_weight for keyword)
            filters: Metadata filters
        """
        
        # Get semantic search results
        semantic_results = self.similarity_search(query, top_k * 2, filters=filters)
        
        # Get keyword search results using TF-IDF
        keyword_results = self._keyword_search(query, top_k * 2, filters)
        
        # Combine and re-rank results
        combined_results = self._combine_search_results(
            semantic_results, keyword_results, semantic_weight
        )
        
        return combined_results[:top_k]
    
    def _keyword_search(self, query: str, top_k: int, 
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Perform keyword-based search using TF-IDF"""
        
        try:
            # Load TF-IDF matrix if not in memory
            matrix_path = self.base_path / "tfidf_matrix.pkl"
            if not hasattr(self, 'tfidf_matrix') and matrix_path.exists():
                with open(matrix_path, 'rb') as f:
                    self.tfidf_matrix = pickle.load(f)
            
            if not hasattr(self, 'tfidf_matrix'):
                logger.warning("TF-IDF matrix not available")
                return []
            
            # Transform query
            query_vec = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include non-zero similarities
                    # Find corresponding chunk metadata
                    chunk_meta = self._get_chunk_metadata_by_index(idx)
                    if chunk_meta and (not filters or self._apply_filters(chunk_meta, filters)):
                        results.append({
                            'score': float(similarities[idx]),
                            'chunk_id': chunk_meta.get('chunk_id', f"tfidf_{idx}"),
                            'content': chunk_meta.get('content', ''),
                            'index_name': 'tfidf',
                            'metadata': chunk_meta
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _get_chunk_metadata_by_index(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get chunk metadata by global index"""
        # This is a simplified version - you might need to implement more sophisticated mapping
        for index_name, metadata_list in self.chunk_metadata.items():
            if idx < len(metadata_list):
                return metadata_list[idx]
            idx -= len(metadata_list)
        return None
    
    def _combine_search_results(self, semantic_results: List[Dict], 
                               keyword_results: List[Dict],
                               semantic_weight: float) -> List[Dict[str, Any]]:
        """Combine and re-rank semantic and keyword search results"""
        
        # Normalize scores
        def normalize_scores(results):
            if not results:
                return results
            max_score = max(r['score'] for r in results)
            min_score = min(r['score'] for r in results)
            score_range = max_score - min_score
            
            if score_range == 0:
                return results
            
            for result in results:
                result['normalized_score'] = (result['score'] - min_score) / score_range
            return results
        
        semantic_results = normalize_scores(semantic_results)
        keyword_results = normalize_scores(keyword_results)
        
        # Combine results
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            chunk_id = result['chunk_id']
            combined[chunk_id] = result.copy()
            combined[chunk_id]['combined_score'] = semantic_weight * result.get('normalized_score', 0)
            combined[chunk_id]['semantic_score'] = result.get('normalized_score', 0)
            combined[chunk_id]['keyword_score'] = 0
        
        # Add keyword results
        keyword_weight = 1 - semantic_weight
        for result in keyword_results:
            chunk_id = result['chunk_id']
            if chunk_id in combined:
                combined[chunk_id]['combined_score'] += keyword_weight * result.get('normalized_score', 0)
                combined[chunk_id]['keyword_score'] = result.get('normalized_score', 0)
            else:
                combined[chunk_id] = result.copy()
                combined[chunk_id]['combined_score'] = keyword_weight * result.get('normalized_score', 0)
                combined[chunk_id]['semantic_score'] = 0
                combined[chunk_id]['keyword_score'] = result.get('normalized_score', 0)
        
        # Sort by combined score
        final_results = list(combined.values())
        final_results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_results
    
    def _apply_filters(self, chunk_metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply metadata filters to chunk"""
        for key, value in filters.items():
            chunk_value = chunk_metadata.get(key)
            
            if isinstance(value, list):
                if chunk_value not in value:
                    return False
            elif isinstance(value, dict):
                # Range filters
                if 'min' in value and chunk_value < value['min']:
                    return False
                if 'max' in value and chunk_value > value['max']:
                    return False
            else:
                if chunk_value != value:
                    return False
        
        return True
    
    def search_by_location(self, state: str = None, district: str = None, 
                          top_k: int = 20) -> List[Dict[str, Any]]:
        """Search chunks by administrative location"""
        filters = {}
        if state:
            filters['state'] = state
        if district:
            filters['district'] = district
        
        # Search all indexes with location filters
        results = []
        for index_name in self.indexes.keys():
            metadata_list = self.chunk_metadata[index_name]
            
            for i, chunk_meta in enumerate(metadata_list):
                if self._apply_filters(chunk_meta, filters):
                    result = {
                        'score': 1.0,  # Perfect match for location
                        'chunk_id': chunk_meta.get('chunk_id', f"{index_name}_{i}"),
                        'content': chunk_meta.get('content', ''),
                        'index_name': index_name,
                        'metadata': chunk_meta
                    }
                    results.append(result)
        
        return results[:top_k]
    
    def search_by_resource_category(self, category: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Search chunks by groundwater resource category"""
        filters = {'safety_category': category}
        
        results = []
        for index_name in self.indexes.keys():
            metadata_list = self.chunk_metadata[index_name]
            
            for i, chunk_meta in enumerate(metadata_list):
                if self._apply_filters(chunk_meta, filters):
                    result = {
                        'score': 1.0,
                        'chunk_id': chunk_meta.get('chunk_id', f"{index_name}_{i}"),
                        'content': chunk_meta.get('content', ''),
                        'index_name': index_name,
                        'metadata': chunk_meta
                    }
                    results.append(result)
        
        return results[:top_k]
    
    def get_chunk_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about loaded chunks and indexes"""
        stats = {
            'total_indexes': len(self.indexes),
            'total_chunks': 0,
            'index_details': {},
            'chunk_distribution': {},
            'quality_distribution': {},
            'location_coverage': {'states': set(), 'districts': set()}
        }
        
        for index_name, metadata_list in self.chunk_metadata.items():
            index_stats = {
                'chunk_count': len(metadata_list),
                'average_chunk_size': 0,
                'chunk_types': {},
                'quality_levels': {}
            }
            
            chunk_sizes = []
            for chunk_meta in metadata_list:
                # Chunk size stats
                size = chunk_meta.get('chunk_size', 0)
                if size > 0:
                    chunk_sizes.append(size)
                
                # Chunk type distribution
                chunk_type = chunk_meta.get('chunk_type', 'unknown')
                index_stats['chunk_types'][chunk_type] = index_stats['chunk_types'].get(chunk_type, 0) + 1
                
                # Quality distribution
                quality = chunk_meta.get('quality_level', chunk_meta.get('completeness_score', 'unknown'))
                index_stats['quality_levels'][str(quality)] = index_stats['quality_levels'].get(str(quality), 0) + 1
                
                # Location coverage
                state = chunk_meta.get('state')
                district = chunk_meta.get('district')
                if state:
                    stats['location_coverage']['states'].add(state)
                if district:
                    stats['location_coverage']['districts'].add(district)
            
            if chunk_sizes:
                index_stats['average_chunk_size'] = np.mean(chunk_sizes)
            
            stats['index_details'][index_name] = index_stats
            stats['total_chunks'] += len(metadata_list)
        
        # Convert sets to lists for JSON serialization
        stats['location_coverage']['states'] = list(stats['location_coverage']['states'])
        stats['location_coverage']['districts'] = list(stats['location_coverage']['districts'])
        
        return stats
    
    def save_chunk_mappings(self):
        """Save chunk ID to chunk mapping for reconstruction"""
        try:
            mapping_path = self.base_path / "chunk_mappings.pkl"
            with open(mapping_path, 'wb') as f:
                pickle.dump(self.id_to_chunk_mapping, f)
            logger.info(f"Saved chunk mappings for {len(self.id_to_chunk_mapping)} chunks")
        except Exception as e:
            logger.error(f"Error saving chunk mappings: {e}")
    
    def get_full_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve full chunk data by chunk ID"""
        mapping = self.id_to_chunk_mapping.get(chunk_id)
        if mapping:
            return mapping['original_chunk']
        return None
    
    def batch_process_json_files(self, json_directory: str, 
                                separate_indexes: bool = True) -> Dict[str, Any]:
        """
        Main pipeline: Process all JSON files in a directory
        
        Args:
            json_directory: Path to directory containing chunk JSON files
            separate_indexes: Whether to create separate indexes per chunk type
        """
        
        # Find all JSON files
        json_files = list(Path(json_directory).glob("*.json"))
        if not json_files:
            logger.error(f"No JSON files found in {json_directory}")
            return {}
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Load all chunks
        all_chunks = self.load_chunks_from_json([str(f) for f in json_files])
        
        if not any(chunks for chunks in all_chunks.values()):
            logger.error("No chunks loaded from JSON files")
            return {}
        
        # Create embeddings and indexes
        results = self.create_embeddings_and_indexes(all_chunks, separate_indexes)
        
        # Save chunk mappings
        self.save_chunk_mappings()
        
        # Generate statistics
        stats = self.get_chunk_statistics()
        results['statistics'] = stats
        
        logger.info("Batch processing completed successfully!")
        logger.info(f"Created {len(results['indexes_created'])} indexes with {results['total_embeddings']} total embeddings")
        
        return results


class INGRESSearchInterface:
    """
    High-level search interface for INGRES groundwater data
    """
    
    def __init__(self, embedding_pipeline: INGRESEmbeddingPipeline):
        self.pipeline = embedding_pipeline
    
    def search(self, query: str, 
               search_type: str = "hybrid",
               filters: Dict[str, Any] = None,
               top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Universal search interface
        
        Args:
            query: Natural language search query
            search_type: 'semantic', 'keyword', or 'hybrid'
            filters: Metadata filters
            top_k: Number of results
        """
        
        if search_type == "semantic":
            return self.pipeline.similarity_search(query, top_k, filters=filters)
        elif search_type == "keyword":
            return self.pipeline._keyword_search(query, top_k, filters)
        elif search_type == "hybrid":
            return self.pipeline.hybrid_search(query, top_k, filters=filters)
        else:
            raise ValueError(f"Unknown search type: {search_type}")
    
    def search_groundwater_issues(self, issue_type: str, 
                                 location: Dict[str, str] = None,
                                 top_k: int = 15) -> List[Dict[str, Any]]:
        """Search for specific groundwater issues"""
        
        issue_queries = {
            'over_exploitation': "over-exploited critical groundwater extraction sustainability",
            'quality_problems': "groundwater quality contamination pollution chemical parameters",
            'declining_levels': "water level decline falling groundwater table",
            'recharge_issues': "low recharge insufficient rainfall groundwater replenishment",
            'saline_intrusion': "saline water intrusion salinity contamination coastal"
        }
        
        query = issue_queries.get(issue_type, issue_type)
        
        filters = {}
        if location:
            filters.update(location)
        
        return self.search(query, search_type="hybrid", filters=filters, top_k=top_k)
    
    def compare_regions(self, regions: List[Dict[str, str]], 
                       comparison_aspect: str = "sustainability") -> Dict[str, List[Dict]]:
        """Compare groundwater status across multiple regions"""
        
        comparison_queries = {
            'sustainability': "sustainability ratio extraction recharge balance",
            'quality': "groundwater quality parameters contamination",
            'availability': "groundwater availability resources future allocation",
            'extraction': "groundwater extraction usage demand"
        }
        
        query = comparison_queries.get(comparison_aspect, comparison_aspect)
        
        results = {}
        for region in regions:
            region_name = f"{region.get('district', 'Unknown')}, {region.get('state', 'Unknown')}"
            region_results = self.search(query, filters=region, top_k=10)
            results[region_name] = region_results
        
        return results
    
    def get_recommendations(self, location: Dict[str, str] = None,
                          focus_area: str = "management") -> List[Dict[str, Any]]:
        """Get management recommendations based on groundwater status"""
        
        recommendation_queries = {
            'management': "groundwater management artificial recharge conservation",
            'policy': "groundwater policy regulation framework governance",
            'conservation': "water conservation efficiency demand management",
            'treatment': "groundwater treatment purification quality improvement"
        }
        
        query = recommendation_queries.get(focus_area, focus_area)
        
        filters = {}
        if location:
            filters.update(location)
        
        # Search for relevant chunks and extract actionable insights
        results = self.search(query, search_type="hybrid", filters=filters, top_k=20)
        
        # Post-process to generate recommendations
        recommendations = []
        for result in results:
            metadata = result.get('metadata', {})
            safety_category = metadata.get('safety_category', '')
            
            if safety_category in ['Over-Exploited', 'Critical']:
                recommendations.append({
                    'priority': 'HIGH',
                    'location': f"{metadata.get('district', '')}, {metadata.get('state', '')}",
                    'recommendation': 'Immediate intervention required - implement strict extraction limits and artificial recharge',
                    'supporting_data': result
                })
            elif safety_category == 'Semi-Critical':
                recommendations.append({
                    'priority': 'MEDIUM',
                    'location': f"{metadata.get('district', '')}, {metadata.get('state', '')}",
                    'recommendation': 'Preventive measures needed - enhance monitoring and promote conservation',
                    'supporting_data': result
                })
        
        return recommendations[:10]


# Usage Examples and Testing
def main():
    """Example usage of the INGRES FAISS pipeline"""
    
    # Initialize pipeline
    config = EmbeddingConfig(
        model_name="all-mpnet-base-v2",  # Good for technical content
        chunk_size_limit=6000
    )
    
    faiss_config = FAISSConfig(
        index_type="IVF",  # Good for your dataset size
        nlist=200,  # Adjusted for ~46,200 chunks
        nprobe=20
    )
    
    pipeline = INGRESEmbeddingPipeline(config, faiss_config)
    
    # Process all JSON files in current directory
    try:
        logger.info("Starting batch processing of JSON files...")
        results = pipeline.batch_process_json_files(".", separate_indexes=True)
        
        if results:
            print(f"\n✅ Processing completed successfully!")
            print(f"📊 Created {len(results['indexes_created'])} indexes")
            print(f"🔢 Total embeddings: {results['total_embeddings']:,}")
            
            # Print statistics
            stats = results.get('statistics', {})
            print(f"\n📈 Dataset Statistics:")
            print(f"   Total chunks: {stats.get('total_chunks', 0):,}")
            print(f"   States covered: {len(stats.get('location_coverage', {}).get('states', []))}")
            print(f"   Districts covered: {len(stats.get('location_coverage', {}).get('districts', []))}")
            
            # Initialize search interface
            search_interface = INGRESSearchInterface(pipeline)
            
            # Example searches
            print(f"\n🔍 Example Searches:")
            
            # 1. Semantic search for over-exploitation
            print("\n1. Searching for over-exploited areas:")
            overexploited = search_interface.search(
                "over-exploited critical groundwater areas high extraction", 
                top_k=5
            )
            for i, result in enumerate(overexploited[:3]):
                print(f"   {i+1}. Score: {result['score']:.3f} - {result['metadata'].get('state', 'Unknown')}, "
                      f"{result['metadata'].get('district', 'Unknown')}")
            
            # 2. Location-based search
            print("\n2. Searching by location (example):")
            if stats.get('location_coverage', {}).get('states'):
                example_state = list(stats['location_coverage']['states'])[0]
                location_results = pipeline.search_by_location(state=example_state, top_k=3)
                print(f"   Found {len(location_results)} results for {example_state}")
                for result in location_results[:2]:
                    print(f"   - {result['metadata'].get('district', 'Unknown')}: "
                          f"{result['metadata'].get('safety_category', 'Unknown')}")
            
            # 3. Resource category search
            print("\n3. Searching by resource category:")
            critical_areas = pipeline.search_by_resource_category("Critical", top_k=3)
            print(f"   Found {len(critical_areas)} critical areas")
            
            print(f"\n✅ All examples completed successfully!")
            print(f"🗂️ Indexes saved in: {pipeline.base_path}")
            
        else:
            print("❌ No results generated. Check your JSON files.")
            
    except Exception as e:
        logger.error(f"Error in main processing: {e}")
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
