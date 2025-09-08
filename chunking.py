import pandas as pd
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from datetime import datetime
import hashlib
columns_to_use = [
    "STATE", "DISTRICT", "ASSESSMENT UNIT", "Rainfall (mm)", "Total Geographical Area (ha)",
    "Ground Water Recharge (ham)", "Annual Ground water Recharge (ham)", "Annual Extractable Ground water Resource (ham)",
    "Ground Water Extraction for all uses (ha.m)", "Stage of Ground Water Extraction (%)",
    "Allocation of Ground Water Resource for Domestic Utilisation for projected year 2025 (ham)",
    "Net Annual Ground Water Availability for Future Use (ham)", "Quality Tagging", "Coastal Areas",
    "In-Storage Unconfined Ground Water Resources(ham)", "Total Ground Water Availability in Unconfined Aquifier (ham)",
    "Dynamic Confined Ground Water Resources(ham)", "In-Storage Confined Ground Water Resources(ham)",
    "Total Confined Ground Water Resources (ham)", "Dynamic Semi Confined Ground Water Resources (ham)",
    "In-Storage Semi Confined Ground Water Resources (ham)", "Total Semi-Confined Ground Water Resources (ham)",
    "Total Ground Water Availability in the area (ham)", "Recharge Worthy Area (ha)", "Total Rainfall Recharge",
    "Canals", "Surface Water Irrigation", "Ground Water Irrigation", "Tanks and Ponds",
    "Water Conservation Structure", "Pipelines", "Sewages and Flash Flood Channels",
    "Waterlogged and shallow water Table", "Flood Prone", "Spring Discharge"
    # Add C, NC, PQ columns as needed
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
        """Define parameter groupings based on the metadata structure"""
        return {
            'core_assessment': [
                'Ground Water Recharge (ham)',
                'Annual Extractable Ground water Resource (ham)',
                'Ground Water Extraction for all uses (ha.m)',
                'Stage of Ground Water Extraction (%)',
                'Net Annual Ground Water Availability for Future Use (ham)'
            ],
            'administrative': [
                'STATE', 'DISTRICT', 'ASSESSMENT UNIT',
                'Total Geographical Area (ha)', 'Rainfall (mm)'
            ],
            'recharge_sources': [
                'Total Rainfall Recharge', 'Canals', 'Surface Water Irrigation',
                'Ground Water Irrigation', 'Tanks and Ponds',
                'Water Conservation Structure', 'Pipelines',
                'Sewages and Flash Flood Channels'
            ],
            'aquifer_resources': [
                'In-Storage Unconfined Ground Water Resources(ham)',
                'Total Ground Water Availability in Unconfined Aquifier (ham)',
                'Dynamic Confined Ground Water Resources(ham)',
                'In-Storage Confined Ground Water Resources(ham)',
                'Total Confined Ground Water Resources (ham)',
                'Dynamic Semi Confined Ground Water Resources (ham)',
                'In-Storage Semi Confined Ground Water Resources (ham)',
                'Total Semi-Confined Ground Water Resources (ham)',
                'Total Ground Water Availability in the area (ham)'
            ],
            'usage_allocation': [
                'Allocation of Ground Water Resource for Domestic Utilisation for projected year 2025 (ham)',
                'Domestic', 'Industrial', 'Irrigation'
            ],
            'environmental': [
                'Environmental Flows (ham)', 'Coastal Areas',
                'Waterlogged and shallow water Table', 'Flood Prone',
                'Spring Discharge', 'Evaporation', 'Transpiration', 'Evapotranspiration'
            ],
            'quality_parameters': [
                'Quality Tagging', 'Fresh', 'Saline', 'Major Parameter Present',
                'Other Parameters Present'
            ]
        }
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load groundwater data from Excel file, using row 8 as header (header=7)"""
        try:
            df = pd.read_excel(file_path, header=7)
            print(f"Loaded data with {len(df)} records and {len(df.columns)} columns")
            print("Columns:", df.columns.tolist())
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
        for col in [
            'Ground Water Recharge (ham)',
            'Ground Water Extraction for all uses (ha.m)',
            'Stage of Ground Water Extraction (%)'
        ]:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
        
        # Calculate derived metrics
        df_processed = self._calculate_derived_metrics(df_processed)
        
        return df_processed
    
    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate additional metrics for better context"""
        
        # Sustainability ratio
        if 'Ground Water Recharge (ham)' in df.columns and 'Ground Water Extraction for all uses (ha.m)' in df.columns:
            df['Sustainability_Ratio'] = df['Ground Water Recharge (ham)'] / (df['Ground Water Extraction for all uses (ha.m)'] + 0.001)
        
        # Resource stress level
        if 'Stage of Ground Water Extraction (%)' in df.columns:
            df['Resource_Stress_Level'] = df['Stage of Ground Water Extraction (%)'].apply(
                lambda x: 'Over-Exploited' if x > 100 else 
                         'Critical' if x > 90 else 
                         'Semi-Critical' if x > 70 else 'Safe'
            )
        
        # Dominant aquifer type
        aquifer_cols = [col for col in df.columns if 'Total' in col and any(aq in col for aq in self.aquifer_types)]
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
                'geographical_area_ha': state_data.get('Total Geographical Area (ha)', pd.Series([0]*len(state_data))).sum()
            },
            hydro_classification={
                'category_distribution': category_counts,
                'avg_extraction_stage': state_data['Stage of Ground Water Extraction (%)'].mean(),
                'dominant_stress_level': max(category_counts, key=category_counts.get)
            },
            data_quality_matrix=self._calculate_quality_matrix(state_data),
            temporal_context={
                'assessment_year': 'AY_2024-25',
                'aggregation_level': 'STATE',
                'data_freshness': 'CURRENT'
            },
            special_conditions={
                'coastal_units': len(state_data[state_data.get('Coastal Areas', 0) > 0]),
                'flood_prone_units': len(state_data[state_data.get('Flood Prone', 0) > 0]),
                'has_springs': len(state_data[state_data.get('Spring Discharge', 0) > 0]) > 0
            },
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
                'geographical_area_ha': district_data['Total Geographical Area (ha)'].sum()
            },
            hydro_classification={
                'category_distribution': category_counts,
                'avg_extraction_stage': district_data['Stage of Ground Water Extraction (%)'].mean(),
                'dominant_stress_level': max(category_counts, key=category_counts.get) if category_counts else 'Safe'
            },
            data_quality_matrix=self._calculate_quality_matrix(district_data),
            temporal_context={
                'assessment_year': 'AY_2024-25',
                'aggregation_level': 'DISTRICT',
                'data_freshness': 'CURRENT'
            },
            special_conditions={
                'coastal_units': len(district_data[district_data.get('Coastal Areas', 0) > 0]),
                'flood_prone_units': len(district_data[district_data.get('Flood Prone', 0) > 0]),
                'waterlogged_units': len(district_data[district_data.get('Waterlogged and shallow water Table', 0) > 0])
            },
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
                'assessment_unit': row['ASSESSMENT UNIT'],
                'geographical_area_ha': row.get('Total Geographical Area (ha)', 0)
            },
            hydro_classification={
                'stage_extraction_percent': row.get('Stage of Ground Water Extraction (%)', 0),
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
            special_conditions={
                'is_coastal': row.get('Coastal Areas', 0) > 0,
                'is_waterlogged': row.get('Waterlogged and shallow water Table', 0) > 0,
                'is_flood_prone': row.get('Flood Prone', 0) > 0,
                'has_springs': row.get('Spring Discharge', 0) > 0
            },
            chunk_type='ASSESSMENT_UNIT',
            confidence_score=self._calculate_unit_confidence_score(row)
        )
        
        return {
            'chunk_id': f"UNIT_{row['STATE']}_{row['DISTRICT']}_{row['ASSESSMENT UNIT']}_{hashlib.md5((str(row['STATE'])+str(row['DISTRICT'])+str(row['ASSESSMENT UNIT'])).encode()).hexdigest()[:8]}",
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
        
        chunk_id = f"PARAM_{param_group}_{row['STATE']}_{row['DISTRICT']}_{row['ASSESSMENT UNIT']}_{hashlib.md5((param_group+str(row['STATE'])+str(row['DISTRICT'])+str(row['ASSESSMENT UNIT'])).encode()).hexdigest()[:8]}"
        
        return {
            'chunk_id': chunk_id,
            'content': content,
            'parameter_group': param_group,
            'administrative_unit': f"{row['STATE']}-{row['DISTRICT']}-{row['ASSESSMENT UNIT']}",
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
        
        description = f"""
        STATE GROUNDWATER ASSESSMENT: {state}
        
        OVERVIEW:
        - Total Assessment Units: {unit_count}
        - Total Geographical Area: {summary.loc['sum', 'Total Geographical Area (ha)']:,.0f} hectares
        - Average Rainfall: {summary.loc['mean', 'Rainfall (mm)']:,.1f} mm
        
        GROUNDWATER RESOURCES:
        - Total Annual Recharge: {summary.loc['sum', 'Ground Water Recharge (ham)']:,.0f} ham
        - Total Extractable Resources: {summary.loc['sum', 'Annual Extractable Ground water Resource (ham)']:,.0f} ham
        - Total Extraction: {summary.loc['sum', 'Ground Water Extraction for all uses (ha.m)']:,.0f} ham
        - Average Extraction Stage: {summary.loc['mean', 'Stage of Ground Water Extraction (%)']:,.1f}%
        
        RESOURCE CLASSIFICATION:
        """
        
        for category, count in categories.items():
            percentage = (count / unit_count) * 100
            description += f"- {category}: {count} units ({percentage:.1f}%)\n        "
        
        description += f"""
        
        FUTURE AVAILABILITY:
        - Net Annual Availability for Future Use: {summary.loc['sum', 'Net Annual Ground Water Availability for Future Use (ham)']:,.0f} ham
        - 2025 Domestic Allocation: {summary.loc['sum', 'Allocation of Ground Water Resource for Domestic Utilisation for projected year 2025 (ham)']:,.0f} ham
        """
        
        return description.strip()
    
    def _generate_district_description(self, state: str, district: str, summary: pd.DataFrame, categories: Dict, unit_count: int) -> str:
        """Generate textual description for district-level data"""
        
        description = f"""
        DISTRICT GROUNDWATER ASSESSMENT: {district}, {state}
        
        DISTRICT OVERVIEW:
        - Assessment Units: {unit_count}
        - Geographical Area: {summary.loc['sum', 'Total Geographical Area (ha)']:,.0f} hectares
        - Average Rainfall: {summary.loc['mean', 'Rainfall (mm)']:,.1f} mm
        
        WATER BALANCE:
        - Annual Recharge: {summary.loc['sum', 'Ground Water Recharge (ham)']:,.0f} ham
        - Extractable Resources: {summary.loc['sum', 'Annual Extractable Ground water Resource (ham)']:,.0f} ham
        - Current Extraction: {summary.loc['sum', 'Ground Water Extraction for all uses (ha.m)']:,.0f} ham
        - Extraction Stage: {summary.loc['mean', 'Stage of Ground Water Extraction (%)']:,.1f}%
        
        UNIT CLASSIFICATION:
        """
        
        for category, count in categories.items():
            percentage = (count / unit_count) * 100
            description += f"- {category}: {count} units ({percentage:.1f}%)\n        "
        
        return description.strip()
    
    def _generate_unit_description(self, row: pd.Series) -> str:
        """Generate comprehensive description for assessment unit"""
        
        unit_name = row['ASSESSMENT UNIT']
        district = row['DISTRICT']
        state = row['STATE']
        
        description = f"""
        ASSESSMENT UNIT: {unit_name}, {district}, {state}
        
        BASIC INFORMATION:
        - Geographical Area: {row.get('Total Geographical Area (ha)', 0):,.0f} hectares
        - Annual Rainfall: {row.get('Rainfall (mm)', 0):,.1f} mm
        - Resource Classification: {row.get('Resource_Stress_Level', 'Unknown')}
        
        GROUNDWATER RESOURCES:
        - Annual Recharge: {row.get('Ground Water Recharge (ham)', 0):,.0f} ham
        - Extractable Resources: {row.get('Annual Extractable Ground water Resource (ham)', 0):,.0f} ham
        - Current Extraction: {row.get('Ground Water Extraction for all uses (ha.m)', 0):,.0f} ham
        - Extraction Stage: {row.get('Stage of Ground Water Extraction (%)', 0):,.1f}%
        - Sustainability Ratio: {row.get('Sustainability_Ratio', 0):,.2f}
        
        AQUIFER INFORMATION:
        - Unconfined Resources: {row.get('Total Ground Water Availability in Unconfined Aquifier (ham)', 0):,.0f} ham
        - Confined Resources: {row.get('Total Confined Ground Water Resources (ham)', 0):,.0f} ham
        - Semi-Confined Resources: {row.get('Total Semi-Confined Ground Water Resources (ham)', 0):,.0f} ham
        - Total Availability: {row.get('Total Ground Water Availability in the area (ham)', 0):,.0f} ham
        
        FUTURE PROJECTIONS:
        - Net Future Availability: {row.get('Net Annual Ground Water Availability for Future Use (ham)', 0):,.0f} ham
        - 2025 Domestic Allocation: {row.get('Allocation of Ground Water Resource for Domestic Utilisation for projected year 2025 (ham)', 0):,.0f} ham
        
        SPECIAL CONDITIONS:
        """
        
        conditions = []
        if row.get('Coastal Areas', 0) > 0:
            conditions.append("Coastal Area")
        if row.get('Waterlogged and shallow water Table', 0) > 0:
            conditions.append("Waterlogged Area")
        if row.get('Flood Prone', 0) > 0:
            conditions.append("Flood Prone")
        if row.get('Spring Discharge', 0) > 0:
            conditions.append("Spring Discharge Present")
        
        if conditions:
            description += f"- {', '.join(conditions)}"
        else:
            description += "- No special environmental conditions reported"
        
        return description.strip()
    
    def _generate_parameter_description(self, row: pd.Series, param_group: str, columns: List[str]) -> str:
        """Generate parameter-focused description"""
        
        unit_id = f"{row['ASSESSMENT UNIT']}, {row['DISTRICT']}, {row['STATE']}"
        
        description = f"""
        {param_group.upper().replace('_', ' ')} DATA: {unit_id}
        
        """
        
        for col in columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value) and value != 0:
                    description += f"- {col}: {value}\n        "
        
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
        critical_params = [
            'Ground Water Recharge (ham)',
            'Annual Extractable Ground water Resource (ham)',
            'Ground Water Extraction for all uses (ha.m)',
            'Stage of Ground Water Extraction (%)'
        ]
        
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
        
        content = f"""
        DATA QUALITY ASSESSMENT: {quality_level} CONFIDENCE LEVEL
        
        Units in this category: {len(quality_data)}
        Average data completeness: {quality_data.apply(lambda row: row.notna().sum() / len(row), axis=1).mean():.2%}
        
        States covered: {', '.join(quality_data['STATE'].unique())}
        
        Recommended usage:
        """
        
        if quality_level == 'HIGH':
            content += "- Primary decision making\n        - Policy formulation\n        - Detailed analysis"
        elif quality_level == 'MEDIUM':
            content += "- Trend analysis\n        - Comparative studies\n        - Secondary validation"
        else:
            content += "- Data gap identification\n        - Future data collection planning\n        - Preliminary assessments only"
        
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
    
    # Example: Process multiple datasets
    file_list = [
        "datasets/INGRES_2022-23.xlsx",
        "datasets/INGRES_2024-25.xlsx"
    ]
    results = chunker.process_multiple_datasets(file_list)
    # Optionally, save each result

    for file, data in results.items():
        out_name = file.replace('.xlsx', '_chunks.json').replace('datasets/', '')
        chunker.save_chunks(data, out_name)
        # Print the first few chunks for each file
        print(f"\nFirst few chunks for {file}:")
        for chunk_type in ['hierarchical_chunks', 'parameter_chunks', 'quality_chunks']:
            chunks = data.get(chunk_type, [])
            print(f"  {chunk_type} (showing up to 3):")
            for chunk in chunks[:3]:
                print(f"    {chunk.get('chunk_id', 'no chunk_id')} | size: {chunk.get('chunk_size', 'n/a')}")
            if not chunks:
                print("    (none)")

    print("INGRES Data Chunking Pipeline Ready!")
    print("\nTo use:")
    print("1. chunker = INGRESDataChunker()")
    print("2. chunks_data = chunker.process_dataset('your_file.xlsx')")
    print("3. chunker.save_chunks(chunks_data, 'output_chunks.json')")