"""Team configuration sharing utilities for Meno.

This module provides utilities for creating, sharing, and managing team-specific
configurations for Meno workflows. Team configurations allow sharing domain-specific
knowledge like:

1. Acronym dictionaries specific to an industry or organization
2. Common misspellings in domain-specific text
3. Standard preprocessing settings for text data
4. Preferred models and visualization settings

These configurations can be version-controlled and shared across teams.
"""

from typing import Dict, List, Optional, Union, Any, Set
import os
import yaml
from pathlib import Path
import logging
import json
import hashlib
from datetime import datetime
from ..utils.config import (
    WorkflowMenoConfig, 
    load_config,
    save_config,
    merge_configs
)

logger = logging.getLogger(__name__)


def create_team_config(
    team_name: str,
    acronyms: Optional[Dict[str, str]] = None,
    spelling_corrections: Optional[Dict[str, str]] = None,
    model_settings: Optional[Dict[str, Any]] = None,
    visualization_settings: Optional[Dict[str, Any]] = None,
    base_config_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> WorkflowMenoConfig:
    """Create a new team configuration file.
    
    Parameters
    ----------
    team_name : str
        Name of the team or domain (e.g., "insurance", "healthcare", "finance")
    acronyms : Optional[Dict[str, str]], optional
        Dictionary of domain-specific acronyms, by default None
    spelling_corrections : Optional[Dict[str, str]], optional
        Dictionary of domain-specific spelling corrections, by default None
    model_settings : Optional[Dict[str, Any]], optional
        Dictionary of model settings overrides, by default None
    visualization_settings : Optional[Dict[str, Any]], optional
        Dictionary of visualization settings overrides, by default None
    base_config_path : Optional[Union[str, Path]], optional
        Path to base configuration file to extend, by default None
    output_path : Optional[Union[str, Path]], optional
        Path to save the configuration, by default None
        If None, saves to "{team_name}_config.yaml" in the current directory

    Returns
    -------
    WorkflowMenoConfig
        The created team configuration
    """
    # Load base configuration
    config = load_config(config_path=base_config_path, config_type="workflow")
    
    # Add team information
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    config_dict = config.dict()
    if "metadata" not in config_dict:
        config_dict["metadata"] = {}
    
    config_dict["metadata"]["team_name"] = team_name
    config_dict["metadata"]["created"] = timestamp
    config_dict["metadata"]["last_modified"] = timestamp
    
    # Add acronyms if provided
    if acronyms:
        if "custom_mappings" not in config_dict["preprocessing"]["acronyms"]:
            config_dict["preprocessing"]["acronyms"]["custom_mappings"] = {}
        
        config_dict["preprocessing"]["acronyms"]["custom_mappings"].update(acronyms)
    
    # Add spelling corrections if provided
    if spelling_corrections:
        if "custom_dictionary" not in config_dict["preprocessing"]["spelling"]:
            config_dict["preprocessing"]["spelling"]["custom_dictionary"] = {}
        
        config_dict["preprocessing"]["spelling"]["custom_dictionary"].update(spelling_corrections)
    
    # Add model settings if provided
    if model_settings:
        # Create a deep update function
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v
        
        deep_update(config_dict["modeling"], model_settings)
    
    # Add visualization settings if provided
    if visualization_settings:
        deep_update(config_dict["visualization"], visualization_settings)
    
    # Create a new config object from the updated dictionary
    new_config = WorkflowMenoConfig(**config_dict)
    
    # Save to file if output_path is provided
    if output_path is None:
        sanitized_team_name = team_name.lower().replace(" ", "_")
        output_path = f"{sanitized_team_name}_config.yaml"
    
    save_config(new_config, output_path)
    logger.info(f"Team configuration for '{team_name}' saved to {output_path}")
    
    return new_config


def update_team_config(
    config_path: Union[str, Path],
    acronyms: Optional[Dict[str, str]] = None,
    spelling_corrections: Optional[Dict[str, str]] = None,
    model_settings: Optional[Dict[str, Any]] = None,
    visualization_settings: Optional[Dict[str, Any]] = None,
    merge_mode: str = "update",
) -> WorkflowMenoConfig:
    """Update an existing team configuration.
    
    Parameters
    ----------
    config_path : Union[str, Path]
        Path to the team configuration file
    acronyms : Optional[Dict[str, str]], optional
        Dictionary of domain-specific acronyms to add or update, by default None
    spelling_corrections : Optional[Dict[str, str]], optional
        Dictionary of spelling corrections to add or update, by default None
    model_settings : Optional[Dict[str, Any]], optional
        Dictionary of model settings to update, by default None
    visualization_settings : Optional[Dict[str, Any]], optional
        Dictionary of visualization settings to update, by default None
    merge_mode : str, optional
        How to merge the dictionaries, by default "update"
        Options: "update" (add new entries and update existing), 
                "replace" (replace entire dictionaries)
    
    Returns
    -------
    WorkflowMenoConfig
        The updated team configuration
    """
    # Load existing configuration
    config = load_config(config_path=config_path, config_type="workflow")
    config_dict = config.dict()
    
    # Update metadata
    if "metadata" not in config_dict:
        config_dict["metadata"] = {}
    config_dict["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Update acronyms
    if acronyms:
        if merge_mode == "replace":
            config_dict["preprocessing"]["acronyms"]["custom_mappings"] = acronyms
        else:
            if "custom_mappings" not in config_dict["preprocessing"]["acronyms"]:
                config_dict["preprocessing"]["acronyms"]["custom_mappings"] = {}
            config_dict["preprocessing"]["acronyms"]["custom_mappings"].update(acronyms)
    
    # Update spelling corrections
    if spelling_corrections:
        if merge_mode == "replace":
            config_dict["preprocessing"]["spelling"]["custom_dictionary"] = spelling_corrections
        else:
            if "custom_dictionary" not in config_dict["preprocessing"]["spelling"]:
                config_dict["preprocessing"]["spelling"]["custom_dictionary"] = {}
            config_dict["preprocessing"]["spelling"]["custom_dictionary"].update(spelling_corrections)
    
    # Update model settings
    if model_settings:
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v
        
        if merge_mode == "replace" and "modeling" in config_dict:
            config_dict["modeling"] = model_settings
        else:
            deep_update(config_dict["modeling"], model_settings)
    
    # Update visualization settings
    if visualization_settings:
        if merge_mode == "replace" and "visualization" in config_dict:
            config_dict["visualization"] = visualization_settings
        else:
            deep_update(config_dict["visualization"], visualization_settings)
    
    # Create new config and save to file
    updated_config = WorkflowMenoConfig(**config_dict)
    save_config(updated_config, config_path)
    logger.info(f"Team configuration updated at {config_path}")
    
    return updated_config


def merge_team_configs(
    configs: List[Union[str, Path, WorkflowMenoConfig]],
    output_path: Optional[Union[str, Path]] = None,
    team_name: Optional[str] = None,
) -> WorkflowMenoConfig:
    """Merge multiple team configurations.
    
    This is useful for combining domain knowledge from different teams or domains.
    In case of conflicts, later configs in the list take precedence.
    
    Parameters
    ----------
    configs : List[Union[str, Path, WorkflowMenoConfig]]
        List of config paths or config objects to merge
    output_path : Optional[Union[str, Path]], optional
        Path to save the merged configuration, by default None
    team_name : Optional[str], optional
        Name for the merged team configuration, by default None
    
    Returns
    -------
    WorkflowMenoConfig
        The merged team configuration
    """
    if not configs:
        raise ValueError("No configurations provided for merging")
    
    # Load all configs
    config_objects = []
    for config in configs:
        if isinstance(config, (str, Path)):
            config_obj = load_config(config_path=config, config_type="workflow")
        else:
            config_obj = config
        config_objects.append(config_obj)
    
    # Start with the first config
    base_config = config_objects[0]
    
    # Create a new merged config iteratively
    merged_config_dict = base_config.dict()
    
    # Initialize dictionaries if they don't exist
    if "metadata" not in merged_config_dict:
        merged_config_dict["metadata"] = {}
    if "custom_mappings" not in merged_config_dict["preprocessing"]["acronyms"]:
        merged_config_dict["preprocessing"]["acronyms"]["custom_mappings"] = {}
    if "custom_dictionary" not in merged_config_dict["preprocessing"]["spelling"]:
        merged_config_dict["preprocessing"]["spelling"]["custom_dictionary"] = {}
    
    # Track source teams for each entry
    acronym_sources = {}
    spelling_sources = {}
    
    # Get initial team name if available
    if "team_name" in merged_config_dict["metadata"]:
        initial_team = merged_config_dict["metadata"]["team_name"]
        for acronym in merged_config_dict["preprocessing"]["acronyms"]["custom_mappings"]:
            acronym_sources[acronym] = initial_team
        for word in merged_config_dict["preprocessing"]["spelling"]["custom_dictionary"]:
            spelling_sources[word] = initial_team
    
    # Merge with subsequent configs
    for i, config in enumerate(config_objects[1:], 1):
        config_dict = config.dict()
        
        # Get team name for attribution
        source_team = config_dict.get("metadata", {}).get("team_name", f"Config_{i}")
        
        # Merge acronyms
        if "custom_mappings" in config_dict["preprocessing"]["acronyms"]:
            source_acronyms = config_dict["preprocessing"]["acronyms"]["custom_mappings"]
            merged_config_dict["preprocessing"]["acronyms"]["custom_mappings"].update(source_acronyms)
            
            # Update sources
            for acronym in source_acronyms:
                acronym_sources[acronym] = source_team
        
        # Merge spelling corrections
        if "custom_dictionary" in config_dict["preprocessing"]["spelling"]:
            source_spellings = config_dict["preprocessing"]["spelling"]["custom_dictionary"]
            merged_config_dict["preprocessing"]["spelling"]["custom_dictionary"].update(source_spellings)
            
            # Update sources
            for word in source_spellings:
                spelling_sources[word] = source_team
        
        # Merge model settings (shallow merge for now)
        for key, value in config_dict["modeling"].items():
            if isinstance(value, dict) and key in merged_config_dict["modeling"] and isinstance(merged_config_dict["modeling"][key], dict):
                merged_config_dict["modeling"][key].update(value)
            else:
                merged_config_dict["modeling"][key] = value
        
        # Merge visualization settings (shallow merge for now)
        for key, value in config_dict["visualization"].items():
            if isinstance(value, dict) and key in merged_config_dict["visualization"] and isinstance(merged_config_dict["visualization"][key], dict):
                merged_config_dict["visualization"][key].update(value)
            else:
                merged_config_dict["visualization"][key] = value
    
    # Update metadata
    if team_name:
        merged_config_dict["metadata"]["team_name"] = team_name
    else:
        merged_config_dict["metadata"]["team_name"] = "Merged Team Config"
    
    merged_config_dict["metadata"]["created"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    merged_config_dict["metadata"]["last_modified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    merged_config_dict["metadata"]["source_configs"] = [
        config_dict.get("metadata", {}).get("team_name", f"Config_{i}") 
        for i, config_dict in enumerate([c.dict() for c in config_objects])
    ]
    
    # Add attribution information
    merged_config_dict["metadata"]["acronym_sources"] = acronym_sources
    merged_config_dict["metadata"]["spelling_sources"] = spelling_sources
    
    # Create new config object
    merged_config = WorkflowMenoConfig(**merged_config_dict)
    
    # Save to file if output_path is provided
    if output_path:
        save_config(merged_config, output_path)
        logger.info(f"Merged configuration saved to {output_path}")
    
    return merged_config


def get_team_config_stats(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Get statistics about a team configuration.
    
    Parameters
    ----------
    config_path : Union[str, Path]
        Path to the team configuration file
    
    Returns
    -------
    Dict[str, Any]
        Dictionary of statistics about the configuration
    """
    config = load_config(config_path=config_path, config_type="workflow")
    config_dict = config.dict()
    
    # Get metadata
    metadata = config_dict.get("metadata", {})
    team_name = metadata.get("team_name", "Unknown")
    created = metadata.get("created", "Unknown")
    last_modified = metadata.get("last_modified", "Unknown")
    
    # Count acronyms
    acronyms = config_dict.get("preprocessing", {}).get("acronyms", {}).get("custom_mappings", {})
    acronym_count = len(acronyms)
    
    # Count spelling corrections
    spellings = config_dict.get("preprocessing", {}).get("spelling", {}).get("custom_dictionary", {})
    spelling_count = len(spellings)
    
    # Get model settings
    model_settings = config_dict.get("modeling", {})
    model_name = model_settings.get("embeddings", {}).get("model_name", "Unknown")
    default_method = model_settings.get("default_method", "Unknown")
    
    # Calculate a configuration hash for version comparison
    config_str = json.dumps(config_dict, sort_keys=True)
    config_hash = hashlib.md5(config_str.encode()).hexdigest()
    
    # Compile statistics
    stats = {
        "team_name": team_name,
        "created": created,
        "last_modified": last_modified,
        "acronym_count": acronym_count,
        "spelling_correction_count": spelling_count,
        "default_model": model_name,
        "default_method": default_method,
        "config_hash": config_hash
    }
    
    return stats


def compare_team_configs(
    config1_path: Union[str, Path],
    config2_path: Union[str, Path]
) -> Dict[str, Any]:
    """Compare two team configurations and identify differences.
    
    Parameters
    ----------
    config1_path : Union[str, Path]
        Path to the first team configuration file
    config2_path : Union[str, Path]
        Path to the second team configuration file
    
    Returns
    -------
    Dict[str, Any]
        Dictionary of differences between the configurations
    """
    config1 = load_config(config_path=config1_path, config_type="workflow")
    config2 = load_config(config_path=config2_path, config_type="workflow")
    
    config1_dict = config1.dict()
    config2_dict = config2.dict()
    
    # Get team names
    team1 = config1_dict.get("metadata", {}).get("team_name", "Config 1")
    team2 = config2_dict.get("metadata", {}).get("team_name", "Config 2")
    
    # Compare acronyms
    acronyms1 = set(config1_dict.get("preprocessing", {}).get("acronyms", {}).get("custom_mappings", {}).keys())
    acronyms2 = set(config2_dict.get("preprocessing", {}).get("acronyms", {}).get("custom_mappings", {}).keys())
    
    common_acronyms = acronyms1.intersection(acronyms2)
    unique_to_1 = acronyms1 - acronyms2
    unique_to_2 = acronyms2 - acronyms1
    
    # Check for acronyms with different expansions
    differing_acronyms = {}
    for acronym in common_acronyms:
        expansion1 = config1_dict["preprocessing"]["acronyms"]["custom_mappings"][acronym]
        expansion2 = config2_dict["preprocessing"]["acronyms"]["custom_mappings"][acronym]
        if expansion1 != expansion2:
            differing_acronyms[acronym] = {
                team1: expansion1,
                team2: expansion2
            }
    
    # Compare spelling corrections
    spellings1 = set(config1_dict.get("preprocessing", {}).get("spelling", {}).get("custom_dictionary", {}).keys())
    spellings2 = set(config2_dict.get("preprocessing", {}).get("spelling", {}).get("custom_dictionary", {}).keys())
    
    common_spellings = spellings1.intersection(spellings2)
    unique_spellings_to_1 = spellings1 - spellings2
    unique_spellings_to_2 = spellings2 - spellings1
    
    # Check for spellings with different corrections
    differing_spellings = {}
    for word in common_spellings:
        correction1 = config1_dict["preprocessing"]["spelling"]["custom_dictionary"][word]
        correction2 = config2_dict["preprocessing"]["spelling"]["custom_dictionary"][word]
        if correction1 != correction2:
            differing_spellings[word] = {
                team1: correction1,
                team2: correction2
            }
    
    # Compare model settings
    model_name1 = config1_dict.get("modeling", {}).get("embeddings", {}).get("model_name", "Unknown")
    model_name2 = config2_dict.get("modeling", {}).get("embeddings", {}).get("model_name", "Unknown")
    
    same_model = model_name1 == model_name2
    
    # Compile comparison
    comparison = {
        "team_names": {
            "config1": team1,
            "config2": team2
        },
        "acronyms": {
            "common_count": len(common_acronyms),
            "unique_to_config1": list(unique_to_1),
            "unique_to_config2": list(unique_to_2),
            "differing_expansions": differing_acronyms
        },
        "spelling_corrections": {
            "common_count": len(common_spellings),
            "unique_to_config1": list(unique_spellings_to_1),
            "unique_to_config2": list(unique_spellings_to_2),
            "differing_corrections": differing_spellings
        },
        "models": {
            "same_model": same_model,
            "config1_model": model_name1,
            "config2_model": model_name2
        }
    }
    
    return comparison


def export_team_acronyms(
    config_path: Union[str, Path],
    output_format: str = "json",
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, str]:
    """Export acronyms from a team configuration.
    
    Parameters
    ----------
    config_path : Union[str, Path]
        Path to the team configuration file
    output_format : str, optional
        Format to export ("json", "yaml", or "dict"), by default "json"
    output_path : Optional[Union[str, Path]], optional
        Path to save the exported acronyms, by default None
    
    Returns
    -------
    Dict[str, str]
        Dictionary of acronyms and their expansions
    """
    config = load_config(config_path=config_path, config_type="workflow")
    acronyms = config.preprocessing.acronyms.custom_mappings
    
    if output_path is not None:
        if output_format == "json":
            with open(output_path, 'w') as f:
                json.dump(acronyms, f, indent=2)
        elif output_format == "yaml":
            with open(output_path, 'w') as f:
                yaml.dump(acronyms, f, default_flow_style=False)
        else:
            logger.warning(f"Unsupported export format: {output_format}. Returning dictionary only.")
    
    return acronyms


def export_team_spelling_corrections(
    config_path: Union[str, Path],
    output_format: str = "json",
    output_path: Optional[Union[str, Path]] = None
) -> Dict[str, str]:
    """Export spelling corrections from a team configuration.
    
    Parameters
    ----------
    config_path : Union[str, Path]
        Path to the team configuration file
    output_format : str, optional
        Format to export ("json", "yaml", or "dict"), by default "json"
    output_path : Optional[Union[str, Path]], optional
        Path to save the exported spelling corrections, by default None
    
    Returns
    -------
    Dict[str, str]
        Dictionary of misspelled words and their corrections
    """
    config = load_config(config_path=config_path, config_type="workflow")
    corrections = config.preprocessing.spelling.custom_dictionary
    
    if output_path is not None:
        if output_format == "json":
            with open(output_path, 'w') as f:
                json.dump(corrections, f, indent=2)
        elif output_format == "yaml":
            with open(output_path, 'w') as f:
                yaml.dump(corrections, f, default_flow_style=False)
        else:
            logger.warning(f"Unsupported export format: {output_format}. Returning dictionary only.")
    
    return corrections


def import_acronyms_from_file(
    file_path: Union[str, Path],
    file_format: Optional[str] = None
) -> Dict[str, str]:
    """Import acronyms from a file.
    
    Parameters
    ----------
    file_path : Union[str, Path]
        Path to the file containing acronyms
    file_format : Optional[str], optional
        Format of the file ("json", "yaml", or None to infer from extension), by default None
    
    Returns
    -------
    Dict[str, str]
        Dictionary of acronyms and their expansions
    """
    # Infer format from file extension if not provided
    if file_format is None:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.json', '.js']:
            file_format = 'json'
        elif ext in ['.yaml', '.yml']:
            file_format = 'yaml'
        else:
            raise ValueError(f"Could not infer file format from extension: {ext}")
    
    # Load the file
    with open(file_path, 'r') as f:
        if file_format == 'json':
            acronyms = json.load(f)
        elif file_format == 'yaml':
            acronyms = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    return acronyms


def import_spelling_corrections_from_file(
    file_path: Union[str, Path],
    file_format: Optional[str] = None
) -> Dict[str, str]:
    """Import spelling corrections from a file.
    
    Parameters
    ----------
    file_path : Union[str, Path]
        Path to the file containing spelling corrections
    file_format : Optional[str], optional
        Format of the file ("json", "yaml", or None to infer from extension), by default None
    
    Returns
    -------
    Dict[str, str]
        Dictionary of misspelled words and their corrections
    """
    # Infer format from file extension if not provided
    if file_format is None:
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.json', '.js']:
            file_format = 'json'
        elif ext in ['.yaml', '.yml']:
            file_format = 'yaml'
        else:
            raise ValueError(f"Could not infer file format from extension: {ext}")
    
    # Load the file
    with open(file_path, 'r') as f:
        if file_format == 'json':
            corrections = json.load(f)
        elif file_format == 'yaml':
            corrections = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    return corrections