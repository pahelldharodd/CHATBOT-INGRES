import re
import json
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import os
from argparse import ArgumentParser

# Optional dependency handling for pdf extraction
try:
    import pdfplumber  # type: ignore
except ImportError:  # pragma: no cover - graceful degradation if not installed
    pdfplumber = None

class ChunkType(Enum):
    METHODOLOGY = "methodology"
    FORMULA = "formula"
    TEMPLATE = "template"
    WORKFLOW = "workflow"
    USER_ROLE = "user_role"
    TECHNICAL_SPEC = "technical_spec"
    VISUAL = "visual"
    GLOSSARY = "glossary"
    REPORT = "report"

class ComponentType(Enum):
    RECHARGE = "recharge"
    ENVIRONMENTAL_FLOW = "environmental_flow"
    EXTRACTION = "extraction"
    DASHBOARD = "dashboard"
    VALIDATION = "validation"

@dataclass
class ChunkMetadata:
    section_number: str = ""
    hierarchy_level: int = 0
    figure_references: List[str] = field(default_factory=list)
    template_references: List[str] = field(default_factory=list)
    formula_references: List[str] = field(default_factory=list)
    user_roles: List[str] = field(default_factory=list)
    data_relationships: List[str] = field(default_factory=list)
    cross_references: List[str] = field(default_factory=list)
    component_type: Optional[ComponentType] = None
    assessment_categories: List[str] = field(default_factory=list)
    aquifer_types: List[str] = field(default_factory=list)

@dataclass
class DocumentChunk:
    chunk_id: str
    chunk_type: ChunkType
    title: str
    content: str
    metadata: ChunkMetadata
    dependencies: List[str] = field(default_factory=list)
    related_chunks: List[str] = field(default_factory=list)
    size_bytes: int = 0

class GEC2015DocumentChunker:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.chunk_id_counter = 0
        self.logger = logging.getLogger(__name__)
        
        # Pattern definitions for identification
        self.patterns = {
            'section_numbers': r'^\d+(\.\d+)*\.?\s',
            'figures': r'Figure\s+(\d+)',
            'templates': r'Template\s+(\d+)|Excel\s+Template\s*(\d*)',
            'formulas': r'Formula\s+(\d+)|Equation\s+(\d+)',
            'user_roles': r'(Field User|District Admin|State Admin|SLC Admin|CGWB Admin|CLEG Admin|Ministry Admin)',
            'assessment_units': r'(SAFE|SEMI-CRITICAL|CRITICAL|OVER-EXPLOITED)',
            'aquifer_types': r'(Unconfined|Semi-confined|Confined)\s+aquifer',
            'recharge_types': r'(Annual Rainfall Recharge|Ground Water Irrigation|Surface Water Irrigation|Canal Seepage|Tanks and Ponds|Water Conservation Structures|Stream Channels|Pipelines)',
            'environmental_flows': r'(Vertical Inter Aquifer Flow|Lateral Flow|Transpiration|Evaporation|Evapotranspiration|Baseflow|Environmental Flows)',
            'extraction_categories': r'(Domestic Use|Irrigation Use|Industrial Use)',
            'technical_units': r'(BCM|Ha\.m|Lpcd|m³|mm|%)'
        }
        
        # Recharge source configurations
        self.recharge_sources = {
            'Annual Rainfall Recharge': ['Water Level Fluctuation', 'Rainfall Infiltration Factor'],
            'Ground Water Irrigation': ['Unit Draft', 'Consumptive Use'],
            'Surface Water Irrigation': ['Seepage Rate', 'Command Area'],
            'Canal Seepage': ['Seepage Factor', 'Canal Length'],
            'Tanks and Ponds': ['Surface Area', 'Seepage Rate'],
            'Water Conservation Structures': ['Recharge Rate', 'Structure Type'],
            'Stream Channels': ['Base Flow', 'Channel Properties'],
            'Pipelines': ['Leakage Rate', 'Network Length']
        }

    def generate_chunk_id(self, prefix: str = "GEC") -> str:
        self.chunk_id_counter += 1
        return f"{prefix}_{self.chunk_id_counter:04d}"

    def extract_section_hierarchy(self, text: str) -> Tuple[str, int]:
        """Extract section number and hierarchy level from text."""
        match = re.match(self.patterns['section_numbers'], text.strip())
        if match:
            section_num = match.group(0).strip()
            level = section_num.count('.')
            return section_num, level
        return "", 0

    def extract_references(self, text: str) -> Dict[str, List[str]]:
        """Extract all types of references from text."""
        references = {
            'figures': [],
            'templates': [],
            'formulas': [],
            'user_roles': [],
            'cross_refs': []
        }
        
        # Figure references
        references['figures'] = re.findall(self.patterns['figures'], text, re.IGNORECASE)
        
        # Template references
        template_matches = re.findall(self.patterns['templates'], text, re.IGNORECASE)
        references['templates'] = [m for group in template_matches for m in group if m]
        
        # Formula references
        formula_matches = re.findall(self.patterns['formulas'], text, re.IGNORECASE)
        references['formulas'] = [m for group in formula_matches for m in group if m]
        
        # User role references
        references['user_roles'] = re.findall(self.patterns['user_roles'], text, re.IGNORECASE)
        
        return references

    def identify_component_type(self, text: str) -> Optional[ComponentType]:
        """Identify the component type based on content."""
        text_lower = text.lower()
        
        if any(recharge in text_lower for recharge in self.recharge_sources.keys()):
            return ComponentType.RECHARGE
        elif any(env_flow.lower() in text_lower for env_flow in ['vertical inter aquifer', 'lateral flow', 'transpiration', 'evaporation', 'baseflow']):
            return ComponentType.ENVIRONMENTAL_FLOW
        elif any(extraction.lower() in text_lower for extraction in ['domestic use', 'irrigation use', 'industrial use']):
            return ComponentType.EXTRACTION
        elif any(dashboard in text_lower for dashboard in ['gis dashboard', 'mis dashboard', 'live ground water dashboard']):
            return ComponentType.DASHBOARD
        elif 'validation' in text_lower or 'quality tagging' in text_lower:
            return ComponentType.VALIDATION
        
        return None

    def chunk_methodology_content(self, text: str, section_title: str) -> List[DocumentChunk]:
        """Chunk core methodology content keeping principles and formulas together."""
        chunks = []
        
        # Split by major methodology sections
        methodology_sections = re.split(r'\n(?=\d+\.\d+\.?\d*\s+[A-Z])', text)
        
        for section in methodology_sections:
            if not section.strip():
                continue
                
            section_num, hierarchy = self.extract_section_hierarchy(section)
            references = self.extract_references(section)
            
            # Extract formulas with their variable definitions
            formula_blocks = self.extract_formula_blocks(section)
            
            metadata = ChunkMetadata(
                section_number=section_num,
                hierarchy_level=hierarchy,
                figure_references=references['figures'],
                template_references=references['templates'],
                formula_references=references['formulas'],
                assessment_categories=re.findall(self.patterns['assessment_units'], section),
                aquifer_types=re.findall(self.patterns['aquifer_types'], section, re.IGNORECASE)
            )
            
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id("METH"),
                chunk_type=ChunkType.METHODOLOGY,
                title=f"Methodology: {section_title}",
                content=section.strip(),
                metadata=metadata,
                size_bytes=len(section.encode('utf-8'))
            )
            
            chunks.append(chunk)
            
            # Create separate formula chunks if formulas are extensive
            if len(formula_blocks) > 3:
                for i, formula_block in enumerate(formula_blocks):
                    formula_chunk = self.create_formula_chunk(formula_block, f"{section_title}_Formula_{i+1}")
                    chunks.append(formula_chunk)
                    chunk.related_chunks.append(formula_chunk.chunk_id)
        
        return chunks

    def extract_formula_blocks(self, text: str) -> List[str]:
        """Extract complete formula blocks with variable definitions."""
        formula_blocks = []
        
        # Pattern to match formula blocks with variables
        formula_pattern = r'((?:Formula|Equation)\s+\d+[:\-]?\s*.*?)(?=(?:Formula|Equation)\s+\d+|$|\n\n[A-Z])'
        matches = re.findall(formula_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            # Include variable definitions that follow
            var_pattern = r'(Where[:\s]*.*?)(?=\n\n|\n[A-Z][^a-z]|$)'
            var_match = re.search(var_pattern, match, re.DOTALL | re.IGNORECASE)
            
            if var_match:
                complete_formula = match + var_match.group(1)
            else:
                complete_formula = match
                
            formula_blocks.append(complete_formula.strip())
        
        return formula_blocks

    def create_formula_chunk(self, formula_text: str, title: str) -> DocumentChunk:
        """Create a dedicated formula chunk."""
        references = self.extract_references(formula_text)
        
        metadata = ChunkMetadata(
            formula_references=references['formulas'],
            figure_references=references['figures']
        )
        
        return DocumentChunk(
            chunk_id=self.generate_chunk_id("FORM"),
            chunk_type=ChunkType.FORMULA,
            title=f"Formula: {title}",
            content=formula_text,
            metadata=metadata,
            size_bytes=len(formula_text.encode('utf-8'))
        )

    def chunk_recharge_components(self, text: str) -> List[DocumentChunk]:
        """Chunk recharge sources keeping calculation methods together."""
        chunks = []
        
        for recharge_type, methods in self.recharge_sources.items():
            # Find sections related to this recharge type
            pattern = rf'({recharge_type}.*?)(?=(?:{"||".join(self.recharge_sources.keys())})|$)'
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if not match.strip():
                    continue
                    
                references = self.extract_references(match)
                
                metadata = ChunkMetadata(
                    component_type=ComponentType.RECHARGE,
                    template_references=references['templates'],
                    formula_references=references['formulas'],
                    data_relationships=[f"recharge_method_{method.lower().replace(' ', '_')}" for method in methods]
                )
                
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id("RECH"),
                    chunk_type=ChunkType.METHODOLOGY,
                    title=f"Recharge Component: {recharge_type}",
                    content=match.strip(),
                    metadata=metadata,
                    size_bytes=len(match.encode('utf-8'))
                )
                
                chunks.append(chunk)
        
        return chunks

    def chunk_template_systems(self, text: str) -> List[DocumentChunk]:
        """Chunk Excel templates and form systems by functional groups."""
        chunks = []
        
        template_sections = {
            'Excel Templates': r'(Excel\s+Template.*?)(?=Form\s+Input|$)',
            'Form Input Systems': r'(Form\s+Input\s+Systems.*?)(?=Shape\s+File|Excel\s+Template|$)',
            'Shape File Requirements': r'(Shape\s+File\s+Requirements.*?)(?=Excel\s+Template|Form\s+Input|$)'
        }
        
        for section_name, pattern in template_sections.items():
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if not match.strip():
                    continue
                    
                references = self.extract_references(match)
                component_type = self.identify_component_type(match)
                
                metadata = ChunkMetadata(
                    template_references=references['templates'],
                    figure_references=references['figures'],
                    component_type=component_type,
                    data_relationships=self.extract_data_relationships(match)
                )
                
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id("TMPL"),
                    chunk_type=ChunkType.TEMPLATE,
                    title=f"Template System: {section_name}",
                    content=match.strip(),
                    metadata=metadata,
                    size_bytes=len(match.encode('utf-8'))
                )
                
                chunks.append(chunk)
        
        return chunks

    def extract_data_relationships(self, text: str) -> List[str]:
        """Extract data relationships from template descriptions."""
        relationships = []
        
        # Common relationship patterns
        relationship_patterns = [
            r'feeds\s+into\s+([^.]+)',
            r'calculated\s+from\s+([^.]+)',
            r'depends\s+on\s+([^.]+)',
            r'input\s+for\s+([^.]+)'
        ]
        
        for pattern in relationship_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            relationships.extend(matches)
        
        return [rel.strip() for rel in relationships]

    def chunk_user_workflows(self, text: str) -> List[DocumentChunk]:
        """Chunk user management and approval workflows by user level."""
        chunks = []
        
        user_roles = [
            'Field User', 'District Admin', 'State Admin', 'SLC Admin', 
            'CGWB Admin', 'CLEG Admin', 'Ministry Admin'
        ]
        
        # Extract workflow sections
        workflow_pattern = r'((?:User\s+Journey|Approval\s+Workflow|User\s+Management).*?)(?=\n\n[A-Z]|\n\d+\.|$)'
        workflow_matches = re.findall(workflow_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for workflow_text in workflow_matches:
            if not workflow_text.strip():
                continue
                
            references = self.extract_references(workflow_text)
            involved_roles = [role for role in user_roles if role.lower() in workflow_text.lower()]
            
            metadata = ChunkMetadata(
                user_roles=involved_roles,
                figure_references=references['figures'],
                cross_references=references['cross_refs']
            )
            
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id("WORK"),
                chunk_type=ChunkType.WORKFLOW,
                title="User Workflow and Approval Process",
                content=workflow_text.strip(),
                metadata=metadata,
                size_bytes=len(workflow_text.encode('utf-8'))
            )
            
            chunks.append(chunk)
        
        return chunks

    def chunk_technical_specifications(self, text: str) -> List[DocumentChunk]:
        """Chunk technical specifications keeping data elements and units together."""
        chunks = []
        
        # Identify technical specification sections
        spec_patterns = {
            'Data Elements': r'(Data\s+Elements.*?)(?=Validation\s+Methods|Quality\s+Tagging|$)',
            'Validation Methods': r'(Validation\s+Methods.*?)(?=Quality\s+Tagging|Data\s+Elements|$)',
            'Quality Tagging': r'(Quality\s+Tagging.*?)(?=Data\s+Elements|Validation\s+Methods|$)'
        }
        
        for spec_type, pattern in spec_patterns.items():
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            
            for match in matches:
                if not match.strip():
                    continue
                    
                references = self.extract_references(match)
                
                # Extract technical units and parameters
                tech_units = re.findall(self.patterns['technical_units'], match)
                
                metadata = ChunkMetadata(
                    data_relationships=self.extract_data_relationships(match),
                    component_type=ComponentType.VALIDATION if 'validation' in spec_type.lower() else None
                )
                
                chunk = DocumentChunk(
                    chunk_id=self.generate_chunk_id("SPEC"),
                    chunk_type=ChunkType.TECHNICAL_SPEC,
                    title=f"Technical Specification: {spec_type}",
                    content=match.strip(),
                    metadata=metadata,
                    size_bytes=len(match.encode('utf-8'))
                )
                
                chunks.append(chunk)
        
        return chunks

    def chunk_visual_content(self, text: str) -> List[DocumentChunk]:
        """Chunk visual content grouping related figures and mockups."""
        chunks = []
        
        # Extract figure references and their contexts
        figure_pattern = r'(Figure\s+\d+[:\-]?[^.]*\..*?)(?=Figure\s+\d+|$)'
        figure_matches = re.findall(figure_pattern, text, re.DOTALL | re.IGNORECASE)
        
        current_visual_group = []
        group_size = 0
        max_group_size = 5  # Group up to 5 related figures
        
        for i, figure_text in enumerate(figure_matches):
            current_visual_group.append(figure_text)
            group_size += len(figure_text)
            
            # Create chunk when group is full or at end
            if len(current_visual_group) >= max_group_size or i == len(figure_matches) - 1:
                if current_visual_group:
                    combined_content = '\n\n'.join(current_visual_group)
                    references = self.extract_references(combined_content)
                    
                    metadata = ChunkMetadata(
                        figure_references=references['figures'],
                        template_references=references['templates']
                    )
                    
                    chunk = DocumentChunk(
                        chunk_id=self.generate_chunk_id("VIS"),
                        chunk_type=ChunkType.VISUAL,
                        title=f"Visual Content Group {len(chunks)+1}",
                        content=combined_content,
                        metadata=metadata,
                        size_bytes=len(combined_content.encode('utf-8'))
                    )
                    
                    chunks.append(chunk)
                    current_visual_group = []
                    group_size = 0
        
        return chunks

    def create_glossary_chunk(self, text: str) -> DocumentChunk:
        """Create a comprehensive glossary chunk."""
        # Extract technical terms and definitions
        term_pattern = r'([A-Z][A-Z\s]+)[\-\:]?\s*([^.\n]+\.)'
        terms = re.findall(term_pattern, text)
        
        # Extract unit definitions
        unit_pattern = r'(BCM|Ha\.m|Lpcd|m³|mm|%)[\-\:]?\s*([^.\n]+\.?)'
        units = re.findall(unit_pattern, text, re.IGNORECASE)
        
        glossary_content = "TECHNICAL TERMS AND DEFINITIONS\n" + "="*40 + "\n\n"
        
        for term, definition in terms:
            glossary_content += f"**{term.strip()}**: {definition.strip()}\n\n"
        
        glossary_content += "\nUNIT DEFINITIONS\n" + "="*20 + "\n\n"
        
        for unit, definition in units:
            glossary_content += f"**{unit}**: {definition.strip()}\n\n"
        
        metadata = ChunkMetadata()
        
        return DocumentChunk(
            chunk_id=self.generate_chunk_id("GLOS"),
            chunk_type=ChunkType.GLOSSARY,
            title="Glossary and Reference Material",
            content=glossary_content,
            metadata=metadata,
            size_bytes=len(glossary_content.encode('utf-8'))
        )

    def establish_chunk_relationships(self):
        """Establish relationships between chunks based on references and dependencies."""
        for chunk in self.chunks:
            # Find related chunks based on template references
            for template_ref in chunk.metadata.template_references:
                related_chunks = [c.chunk_id for c in self.chunks 
                                if template_ref in c.metadata.template_references 
                                and c.chunk_id != chunk.chunk_id]
                chunk.related_chunks.extend(related_chunks)
            
            # Find dependencies based on formula references
            for formula_ref in chunk.metadata.formula_references:
                dependent_chunks = [c.chunk_id for c in self.chunks 
                                  if c.chunk_type == ChunkType.FORMULA 
                                  and formula_ref in c.content]
                chunk.dependencies.extend(dependent_chunks)
            
            # Remove duplicates
            chunk.related_chunks = list(set(chunk.related_chunks))
            chunk.dependencies = list(set(chunk.dependencies))

    def process_document(self, document_text: str) -> List[DocumentChunk]:
        """Main processing function to chunk the entire document."""
        self.logger.info("Starting document processing...")
        
        # Split document into major sections
        sections = self.split_into_major_sections(document_text)
        
        for section_name, section_text in sections.items():
            self.logger.info(f"Processing section: {section_name}")
            
            if "methodology" in section_name.lower():
                chunks = self.chunk_methodology_content(section_text, section_name)
            elif "recharge" in section_name.lower():
                chunks = self.chunk_recharge_components(section_text)
            elif "template" in section_name.lower() or "form" in section_name.lower():
                chunks = self.chunk_template_systems(section_text)
            elif "user" in section_name.lower() or "workflow" in section_name.lower():
                chunks = self.chunk_user_workflows(section_text)
            elif "specification" in section_name.lower() or "validation" in section_name.lower():
                chunks = self.chunk_technical_specifications(section_text)
            elif "figure" in section_name.lower() or "visual" in section_name.lower():
                chunks = self.chunk_visual_content(section_text)
            else:
                # Default chunking for unclassified sections
                chunks = self.default_chunk_section(section_text, section_name)
            
            self.chunks.extend(chunks)
        
        # Create glossary chunk
        glossary_chunk = self.create_glossary_chunk(document_text)
        self.chunks.append(glossary_chunk)
        
        # Establish relationships
        self.establish_chunk_relationships()
        
        self.logger.info(f"Document processing completed. Created {len(self.chunks)} chunks.")
        return self.chunks

    def split_into_major_sections(self, text: str) -> Dict[str, str]:
        """Split document into major sections based on content structure."""
        sections = {}
        
        # Define major section patterns
        section_patterns = {
            'Core Methodology': r'(GEC-2015\s+methodology.*?)(?=Ground\s+Water\s+Components|$)',
            'Recharge Components': r'(Ground\s+Water\s+Components.*?Recharge\s+Sources.*?)(?=Environmental\s+Flows|$)',
            'Environmental Flows': r'(Environmental\s+Flows.*?)(?=Extraction\s+Categories|$)',
            'Extraction Categories': r'(Extraction\s+Categories.*?)(?=Data\s+Input\s+Systems|$)',
            'Data Input Systems': r'(Data\s+Input\s+Systems.*?)(?=User\s+Interface|$)',
            'User Interface': r'(User\s+Interface.*?)(?=User\s+Management|$)',
            'User Management': r'(User\s+Management.*?)(?=Reporting\s+System|$)',
            'Reporting System': r'(Reporting\s+System.*?)(?=Technical\s+Specifications|$)',
            'Technical Specifications': r'(Technical\s+Specifications.*?)(?=Visual\s+Content|$)',
            'Visual Content': r'(Visual\s+Content.*?)(?=$)'
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            if matches:
                sections[section_name] = matches[0]
        
        return sections

    def default_chunk_section(self, text: str, section_name: str) -> List[DocumentChunk]:
        """Default chunking strategy for unclassified sections."""
        chunks = []
        
        # Split by subsections
        subsections = re.split(r'\n(?=\d+\.\d+)', text)
        
        for subsection in subsections:
            if not subsection.strip():
                continue
                
            section_num, hierarchy = self.extract_section_hierarchy(subsection)
            references = self.extract_references(subsection)
            
            metadata = ChunkMetadata(
                section_number=section_num,
                hierarchy_level=hierarchy,
                figure_references=references['figures'],
                template_references=references['templates']
            )
            
            chunk = DocumentChunk(
                chunk_id=self.generate_chunk_id("GEN"),
                chunk_type=ChunkType.METHODOLOGY,
                title=f"{section_name}: {section_num}",
                content=subsection.strip(),
                metadata=metadata,
                size_bytes=len(subsection.encode('utf-8'))
            )
            
            chunks.append(chunk)
        
        return chunks

    def export_chunks_metadata(self) -> Dict[str, Any]:
        """Export chunk metadata for analysis and optimization."""
        metadata_export = {
            'total_chunks': len(self.chunks),
            'chunk_types': {},
            'size_distribution': {},
            'relationships_map': {},
            'component_breakdown': {}
        }
        
        # Analyze chunk types
        for chunk_type in ChunkType:
            type_chunks = [c for c in self.chunks if c.chunk_type == chunk_type]
            metadata_export['chunk_types'][chunk_type.value] = {
                'count': len(type_chunks),
                'avg_size': sum(c.size_bytes for c in type_chunks) / len(type_chunks) if type_chunks else 0
            }
        
        # Size distribution
        sizes = [c.size_bytes for c in self.chunks]
        metadata_export['size_distribution'] = {
            'min': min(sizes) if sizes else 0,
            'max': max(sizes) if sizes else 0,
            'avg': sum(sizes) / len(sizes) if sizes else 0
        }
        
        # Relationship mapping
        for chunk in self.chunks:
            metadata_export['relationships_map'][chunk.chunk_id] = {
                'dependencies': chunk.dependencies,
                'related': chunk.related_chunks
            }
        
        return metadata_export

    # -------------------- New Helper / Export Methods -------------------- #
    def export_chunks_to_json(self, output_path: str) -> str:
        """Serialize current chunks list to a JSON file.

        Args:
            output_path: Destination JSON file path.
        Returns:
            The path written.
        """
        def serialize_chunk(chunk: DocumentChunk) -> Dict[str, Any]:
            meta = asdict(chunk.metadata)
            # Convert Enum inside metadata
            if meta.get('component_type') is not None:
                meta['component_type'] = meta['component_type'].value  # type: ignore
            return {
                'chunk_id': chunk.chunk_id,
                'chunk_type': chunk.chunk_type.value,
                'title': chunk.title,
                'content': chunk.content,
                'metadata': meta,
                'dependencies': chunk.dependencies,
                'related_chunks': chunk.related_chunks,
                'size_bytes': chunk.size_bytes
            }

        export_payload = [serialize_chunk(c) for c in self.chunks]
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_payload, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Exported {len(export_payload)} chunks to {output_path}")
        return output_path

    def export_analysis_metadata(self, output_path: str) -> str:
        """Optional: export aggregate metadata to separate JSON (diagnostics)."""
        meta = self.export_chunks_metadata()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Exported analysis metadata to {output_path}")
        return output_path


def load_pdf_text(pdf_path: str) -> str:
    """Load text from a PDF using pdfplumber. Returns empty string if not available."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdfplumber is None:
        raise ImportError("pdfplumber is not installed. Install with 'pip install pdfplumber'.")
    text_parts: List[str] = []
    with pdfplumber.open(pdf_path) as pdf:  # type: ignore
        for page in pdf.pages:
            page_text = page.extract_text() or ''
            text_parts.append(page_text)
    return '\n'.join(text_parts)

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    parser = ArgumentParser(description="Chunk the GEC-2015 user manual and export JSON")
    parser.add_argument('--pdf', default='GEC User_manual.pdf', help='Path to the user manual PDF')
    parser.add_argument('--out', default='gec_usermanual_chunks.json', help='Output JSON file for chunks')
    parser.add_argument('--meta', default='gec_usermanual_metadata.json', help='(Optional) aggregate metadata JSON file')
    parser.add_argument('--no-meta', action='store_true', help='Skip writing aggregate metadata file')
    args = parser.parse_args()

    chunker = GEC2015DocumentChunker()
    print("GEC-2015 Document Chunker initialized successfully!")
    print(f"Supported chunk types: {[ct.value for ct in ChunkType]}")
    print(f"Supported component types: {[ct.value for ct in ComponentType]}")

    try:
        manual_text = load_pdf_text(args.pdf)
    except Exception as e:  # Provide clear feedback and exit gracefully
        logging.error(f"Failed to load PDF: {e}")
        raise SystemExit(1)

    logging.info("Processing user manual text into chunks...")
    chunker.process_document(manual_text)
    chunk_file = chunker.export_chunks_to_json(args.out)
    logging.info(f"Chunk file written: {chunk_file}")

    if not args.no_meta:
        meta_file = chunker.export_analysis_metadata(args.meta)
        logging.info(f"Metadata file written: {meta_file}")

    print(f"Done. Chunks JSON: {args.out}")
    if not args.no_meta:
        print(f"Metadata JSON: {args.meta}")