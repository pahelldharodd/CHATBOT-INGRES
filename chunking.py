import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import hashlib

# Updated columns based on your cleaned CSV metadata
columns_to_use = [
    "Year", "S.No", "STATE", "DISTRICT", "RR_C", "RR_C_NC", "RR_PQ", "RR_Tot", 
    "TGA_C", "TGA_C_NC", "TGA_PQ", "TGA_Tot", "TGA", "TGA_Tot.1",
    "GWR_RR_C", "GWR_RR_C_NC", "GWR_RR_PQ", "GWR_RR_Tot", "GWR_CI_C", "GWR_CI_C_NC", 
    "GWR_CI_PQ", "GWR_CI_Tot", "GWR_SWI_IRR_C", "GWR_SWI_IRR_C_NC", "GWR_SWI_IRR_PQ", 
    "GWR_SWI_IRR_Tot", "GWR_GWI_IRR_C", "GWR_GWI_IRR_C_NC", "GWR_GWI_IRR_PQ", 
    "GWR_GWI_IRR_Tot", "GWR_TP_C", "GWR_TP_C_NC", "GWR_TP_PQ", "GWR_TP_Tot",
    "GWR_WCS_C", "GWR_WCS_C_NC", "GWR_WCS_PQ", "GWR_WCS_Tot", "GWR_PL_C", 
    "GWR_PL_C_NC", "GWR_PL_PQ", "GWR_PL_Tot", "GWR_SF_C", "GWR_SF_C_NC", 
    "GWR_SF_PQ", "GWR_SF_Tot", "GWR_C", "GWR_C_NC", "GWR_PQ", "GWR_Tot",
    "IFO_BF_C", "IFO_BF_C_NC", "IFO_BF_PQ", "IFO_BF_Tot", "IFO_SR_C", 
    "IFO_SR_C_NC", "IFO_SR_PQ", "IFO_SR_Tot", "IFO_LF_C", "IFO_LF_C_NC", 
    "IFO_LF_PQ", "IFO_LF_Tot", "IFO_VF_C", "IFO_VF_C_NC", "IFO_VF_PQ", 
    "IFO_VF_Tot", "IFO_EV_C", "IFO_EV_C_NC", "IFO_EV_PQ", "IFO_EV_Tot",
    "IFO_TR_C", "IFO_TR_C_NC", "IFO_TR_PQ", "IFO_TR_Tot", "IFO_ET_C", 
    "IFO_ET_C_NC", "IFO_ET_PQ", "IFO_ET_Tot", "IFO_C", "IFO_C_NC", 
    "IFO_PQ", "IFO_Tot", "AGR_C", "AGR_C_NC", "AGR_PQ", "AGR_Tot",
    "EFR_C", "EFR_C_NC", "EFR_PQ", "EFR_Tot", "AER_C", "AER_C_NC", 
    "AER_PQ", "AER_Tot", "GWE_DOM_C", "GWE_DOM_C_NC", "GWE_DOM_PQ", 
    "GWE_DOM_Tot", "GWE_IND_C", "GWE_IND_C_NC", "GWE_IND_PQ", "GWE_IND_Tot",
    "GWE_IRR_C", "GWE_IRR_C_NC", "GWE_IRR_PQ", "GWE_IRR_Tot", "GWE_C", 
    "GWE_C_NC", "GWE_PQ", "GWE_Tot", "DOM_DOM_C", "DOM_DOM_C_NC", 
    "DOM_DOM_PQ", "DOM_DOM_Tot", "NAG_C", "NAG_C_NC", "NAG_PQ", "NAG_Tot",
    "QT_MP_C", "QT_MP_C_NC", "QT_MP_PQ", "QT_OP_C", "QT_OP_C_NC", "QT_OP_PQ",
    "APR_WL", "APR_FP", "APR_SD", "CSA_C", "CSA_C_NC", "CSA_PQ", "CSA_Tot",
    "UCA_FR", "UCA_SL", "CFA_FR", "CFA_SL", "TGAH_FR", "TGAH_SL"
]

@dataclass
class ChunkMetadata:
    """Metadata structure for groundwater data chunks"""
    administrative: Dict[str, Any]
    hydro_classification: Dict[str, Any]
    data_quality_matrix: Dict[str, Any]
    temporal_context: Dict[str, Any]
    special_conditions: Dict[str, Any]
    chunk_type: str
    confidence_score: float

class INGRESDataChunker:
    """
    Comprehensive chunking pipeline for INGRES groundwater data
    Implements hierarchical, parameter-based, and quality-aware chunking
    """
    
    def __init__(self):
        self.column_mappings = self._define_column_mappings()
        self.quality_indicators = ['C', 'NC', 'PQ']
        self.aquifer_types = ['Unconfined', 'Confined', 'Semi-Confined']
        
    def _define_column_mappings(self) -> Dict[str, List[str]]:
        """Define parameter groupings based on the cleaned CSV column names"""
        return {
            'core_assessment': [
                'RR_C', 'RR_C_NC', 'RR_PQ', 'RR_Tot',
                'GWR_Tot', 'GWE_Tot', 'IFO_Tot', 'AGR_Tot', 'EFR_Tot', 'AER_Tot'
            ],
            'administrative': [
                'STATE', 'DISTRICT', 'Year', 'S.No'
            ],
            'recharge_sources': [
                'GWR_RR_Tot', 'GWR_CI_Tot', 'GWR_SWI_IRR_Tot', 'GWR_GWI_IRR_Tot',
                'GWR_TP_Tot', 'GWR_WCS_Tot', 'GWR_PL_Tot', 'GWR_SF_Tot'
            ],
            'aquifer_resources': [
                'TGA', 'TGA_Tot', 'TGAH_FR', 'TGAH_SL',
                'CSA_Tot', 'UCA_FR', 'UCA_SL', 'CFA_FR', 'CFA_SL'
            ],
            'usage_allocation': [
                'GWE_DOM_Tot', 'GWE_IND_Tot', 'GWE_IRR_Tot', 'GWE_Tot',
                'DOM_DOM_Tot', 'NAG_Tot'
            ],
            'environmental': [
                'APR_WL', 'APR_FP', 'APR_SD', 'CSA_Tot', 'UCA_FR', 'UCA_SL', 'CFA_FR', 'CFA_SL'
            ],
            'quality_parameters': [
                'QT_MP_C', 'QT_MP_C_NC', 'QT_MP_PQ', 'QT_OP_C', 'QT_OP_C_NC', 'QT_OP_PQ'
            ]
        }
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load groundwater data from cleaned CSV file (header row is first row)"""
        try:
            df = pd.read_csv(file_path)
            print(f"Loaded data with {len(df)} records and {len(df.columns)} columns")
            print("First few columns:", df.columns.tolist()[:10])
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the groundwater data"""
        df_processed = df.copy()
        
        # Handle missing values
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        df_processed[numeric_cols] = df_processed[numeric_cols].fillna(0)
        
        # Standardize text columns
        text_cols = df_processed.select_dtypes(include=['object']).columns
        for col in text_cols:
            df_processed[col] = df_processed[col].astype(str).str.strip()
        
        # Convert important columns to numeric, coercing errors to NaN
        for col in ['RR_Tot', 'GWR_Tot', 'GWE_Tot', 'IFO_Tot', 'AGR_Tot', 'EFR_Tot', 'AER_Tot']:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Calculate derived metrics
        df_processed = self._calculate_derived_metrics(df_processed)
        
        return df_processed
    
    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional metrics for better context"""
        
        # Sustainability ratio (example: RR_Tot / GWE_Tot)
        if 'RR_Tot' in df.columns and 'GWE_Tot' in df.columns:
            df['Sustainability_Ratio'] = df['RR_Tot'] / (df['GWE_Tot'] + 0.001)

        # Resource stress level (example: use GWE_Tot as a proxy if no direct % column)
        if 'GWE_Tot' in df.columns and 'RR_Tot' in df.columns:
            df['Resource_Stress_Level'] = (df['GWE_Tot'] / (df['RR_Tot'] + 0.001)).apply(
                lambda x: 'Over-Exploited' if x > 1.0 else 
                         'Critical' if x > 0.9 else 
                         'Semi-Critical' if x > 0.7 else 'Safe'
            )

        # Dominant aquifer type (example: pick max from available aquifer columns)
        aquifer_cols = [col for col in ['TGA', 'TGA_Tot', 'TGAH_FR', 'TGAH_SL'] if col in df.columns]
        if aquifer_cols:
            df['Dominant_Aquifer'] = df[aquifer_cols].idxmax(axis=1)
        
        return df
    
    def create_hierarchical_chunks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create hierarchical chunks: State -> District -> Assessment Unit"""
        chunks = []
        
        # Level 1: State-level chunks
        for state in df['STATE'].unique():
            state_data = df[df['STATE'] == state]
            state_chunk = self._create_state_chunk(state_data, state)
            chunks.append(state_chunk)
        
        # Level 2: District-level chunks
        for state in df['STATE'].unique():
            state_data = df[df['STATE'] == state]
            for district in state_data['DISTRICT'].unique():
                district_data = state_data[state_data['DISTRICT'] == district]
                district_chunk = self._create_district_chunk(district_data, state, district)
                chunks.append(district_chunk)
        
        # Level 3: Assessment unit chunks
        for _, row in df.iterrows():
            unit_chunk = self._create_unit_chunk(row)
            chunks.append(unit_chunk)
        
        return chunks
    
    def _create_state_chunk(self, state_data: pd.DataFrame, state: str) -> Dict[str, Any]:
        """Create state-level summary chunk"""
        # Calculate state-level statistics
        numeric_cols = state_data.select_dtypes(include=[np.number]).columns
        state_summary = state_data[numeric_cols].agg(['mean', 'sum', 'min', 'max']).round(2)
        
        # Count assessment units by category
        category_counts = state_data['Resource_Stress_Level'].value_counts().to_dict()
        
        # Generate textual description
        content = self._generate_state_description(state, state_summary, category_counts, len(state_data))
        
        metadata = ChunkMetadata(
            administrative={
                'state': state,
                'district': 'ALL',
                'assessment_unit': 'STATE_SUMMARY',
                'total_units': len(state_data),
                'geographical_area_ha': state_data.get('TGA', pd.Series([0]*len(state_data))).sum()
            },
            hydro_classification={
                'category_distribution': category_counts,
                'avg_extraction_stage': state_data.get('GWE_Tot', pd.Series([0]*len(state_data))).mean(),
                'dominant_stress_level': max(category_counts, key=category_counts.get) if category_counts else 'Safe'
            },
            data_quality_matrix=self._calculate_quality_matrix(state_data),
            temporal_context={
                'assessment_year': 'AY_2024-25',
                'aggregation_level': 'STATE',
                'data_freshness': 'CURRENT'
            },
            special_conditions={},
            chunk_type='STATE_SUMMARY',
            confidence_score=self._calculate_confidence_score(state_data)
        )
        
        return {
            'chunk_id': f"STATE_{state}_{hashlib.md5(state.encode()).hexdigest()[:8]}",
            'content': content,
            'metadata': metadata.__dict__,
            'chunk_size': len(content),
            'data_points': len(state_data)
        }
    
    def _create_district_chunk(self, district_data: pd.DataFrame, state: str, district: str) -> Dict[str, Any]:
        """Create district-level summary chunk"""
        numeric_cols = district_data.select_dtypes(include=[np.number]).columns
        district_summary = district_data[numeric_cols].agg(['mean', 'sum', 'min', 'max']).round(2)
        category_counts = district_data['Resource_Stress_Level'].value_counts().to_dict()
        content = self._generate_district_description(state, district, district_summary, category_counts, len(district_data))
        
        metadata = ChunkMetadata(
            administrative={
                'state': state,
                'district': district,
                'assessment_unit': 'DISTRICT_SUMMARY',
                'total_units': len(district_data),
                'geographical_area_ha': district_data.get('TGA', pd.Series([0]*len(district_data))).sum()
            },
            hydro_classification={
                'category_distribution': category_counts,
                'avg_extraction_stage': district_data.get('GWE_Tot', pd.Series([0]*len(district_data))).mean(),
                'dominant_stress_level': max(category_counts, key=category_counts.get) if category_counts else 'Safe'
            },
            data_quality_matrix=self._calculate_quality_matrix(district_data),
            temporal_context={
                'assessment_year': 'AY_2024-25',
                'aggregation_level': 'DISTRICT',
                'data_freshness': 'CURRENT'
            },
            special_conditions={},
            chunk_type='DISTRICT_SUMMARY',
            confidence_score=self._calculate_confidence_score(district_data)
        )
        
        return {
            'chunk_id': f"DISTRICT_{state}_{district}_{hashlib.md5((state+district).encode()).hexdigest()[:8]}",
            'content': content,
            'metadata': metadata.__dict__,
            'chunk_size': len(content),
            'data_points': len(district_data)
        }
    
    def _create_unit_chunk(self, row: pd.Series) -> Dict[str, Any]:
        """Create assessment unit-level detailed chunk"""
        # Generate comprehensive unit description
        content = self._generate_unit_description(row)
        
        metadata = ChunkMetadata(
            administrative={
                'state': row['STATE'],
                'district': row['DISTRICT'],
                'assessment_unit': row.get('S.No', 'UNKNOWN'),
                'geographical_area_ha': row.get('TGA', 0)
            },
            hydro_classification={
                'stage_extraction_percent': row.get('GWE_Tot', 0),
                'safety_category': row.get('Resource_Stress_Level', 'Unknown'),
                'sustainability_ratio': row.get('Sustainability_Ratio', 0),
                'dominant_aquifer_type': row.get('Dominant_Aquifer', 'Unknown')
            },
            data_quality_matrix=self._calculate_unit_quality_matrix(row),
            temporal_context={
                'assessment_year': 'AY_2024-25',
                'aggregation_level': 'UNIT',
                'data_freshness': 'CURRENT'
            },
            special_conditions={},
            chunk_type='ASSESSMENT_UNIT',
            confidence_score=self._calculate_unit_confidence_score(row)
        )
        
        return {
            'chunk_id': f"UNIT_{row['STATE']}_{row['DISTRICT']}_{row.get('S.No', 'UNKNOWN')}_{hashlib.md5((str(row['STATE'])+str(row['DISTRICT'])+str(row.get('S.No', 'UNKNOWN'))).encode()).hexdigest()[:8]}",
            'content': content,
            'metadata': metadata.__dict__,
            'chunk_size': len(content),
            'data_points': 1
        }
    
    def create_parameter_chunks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create parameter-focused thematic chunks"""
        parameter_chunks = []
        
        for param_group, columns in self.column_mappings.items():
            available_columns = [col for col in columns if col in df.columns]
            if not available_columns:
                continue
                
            for _, row in df.iterrows():
                chunk = self._create_parameter_chunk(row, param_group, available_columns)
                parameter_chunks.append(chunk)
        
        return parameter_chunks
    
    def _create_parameter_chunk(self, row: pd.Series, param_group: str, columns: List[str]) -> Dict[str, Any]:
        """Create a parameter-focused chunk"""
        
        content = self._generate_parameter_description(row, param_group, columns)
        
        unit_id = row.get('S.No', 'UNKNOWN')
        chunk_id = f"PARAM_{param_group}_{row.get('STATE', 'UNKNOWN')}_{row.get('DISTRICT', 'UNKNOWN')}_{unit_id}_{hashlib.md5((param_group+str(row.get('STATE', 'UNKNOWN'))+str(row.get('DISTRICT', 'UNKNOWN'))+str(unit_id)).encode()).hexdigest()[:8]}"
        
        return {
            'chunk_id': chunk_id,
            'content': content,
            'parameter_group': param_group,
            'administrative_unit': f"{row.get('STATE', 'UNKNOWN')}-{row.get('DISTRICT', 'UNKNOWN')}-{unit_id}",
            'chunk_size': len(content),
            'parameter_count': len(columns)
        }
    
    def create_quality_aware_chunks(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create chunks based on data quality indicators"""
        quality_chunks = []
        
        for quality_level in ['HIGH', 'MEDIUM', 'LOW']:
            quality_chunk = self._create_quality_chunk(df, quality_level)
            if quality_chunk:
                quality_chunks.append(quality_chunk)
        
        return quality_chunks
    
    def _generate_state_description(self, state: str, summary: pd.DataFrame, categories: Dict, unit_count: int) -> str:
        """Generate textual description for state-level data"""
        
        # Check for available columns and use them safely
        total_geo_area = summary.loc['sum', 'TGA'] if 'TGA' in summary.columns else 0
        total_recharge = summary.loc['sum', 'RR_Tot'] if 'RR_Tot' in summary.columns else 0
        total_extraction = summary.loc['sum', 'GWE_Tot'] if 'GWE_Tot' in summary.columns else 0
        avg_sustainability = summary.loc['mean', 'Sustainability_Ratio'] if 'Sustainability_Ratio' in summary.columns else 0
        
        # Try to get future availability columns - they might not exist in cleaned data
        net_availability = 0
        domestic_allocation = 0
        if 'NAG_Tot' in summary.columns:
            net_availability = summary.loc['sum', 'NAG_Tot']
        if 'DOM_DOM_Tot' in summary.columns:
            domestic_allocation = summary.loc['sum', 'DOM_DOM_Tot']
        
        description = f"""STATE GROUNDWATER ASSESSMENT: {state}

OVERVIEW:
- Total Assessment Units: {unit_count}
- Total Geographical Area: {total_geo_area:,.0f} hectares

GROUNDWATER RESOURCES:
- Total Annual Recharge: {total_recharge:,.0f} ham
- Total Extraction: {total_extraction:,.0f} ham
- Average Sustainability Ratio: {avg_sustainability:,.2f}

RESOURCE CLASSIFICATION:"""
        
        for category, count in categories.items():
            percentage = (count / unit_count) * 100 if unit_count > 0 else 0
            description += f"\n- {category}: {count} units ({percentage:.1f}%)"
        
        if net_availability > 0 or domestic_allocation > 0:
            description += f"""

FUTURE AVAILABILITY:
- Net Annual Availability for Future Use: {net_availability:,.0f} ham
- Domestic Allocation: {domestic_allocation:,.0f} ham"""
        
        return description.strip()
    
    def _generate_district_description(self, state: str, district: str, summary: pd.DataFrame, categories: Dict, unit_count: int) -> str:
        """Generate textual description for district-level data"""
        
        # Check for available columns and use them safely
        total_geo_area = summary.loc['sum', 'TGA'] if 'TGA' in summary.columns else 0
        total_recharge = summary.loc['sum', 'RR_Tot'] if 'RR_Tot' in summary.columns else 0
        total_extraction = summary.loc['sum', 'GWE_Tot'] if 'GWE_Tot' in summary.columns else 0
        avg_sustainability = summary.loc['mean', 'Sustainability_Ratio'] if 'Sustainability_Ratio' in summary.columns else 0
        
        description = f"""DISTRICT GROUNDWATER ASSESSMENT: {district}, {state}

DISTRICT OVERVIEW:
- Assessment Units: {unit_count}
- Geographical Area: {total_geo_area:,.0f} hectares

WATER BALANCE:
- Annual Recharge: {total_recharge:,.0f} ham
- Current Extraction: {total_extraction:,.0f} ham
- Average Sustainability Ratio: {avg_sustainability:,.2f}

UNIT CLASSIFICATION:"""
        
        for category, count in categories.items():
            percentage = (count / unit_count) * 100 if unit_count > 0 else 0
            description += f"\n- {category}: {count} units ({percentage:.1f}%)"
        
        return description.strip()
    
    def _generate_unit_description(self, row: pd.Series) -> str:
        """Generate comprehensive description for assessment unit"""
        unit_name = row.get('S.No', 'UNKNOWN')
        district = row.get('DISTRICT', 'UNKNOWN')
        state = row.get('STATE', 'UNKNOWN')
        
        # Use available columns safely
        geo_area = row.get('TGA', 0)
        resource_class = row.get('Resource_Stress_Level', 'Unknown')
        annual_recharge = row.get('RR_Tot', 0)
        extraction = row.get('GWE_Tot', 0)
        sustainability_ratio = row.get('Sustainability_Ratio', 0)
        
        description = f"""ASSESSMENT UNIT: {unit_name}, {district}, {state}

BASIC INFORMATION:
- Geographical Area: {geo_area:,.0f} hectares
- Resource Classification: {resource_class}

GROUNDWATER RESOURCES:
- Annual Recharge: {annual_recharge:,.0f} ham
- Current Extraction: {extraction:,.0f} ham
- Sustainability Ratio: {sustainability_ratio:,.2f}"""
        
        return description.strip()
    
    def _generate_parameter_description(self, row: pd.Series, param_group: str, columns: List[str]) -> str:
        """Generate parameter-focused description"""
        
        # Use S.No instead of ASSESSMENT UNIT since that's what's in your cleaned data
        unit_id = f"{row.get('S.No', 'UNKNOWN')}, {row.get('DISTRICT', 'UNKNOWN')}, {row.get('STATE', 'UNKNOWN')}"
        
        description = f"""{param_group.upper().replace('_', ' ')} DATA: {unit_id}

"""
        
        for col in columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value) and value != 0:
                    description += f"- {col}: {value}\n"
        
        return description.strip()
    
    def _calculate_quality_matrix(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics for a dataset"""
        
        total_params = len(data.columns)
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        return {
            'total_parameters': total_params,
            'numeric_parameters': len(numeric_cols),
            'completeness_score': (1 - data.isnull().sum().sum() / (len(data) * total_params)) * 100,
            'numeric_completeness': (1 - data[numeric_cols].isnull().sum().sum() / (len(data) * len(numeric_cols))) * 100 if len(numeric_cols) > 0 else 0
        }
    
    def _calculate_unit_quality_matrix(self, row: pd.Series) -> Dict[str, Any]:
        """Calculate quality matrix for a single unit"""
        
        non_null_count = row.notna().sum()
        total_count = len(row)
        
        return {
            'completeness_score': (non_null_count / total_count) * 100,
            'missing_parameters': total_count - non_null_count,
            'data_reliability': 'High' if (non_null_count / total_count) > 0.8 else 'Medium' if (non_null_count / total_count) > 0.6 else 'Low'
        }
    
    def _calculate_confidence_score(self, data: pd.DataFrame) -> float:
        """Calculate overall confidence score for the data"""
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        # Completeness score
        completeness = 1 - (data.isnull().sum().sum() / (len(data) * len(data.columns)))
        
        # Consistency score (based on reasonable value ranges)
        consistency = 1.0  # Simplified - would need domain knowledge for proper implementation
        
        # Coverage score
        coverage = len(data) / max(len(data), 1)  # Simplified
        
        return (completeness + consistency + coverage) / 3
    
    def _calculate_unit_confidence_score(self, row: pd.Series) -> float:
        """Calculate confidence score for a single unit"""
        
        non_null_ratio = row.notna().sum() / len(row)
        
        # Additional checks for critical parameters
        critical_params = ['RR_Tot', 'GWE_Tot', 'AER_Tot', 'TGA']
        
        critical_completeness = sum(1 for param in critical_params if param in row.index and pd.notna(row[param])) / len(critical_params)
        
        return (non_null_ratio + critical_completeness) / 2
    
    def _create_quality_chunk(self, df: pd.DataFrame, quality_level: str) -> Optional[Dict[str, Any]]:
        """Create chunks based on data quality level"""
        
        if quality_level == 'HIGH':
            # Units with >80% data completeness
            quality_data = df[df.apply(lambda row: row.notna().sum() / len(row) > 0.8, axis=1)]
        elif quality_level == 'MEDIUM':
            # Units with 60-80% data completeness  
            quality_data = df[df.apply(lambda row: 0.6 < row.notna().sum() / len(row) <= 0.8, axis=1)]
        else:  # LOW
            # Units with <60% data completeness
            quality_data = df[df.apply(lambda row: row.notna().sum() / len(row) <= 0.6, axis=1)]
        
        if len(quality_data) == 0:
            return None
        
        content = f"""DATA QUALITY ASSESSMENT: {quality_level} CONFIDENCE LEVEL

Units in this category: {len(quality_data)}
Average data completeness: {quality_data.apply(lambda row: row.notna().sum() / len(row), axis=1).mean():.2%}

States covered: {', '.join(quality_data['STATE'].unique())}

Recommended usage:"""
        
        if quality_level == 'HIGH':
            content += "\n- Primary decision making\n- Policy formulation\n- Detailed analysis"
        elif quality_level == 'MEDIUM':
            content += "\n- Trend analysis\n- Comparative studies\n- Secondary validation"
        else:
            content += "\n- Data gap identification\n- Future data collection planning\n- Preliminary assessments only"
        
        return {
            'chunk_id': f"QUALITY_{quality_level}_{hashlib.md5(quality_level.encode()).hexdigest()[:8]}",
            'content': content,
            'quality_level': quality_level,
            'unit_count': len(quality_data),
            'chunk_size': len(content)
        }
    
    def process_dataset(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Main processing pipeline with robust error handling"""
        
        print("Loading and preprocessing data...")
        df = self.load_data(file_path)
        if df.empty:
            print("No data loaded, skipping processing")
            return {}
        
        df_processed = self.preprocess_data(df)
        if df_processed.empty:
            print("No data after preprocessing, skipping processing") 
            return {}
        
        results = {
            'hierarchical_chunks': [],
            'parameter_chunks': [],
            'quality_chunks': [],
            'total_chunks': 0,
            'processing_summary': {
                'total_units': len(df_processed),
                'columns_available': len(df_processed.columns),
                'chunk_types': []
            }
        }
        
        # Try hierarchical chunks
        try:
            print("Creating hierarchical chunks...")
            hierarchical_chunks = self.create_hierarchical_chunks(df_processed)
            results['hierarchical_chunks'] = hierarchical_chunks
            if hierarchical_chunks:
                results['processing_summary']['chunk_types'].append('hierarchical')
        except Exception as e:
            print(f"Error creating hierarchical chunks: {e}")
        
        # Try parameter-based chunks
        try:
            print("Creating parameter-based chunks...")
            parameter_chunks = self.create_parameter_chunks(df_processed)
            results['parameter_chunks'] = parameter_chunks
            if parameter_chunks:
                results['processing_summary']['chunk_types'].append('parameter_based')
        except Exception as e:
            print(f"Error creating parameter chunks: {e}")
        
        # Try quality-aware chunks
        try:
            print("Creating quality-aware chunks...")
            quality_chunks = self.create_quality_aware_chunks(df_processed)
            results['quality_chunks'] = quality_chunks
            if quality_chunks:
                results['processing_summary']['chunk_types'].append('quality_aware')
        except Exception as e:
            print(f"Error creating quality chunks: {e}")
        
        results['total_chunks'] = len(results['hierarchical_chunks']) + len(results['parameter_chunks']) + len(results['quality_chunks'])
        
        print(f"Processing complete! Generated {results['total_chunks']} chunks")
        print(f"Chunk types created: {results['processing_summary']['chunk_types']}")
        
        return results
    
    def process_multiple_datasets(self, file_paths: list) -> dict:
        all_results = {}
        for file_path in file_paths:
            print(f"\nProcessing file: {file_path}")
            result = self.process_dataset(file_path)
            all_results[file_path] = result
        return all_results
    
    def save_chunks(self, chunks_data: Dict[str, Any], output_path: str):
        """Save chunks to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"Chunks saved to {output_path}")

# Usage Example
if __name__ == "__main__":
    # Initialize chunker
    chunker = INGRESDataChunker()
    
    # Process all cleaned CSV datasets in clean_csv/
    import glob
    file_list = glob.glob('clean_csv/*.csv')
    print(f"Found {len(file_list)} CSV files to process.")
    results = chunker.process_multiple_datasets(file_list)
    for file, data in results.items():
        out_name = file.replace('.csv', '_chunks.json').replace('clean_csv/', '')
        chunker.save_chunks(data, out_name)
        print(f"Processed and saved chunks for {file}")
    print("All files processed.")