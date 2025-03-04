from typing import Dict, List, Optional, Tuple, Union
import xml.etree.ElementTree as ET
import pandas as pd
import json
from pathlib import Path
from .utils import setup_logger, safe_xml_find, process_dataframe
from .exceptions import OrphanetProcessorError

class OrphanetDataManager:
    """Process Orphanet XML data files and merge them into a single dataset."""
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the OrphanetProcessor.
        
        Args:
            output_dir: Directory for output files. Defaults to current directory.
        """
        self.logger = setup_logger(__name__)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def parse_xml(self, file_path: Union[str, Path]) -> ET.Element:
        """Parse XML file and return root element."""
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except Exception as e:
            raise OrphanetProcessorError(f"Failed to parse XML file: {e}")
            
            
    def get_disorder_data(self, disorder: ET.Element) -> dict:
        """extract disorders data: commun columns"""
        disorder_data = {
            "OrphaCode": safe_xml_find(disorder, "OrphaCode"),
            "ExpertLink": safe_xml_find(disorder, "ExpertLink"),
            "Name": safe_xml_find(disorder, "Name"),
            "DisorderType Name": safe_xml_find(disorder, "DisorderType/Name"),
            "DisorderGroup Name": safe_xml_find(disorder, "DisorderGroup/Name")
        }
        return disorder_data
    
    
    def extract_phenotype_data(self, root: ET.Element, output_csv: str = None) -> pd.DataFrame:
        """Extract phenotype data from XML root."""
        data = []

        for disorder_set in root.findall(".//HPODisorderSetStatus"):
            disorder = disorder_set.find("Disorder")
            if disorder is None:
                continue

            disorder_data = self.get_disorder_data(disorder)

            hpo_list = disorder.find("HPODisorderAssociationList")
            if hpo_list is not None:
                disorder_data["HPODisorderAssociationList count"] = hpo_list.attrib.get("count", "0")
                hpo_associations = []
                for assoc in hpo_list.findall("HPODisorderAssociation")[:20]:  # Limit to 20
                    hpo_data = {
                        "HPOId": safe_xml_find(assoc, "HPO/HPOId"),
                        "HPOTerm": safe_xml_find(assoc, "HPO/HPOTerm"),
                        "HPOFrequency": safe_xml_find(assoc, "HPOFrequency/Name"),
                        "DiagnosticCriteria": safe_xml_find(assoc, "DiagnosticCriteria")
                    }
                    hpo_associations.append(hpo_data)
                disorder_data["HPODisorderAssociation"] = json.dumps(hpo_associations, ensure_ascii=False)

            data.append(disorder_data)
            df = pd.DataFrame(data)
        if output_csv: df.to_csv(output_csv, index=False, encoding="utf-8")            
        return df



    def extract_consequences_data(self,root: ET.Element, output_csv: str = None) -> pd.DataFrame:
        """Extract functional consequences data from XML root."""
        data = []

        for disorder_relevance in root.findall(".//DisorderDisabilityRelevance"):
            disorder = disorder_relevance.find("Disorder")
            if disorder is None:
                continue

            disorder_data = self.get_disorder_data(disorder)

            disability_list = disorder.find("DisabilityDisorderAssociationList")
            if disability_list:
                disorder_data["DisabilityDisorderAssociationList count"] = disability_list.attrib.get("count", "0")
                disabilities = []

                for disability_assoc in disability_list.findall("DisabilityDisorderAssociation"):
                    disability_data = {
                        "Disability": safe_xml_find(disability_assoc, "Disability/Name"),
                        "FrequencyDisability": safe_xml_find(disability_assoc, "FrequenceDisability/Name"),
                        "TemporalityDisability": safe_xml_find(disability_assoc, "TemporalityDisability/Name"),
                        "SeverityDisability": safe_xml_find(disability_assoc, "SeverityDisability/Name"),
                        "LossOfAbility": safe_xml_find(disability_assoc, "LossOfAbility"),
                        "TypeDisability": safe_xml_find(disability_assoc, "Type"),
                        "Defined": safe_xml_find(disability_assoc, "Defined")
                    }
                    disabilities.append(disability_data)
                disorder_data["DisabilityDisorderAssociations"] = json.dumps(disabilities, ensure_ascii=False)
            data.append(disorder_data)
            df = pd.DataFrame(data)
        if output_csv: df.to_csv(output_csv, index=False, encoding="utf-8")            
        return df




    def extract_natural_history_and_age_data(self,root: ET.Element, output_csv: str = None) -> pd.DataFrame:
        """Extract natural history and age of onset data from XML root."""
        data = []

        for disorder in root.findall(".//Disorder"):
            disorder_data = self.get_disorder_data(disorder)

            age_list = disorder.find("AverageAgeOfOnsetList")
            if age_list:
                disorder_data["AverageAgeOfOnsetList count"] = age_list.attrib.get("count", "0")
                ages = []
                for age in age_list.findall("AverageAgeOfOnset"):
                    ages_data = {
                        'AverageAgeOfOnset' : safe_xml_find(age, "Name")
                    }
                    ages.append(ages_data)
                disorder_data["AverageAgesOfOnset"] = json.dumps(ages, ensure_ascii=False)

            inheritance_list = disorder.find("TypeOfInheritanceList")
            if inheritance_list:
                inhs = []
                disorder_data["TypeOfInheritanceList count"] = inheritance_list.attrib.get("count", "0")
                for inh in inheritance_list.findall("TypeOfInheritance"): 
                    inheritances_data = {
                        'TypeOfInheritance' : safe_xml_find(inh, "Name")
                    } 
                    inhs.append(inheritances_data)
                    
                disorder_data["TypesOfInheritance"] = json.dumps(inhs, ensure_ascii=False)

            data.append(disorder_data)
            df = pd.DataFrame(data)
        if output_csv: df.to_csv(output_csv, index=False, encoding="utf-8")            
        return df          


    def extract_references_data(self, root: ET.Element, output_csv: str = None) -> pd.DataFrame:
        """Extract reference data from XML root."""
        data = []

        for disorder in root.findall(".//Disorder"):
            disorder_data = self.get_disorder_data(disorder)

            ext_ref_list = disorder.find("ExternalReferenceList")
            if ext_ref_list:
                disorder_data["ExternalReferenceList count"] = ext_ref_list.attrib.get("count", "0")
                external_refs = {}
                for ref in ext_ref_list.findall("ExternalReference"):
                    external_refs[safe_xml_find(ref, "Source")] = safe_xml_find(ref, "Reference")
                disorder_data["ExternalReferences"] = json.dumps(external_refs, ensure_ascii=False)


            summary_list = disorder.find("SummaryInformationList")
            if summary_list:
                summary_info = {}
                for summary in summary_list.findall(".//TextSection"):
                     summary_info[safe_xml_find(summary, "TextSectionType/Name")] = safe_xml_find(summary,"Contents")       
                disorder_data["SummaryInformation"] = json.dumps(summary_info, ensure_ascii=False)
            data.append(disorder_data)
            df = pd.DataFrame(data)
        if output_csv: df.to_csv(output_csv, index=False, encoding="utf-8")            
        return df



    def extract_epidemiology_data(self, root: ET.Element, output_csv: str = None) -> pd.DataFrame:
        """Extract epidemiology data from XML root."""
        data = []

        for disorder in root.findall(".//Disorder"):
            disorder_data = self.get_disorder_data(disorder)

            prevalence_list = disorder.find("PrevalenceList")
            if prevalence_list:
                disorder_data["PrevalenceList count"] = prevalence_list.attrib.get("count", "0")
                prevalences = []
                for prev in prevalence_list.findall("Prevalence"):
                    prevalence_data = {
                        "Source": safe_xml_find(prev, "Source"),
                        "PrevalenceType": safe_xml_find(prev, "PrevalenceType/Name"),
                        "PrevalenceQualification": safe_xml_find(prev, "PrevalenceQualification/Name"),
                        "PrevalenceClass": safe_xml_find(prev, "PrevalenceClass/Name"),
                        "ValMoy": safe_xml_find(prev, "ValMoy"),
                        "PrevalenceGeographic": safe_xml_find(prev, "PrevalenceGeographic/Name"),
                        "PrevalenceValidationStatus": safe_xml_find(prev, "PrevalenceValidationStatus/Name")
                    }
                    prevalences.append(prevalence_data)
                disorder_data["PrevalenceData"] = json.dumps(prevalences, ensure_ascii=False)

            data.append(disorder_data)
            df = pd.DataFrame(data)
        if output_csv: df.to_csv(output_csv, index=False, encoding="utf-8")            
        return df
    def merge_datasets(
        self,
        dataframes: List[pd.DataFrame],
        common_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Merge multiple datasets based on OrphaCode.
        
        Args:
            dataframes: List of dataframes to merge
            common_columns: List of columns that should not be renamed with suffixes
        """
        if not dataframes:
            raise OrphanetProcessorError("No dataframes provided for merging")
            
        common_columns = common_columns or [
            "ExpertLink", "Name", "DisorderType Name", "DisorderGroup Name"
        ]
        
        # Process each dataframe
        processed_dfs = [
            process_dataframe(df, i, common_columns)
            for i, df in enumerate(dataframes)
        ]
        
        # Merge dataframes
        merged_df = processed_dfs[0]
        for df in processed_dfs[1:]:
            merged_df = merged_df.merge(df, on="OrphaCode", how="outer")
            
        # Handle common columns
        for col in common_columns:
            duplicate_cols = [
                c for c in merged_df.columns
                if c.startswith(col + "_df")
            ]
            if duplicate_cols:
                merged_df[col] = merged_df[duplicate_cols].bfill(axis=1).iloc[:, 0]
                merged_df.drop(columns=duplicate_cols, inplace=True)
                
        return merged_df

    def process_files(
        self,
        xml_files: Dict[str, Union[str, Path]],
        output_file: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Process multiple XML files and merge their data.
        
        Args:
            xml_files: Dictionary mapping file types to file paths
            output_file: Path to save merged dataset (optional)
            
        Returns:
            Merged DataFrame
        """
        dataframes = []
        
        for file_type, file_path in xml_files.items():
            self.logger.info(f"Processing {file_type} file: {file_path}")
            root = self.parse_xml(file_path)
            
            if "phenotype" in file_type:
                df = self.extract_phenotype_data(root)
            if "references" in file_type:
                df = self.extract_references_data(root)
            if "consequences" in file_type:
                df = self.extract_consequences_data(root)
            if "natural_history" in file_type:
                df = self.extract_natural_history_and_age_data(root)
            if "epidimiology" in file_type:
                df = self.extract_epidemiology_data(root)
            dataframes.append(df)
            
        merged_df = self.merge_datasets(dataframes)
        
        if output_file:
            output_path = self.output_dir / output_file
            merged_df.to_csv(output_path, index=False, encoding="utf-8")
            self.logger.info(f"Merged data saved to {output_path}")
            
        return merged_df
