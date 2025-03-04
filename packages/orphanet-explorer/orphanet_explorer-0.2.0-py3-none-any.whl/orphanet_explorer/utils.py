import logging
from typing import Any, Dict, List
import xml.etree.ElementTree as ET
import pandas as pd

def setup_logger(name: str) -> logging.Logger:
    """Set up and return a logger with the given name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

def safe_xml_find(
    element: ET.Element,
    path: str,
    default: str = "N/A"
) -> str:
    """Safely find and return text from XML element."""
    found = element.findtext(path)
    return found if found is not None else default

def process_dataframe(
    df: pd.DataFrame,
    index: int,
    common_columns: List[str]
) -> pd.DataFrame:
    """Process a dataframe for merging."""
    df = df.copy()
    df.reset_index(drop=True, inplace=True)
    df["OrphaCode"] = df["OrphaCode"].astype(str)
    df.drop_duplicates(subset=["OrphaCode"], keep="first", inplace=True)
    
    # Rename columns except OrphaCode and common columns
    df.columns = [col if col == "OrphaCode" else f"{col}_df{index+1}" for col in df.columns]
    return df

def save_to_csv(
    df: pd.DataFrame,
    output_file: str,
):
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\n✅ Data saved to {output_file}")