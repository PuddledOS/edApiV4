from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class OrganicScan(BaseModel):
    """Individual organic scan event"""
    timestamp: Optional[str] = None
    scan_type: str  # "Analyse" or "Log"
    genus: str
    species: str
    variant: Optional[str] = None
    system_name: Optional[str] = None
    system_address: Optional[int] = None
    body_name: Optional[str] = None
    body_id: Optional[int] = None
    was_logged: bool = False  # True if already logged by another commander


class OrganicSummary(BaseModel):
    """Summary of organic scans"""
    total_analyse_scans: int = 0
    total_log_scans: int = 0
    unique_species: int = 0
    unique_genus: int = 0
    first_discoveries: int = 0


class SystemOrganics(BaseModel):
    """Organic scans for a specific system"""
    system_name: str
    system_address: Optional[int] = None
    total_analyse_scans: int = 0
    total_log_scans: int = 0
    unique_species: int = 0
    unique_genus: int = 0
    first_discoveries: int = 0
    bodies: Dict[str, Dict[str, List[OrganicScan]]] = Field(
        default_factory=dict,
        description="Scans grouped by body name, then by scan type (analyse/log)"
    )
    all_scans: List[OrganicScan] = Field(default_factory=list)


class OrganicStats(BaseModel):
    """Comprehensive organic scan statistics"""
    total_analyse_scans: int = 0
    total_log_scans: int = 0
    first_discoveries: int = 0
    unique_genus: int = 0
    unique_species: int = 0
    unique_variants: int = 0
    systems_with_organics: int = 0
    bodies_with_organics: int = 0
    most_common_genus: str = "None"
    most_common_species: str = "None"
    genus_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of scans per genus"
    )
    species_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of scans per species"
    )


class GenusDistribution(BaseModel):
    """Distribution data for a specific genus"""
    genus: str
    total_scans: int = 0
    unique_species: int = 0
    species_list: List[str] = Field(default_factory=list)
    first_discoveries: int = 0