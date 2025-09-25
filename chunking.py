import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentType(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    STATE_NARRATIVE = "state_narratives"
    DISTRICT_NARRATIVE = "district_narratives"
    METHODOLOGY = "methodology"
    CONCLUSIONS = "conclusions"
    STATE_SUMMARY_TABLE = "state_summary_tables"
    DISTRICT_COMPARISON_TABLE = "district_comparison_tables"
    UNIT_LEVEL_TABLE = "unit_level_tables"
    MAP = "maps"
    CHART = "charts"
    INFOGRAPHIC = "infographics"

class CategoryStatus(Enum):
    SAFE = "Safe"
    SEMI_CRITICAL = "Semi-Critical"
    CRITICAL = "Critical"
    OVER_EXPLOITED = "Over-Exploited"

@dataclass
class ChunkMetadata:
    chunk_id: str
    content_type: ContentType
    state: Optional[str] = None
    district: Optional[str] = None
    assessment_unit: Optional[str] = None
    year: Optional[str] = None
    page_number: Optional[int] = None
    geographic_scope: Optional[str] = None
    data_type: Optional[str] = None
    temporal_scope: Optional[str] = None
    table_id: Optional[str] = None
    image_id: Optional[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class TextChunk:
    chunk_id: str
    content: str
    metadata: ChunkMetadata
    token_count: int
    overlap_with_previous: Optional[str] = None
    overlap_with_next: Optional[str] = None

@dataclass
class TableChunk:
    chunk_id: str
    table_data: pd.DataFrame
    metadata: ChunkMetadata
    column_schema: Dict[str, str]
    semantic_tags: List[str]
    index_keys: Dict[str, Any]

@dataclass
class ImageChunk:
    chunk_id: str
    image_path: str
    metadata: ChunkMetadata
    extracted_text: str
    captions: List[str]
    associated_table_ids: List[str]

class GroundwaterDataChunker:
    def __init__(self, chunk_size: int = 700, overlap_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.state_patterns = self._load_state_patterns()
        self.district_patterns = self._load_district_patterns()
        
    def _load_state_patterns(self) -> List[str]:
        """Load Indian state and UT name patterns for entity extraction"""
        return [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
            "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
            "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
            "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
            "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi", "Lakshadweep", "Puducherry", "Jammu and Kashmir", "Ladakh"
        ]
    
    def _load_district_patterns(self) -> Dict[str, List[str]]:
        """Load district patterns by state (simplified for example)"""
        return {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
            "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
            # Add more state-district mappings as needed
        }
    
    def _generate_chunk_id(self, content_type: str, identifier: str = None) -> str:
        """Generate unique chunk ID"""
        base_string = f"{content_type}_{identifier}_{datetime.now().isoformat()}"
        return hashlib.md5(base_string.encode()).hexdigest()[:16]
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract geographic and temporal entities from text"""
        entities = {
            'states': [],
            'districts': [],
            'years': [],
            'categories': [],
            'trends': []
        }
        
        # Extract states
        for state in self.state_patterns:
            if state.lower() in text.lower():
                entities['states'].append(state)
        
        # Extract districts
        for state, districts in self.district_patterns.items():
            if state in entities['states']:
                for district in districts:
                    if district.lower() in text.lower():
                        entities['districts'].append(district)
        
        # Extract years
        year_pattern = r'\b(2023|2024)\b'
        entities['years'] = re.findall(year_pattern, text)
        
        # Extract categories
        for category in CategoryStatus:
            if category.value.lower() in text.lower():
                entities['categories'].append(category.value)
        
        # Extract trend indicators
        trend_patterns = [
            'improved', 'deteriorated', 'unchanged', 'no change',
            'increased', 'decreased', 'stable', 'declining'
        ]
        for pattern in trend_patterns:
            if pattern in text.lower():
                entities['trends'].append(pattern)
        
        return entities
    
    def _classify_content_type(self, text: str, context: Dict = None) -> ContentType:
        """Classify content type based on text content and context"""
        text_lower = text.lower()
        
        # Classification logic
        if any(word in text_lower for word in ['executive summary', 'overview', 'introduction']):
            return ContentType.EXECUTIVE_SUMMARY
        elif any(word in text_lower for word in ['methodology', 'assessment procedure', 'criteria']):
            return ContentType.METHODOLOGY
        elif any(word in text_lower for word in ['conclusion', 'recommendation', 'summary']):
            return ContentType.CONCLUSIONS
        elif context and 'is_state_level' in context and context['is_state_level']:
            return ContentType.STATE_NARRATIVE
        elif context and 'is_district_level' in context and context['is_district_level']:
            return ContentType.DISTRICT_NARRATIVE
        else:
            return ContentType.STATE_NARRATIVE  # Default
    
    def chunk_text_content(self, text: str, page_number: int = None) -> List[TextChunk]:
        """Chunk narrative text content with overlap"""
        chunks = []
        
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = ""
        current_tokens = 0
        chunk_sentences = []
        
        for sentence in sentences:
            sentence_tokens = len(sentence.split())
            
            if current_tokens + sentence_tokens <= self.chunk_size:
                current_chunk += sentence + " "
                current_tokens += sentence_tokens
                chunk_sentences.append(sentence)
            else:
                # Create chunk
                if current_chunk.strip():
                    chunk = self._create_text_chunk(
                        current_chunk.strip(), 
                        chunk_sentences, 
                        page_number
                    )
                    chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = chunk_sentences[-self._calculate_overlap_sentences(chunk_sentences):]
                overlap_text = " ".join(overlap_sentences)
                overlap_tokens = len(overlap_text.split())
                
                current_chunk = overlap_text + " " + sentence + " "
                current_tokens = overlap_tokens + sentence_tokens
                chunk_sentences = overlap_sentences + [sentence]
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_text_chunk(
                current_chunk.strip(), 
                chunk_sentences, 
                page_number
            )
            chunks.append(chunk)
        
        # Add overlap references
        for i in range(len(chunks)):
            if i > 0:
                chunks[i].overlap_with_previous = chunks[i-1].chunk_id
            if i < len(chunks) - 1:
                chunks[i].overlap_with_next = chunks[i+1].chunk_id
        
        return chunks
    
    def _calculate_overlap_sentences(self, sentences: List[str]) -> int:
        """Calculate number of sentences for overlap"""
        total_tokens = sum(len(s.split()) for s in sentences)
        overlap_ratio = self.overlap_size / total_tokens if total_tokens > 0 else 0
        return max(1, int(len(sentences) * overlap_ratio))
    
    def _create_text_chunk(self, content: str, sentences: List[str], page_number: int = None) -> TextChunk:
        """Create a text chunk with metadata"""
        entities = self._extract_entities(content)
        content_type = self._classify_content_type(content)
        
        chunk_id = self._generate_chunk_id(content_type.value, str(page_number))
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            content_type=content_type,
            state=entities['states'][0] if entities['states'] else None,
            district=entities['districts'][0] if entities['districts'] else None,
            year=entities['years'][0] if entities['years'] else None,
            page_number=page_number
        )
        
        return TextChunk(
            chunk_id=chunk_id,
            content=content,
            metadata=metadata,
            token_count=len(content.split())
        )
    
    def chunk_table_data(self, table_data: pd.DataFrame, table_info: Dict) -> TableChunk:
        """Process and chunk table data"""
        table_type = self._classify_table_type(table_data, table_info)
        semantic_tags = self._generate_semantic_tags(table_data)
        index_keys = self._extract_index_keys(table_data, table_type)
        
        chunk_id = self._generate_chunk_id(
            table_type.value, 
            table_info.get('table_id', 'unknown')
        )
        
        # Extract geographic entities from table
        geographic_info = self._extract_geographic_from_table(table_data)
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            content_type=table_type,
            state=geographic_info.get('state'),
            district=geographic_info.get('district'),
            page_number=table_info.get('page_number'),
            table_id=table_info.get('table_id')
        )
        
        # Generate column schema
        column_schema = {col: str(table_data[col].dtype) for col in table_data.columns}
        
        return TableChunk(
            chunk_id=chunk_id,
            table_data=table_data,
            metadata=metadata,
            column_schema=column_schema,
            semantic_tags=semantic_tags,
            index_keys=index_keys
        )
    
    def _classify_table_type(self, df: pd.DataFrame, table_info: Dict) -> ContentType:
        """Classify table type based on columns and content"""
        columns = [col.lower() for col in df.columns]
        
        # State summary table indicators
        if any(term in ' '.join(columns) for term in ['state', 'total number', 'improved', 'deteriorated']):
            return ContentType.STATE_SUMMARY_TABLE
        
        # District comparison table indicators
        elif any(term in ' '.join(columns) for term in ['district', 'extraction', 'categorization', '2023', '2024']):
            return ContentType.DISTRICT_COMPARISON_TABLE
        
        # Unit level table indicators
        else:
            return ContentType.UNIT_LEVEL_TABLE
    
    def _generate_semantic_tags(self, df: pd.DataFrame) -> List[str]:
        """Generate semantic tags based on table content"""
        tags = []
        
        # Check for improvement trends
        if any('improv' in str(col).lower() for col in df.columns):
            tags.append('improvement_trend')
        
        # Check for deterioration trends
        if any('deterior' in str(col).lower() for col in df.columns):
            tags.append('deterioration_trend')
        
        # Check for status changes
        if any('2023' in str(col) and '2024' in str(col) for col in df.columns):
            tags.append('status_change')
        
        # Check for extraction levels
        if any('extraction' in str(col).lower() for col in df.columns):
            tags.append('extraction_level')
        
        return tags
    
    def _extract_index_keys(self, df: pd.DataFrame, table_type: ContentType) -> Dict[str, Any]:
        """Extract index keys based on table type"""
        index_keys = {}
        
        if table_type == ContentType.STATE_SUMMARY_TABLE:
            if 'Name of State/UT' in df.columns:
                index_keys['states'] = df['Name of State/UT'].tolist()
            if 'Total Number of Assessed Units' in df.columns:
                index_keys['total_units'] = df['Total Number of Assessed Units'].sum()
        
        elif table_type == ContentType.DISTRICT_COMPARISON_TABLE:
            if 'District' in df.columns:
                index_keys['districts'] = df['District'].unique().tolist()
            if 'Assessment Unit' in df.columns:
                index_keys['assessment_units'] = df['Assessment Unit'].unique().tolist()
        
        return index_keys
    
    def _extract_geographic_from_table(self, df: pd.DataFrame) -> Dict[str, str]:
        """Extract geographic information from table data"""
        geographic_info = {}
        
        # Check for state information
        for col in df.columns:
            if 'state' in col.lower():
                states = df[col].dropna().unique()
                if len(states) == 1:
                    geographic_info['state'] = states[0]
                break
        
        # Check for district information
        for col in df.columns:
            if 'district' in col.lower():
                districts = df[col].dropna().unique()
                if len(districts) == 1:
                    geographic_info['district'] = districts[0]
                break
        
        return geographic_info
    
    def chunk_image_data(self, image_info: Dict) -> ImageChunk:
        """Process and chunk image data"""
        image_type = self._classify_image_type(image_info)
        
        chunk_id = self._generate_chunk_id(
            image_type.value, 
            image_info.get('image_id', 'unknown')
        )
        
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            content_type=image_type,
            page_number=image_info.get('page_number'),
            image_id=image_info.get('image_id'),
            geographic_scope=image_info.get('geographic_scope'),
            data_type=image_info.get('data_type'),
            temporal_scope=image_info.get('temporal_scope')
        )
        
        return ImageChunk(
            chunk_id=chunk_id,
            image_path=image_info.get('image_path', ''),
            metadata=metadata,
            extracted_text=image_info.get('extracted_text', ''),
            captions=image_info.get('captions', []),
            associated_table_ids=image_info.get('associated_table_ids', [])
        )
    
    def _classify_image_type(self, image_info: Dict) -> ContentType:
        """Classify image type based on metadata"""
        data_type = image_info.get('data_type', '').lower()
        
        if 'map' in data_type or 'geographical' in data_type:
            return ContentType.MAP
        elif 'chart' in data_type or 'graph' in data_type:
            return ContentType.CHART
        else:
            return ContentType.INFOGRAPHIC
    
    def process_document(self, text_content: str, tables: List[Dict], images: List[Dict]) -> Dict[str, List]:
        """Process entire document and return all chunks"""
        logger.info("Starting document processing...")
        
        results = {
            'text_chunks': [],
            'table_chunks': [],
            'image_chunks': []
        }
        
        # Process text content
        logger.info("Processing text content...")
        text_chunks = self.chunk_text_content(text_content)
        results['text_chunks'] = text_chunks
        
        # Process tables
        logger.info(f"Processing {len(tables)} tables...")
        for table_info in tables:
            if 'data' in table_info:
                table_chunk = self.chunk_table_data(table_info['data'], table_info)
                results['table_chunks'].append(table_chunk)
        
        # Process images
        logger.info(f"Processing {len(images)} images...")
        for image_info in images:
            image_chunk = self.chunk_image_data(image_info)
            results['image_chunks'].append(image_chunk)
        
        logger.info(f"Processing complete: {len(results['text_chunks'])} text chunks, "
                   f"{len(results['table_chunks'])} table chunks, "
                   f"{len(results['image_chunks'])} image chunks")
        
        return results
    
    def export_chunks_to_json(self, chunks: Dict[str, List], output_path: str):
        """Export chunks to JSON format for vector database ingestion"""
        export_data = {
            'text_chunks': [asdict(chunk) for chunk in chunks['text_chunks']],
            'table_chunks': [],
            'image_chunks': [asdict(chunk) for chunk in chunks['image_chunks']]
        }
        
        # Handle table chunks separately due to DataFrame serialization
        for chunk in chunks['table_chunks']:
            chunk_dict = asdict(chunk)
            chunk_dict['table_data'] = chunk.table_data.to_dict('records')
            export_data['table_chunks'].append(chunk_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Chunks exported to {output_path}")

# Example usage
def example_usage():
    """Example of how to use the chunking pipeline"""
    
    # Initialize chunker
    chunker = GroundwaterDataChunker(chunk_size=600, overlap_size=100)

    # --- Replace this section with actual PDF extraction ---
    # Set the input PDF file
    input_pdf = "Groundwater-data_extracted.pdf"

    # --- Actual extraction using pdfplumber ---
    import pdfplumber
    import os

    text_content = ""
    tables = []
    images = []

    if os.path.exists(input_pdf):
        with pdfplumber.open(input_pdf) as pdf:
            # Extract all text
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""
                text_content += page_text + "\n"

                # Extract tables
                page_tables = page.extract_tables()
                for idx, table in enumerate(page_tables):
                    # Clean header: replace None with default column names and ensure all are strings
                    header = table[0]
                    clean_header = []
                    for i, col in enumerate(header):
                        if col is None or str(col).strip() == '':
                            clean_header.append(f"Column{i+1}")
                        else:
                            clean_header.append(str(col))
                    df = pd.DataFrame(table[1:], columns=clean_header)
                    tables.append({
                        'data': df,
                        'table_id': f"table_{page_num}_{idx+1}",
                        'page_number': page_num
                    })

                # Extract images (save as files and reference path)
                for img_idx, img in enumerate(page.images):
                    # Extract image bbox and crop
                    bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
                    cropped = page.crop(bbox).to_image(resolution=300)
                    img_path = f"extracted_image_{page_num}_{img_idx+1}.png"
                    cropped.save(img_path, format="PNG")
                    images.append({
                        'image_id': f"img_{page_num}_{img_idx+1}",
                        'image_path': img_path,
                        'page_number': page_num,
                        'data_type': 'image',
                        'captions': [],
                        'extracted_text': '',
                        'geographic_scope': None,
                        'temporal_scope': None
                    })
    else:
        logger.error(f"Input PDF {input_pdf} not found.")

    # Process document
    chunks = chunker.process_document(
        text_content=text_content,
        tables=tables,
        images=images
    )

    # Export to JSON
    chunker.export_chunks_to_json(chunks, 'groundwater_chunks.json')

    return chunks

if __name__ == "__main__":
    example_usage()