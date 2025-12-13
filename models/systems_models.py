from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScanBody(BaseModel):
    """Individual body scan data"""
    BodyName: Optional[str] = None
    BodyID: Optional[int] = None
    BodyType: str  # "Star" or "Planet"
    StarSystem: Optional[str] = None
    SystemAddress: Optional[int] = None
    DistanceFromArrivalLS: float = 0
    WasDiscovered: bool = True
    WasMapped: bool = True
    WasFootfalled: Optional[bool] = None
    PlanetClass: Optional[str] = None
    TerraformState: Optional[str] = None
    Atmosphere: Optional[str] = None
    Landable: Optional[bool] = None
    MassEM: Optional[float] = None
    SurfaceTemperature: Optional[float] = None
    StarType: Optional[str] = None
    StellarMass: Optional[float] = None


class SystemScanSummary(BaseModel):
    """Summary of system scan data"""
    SystemName: str
    SystemAddress: Optional[int] = None
    TotalBodies: int = 0
    ScannedBodies: int = 0
    FirstDiscoveries: int = 0
    FirstMapped: int = 0
    FirstFootfall: int = 0
    Stars: int = 0
    Planets: int = 0
    LandableBodies: int = 0
    TerraformableBodies: int = 0
    planet_types: Dict[str, int] = Field(default_factory=dict)
    star_types: Dict[str, int] = Field(default_factory=dict)


class DiscoveryStatus(BaseModel):
    """Discovery status for a body"""
    name: Optional[str] = None
    first_discovered: bool = False
    first_mapped: bool = False
    first_footfall: bool = False
    scan_type: str = "Unknown"
    timestamp: Optional[str] = None


class ExplorationStats(BaseModel):
    """Overall exploration statistics"""
    total_systems_visited: int = 0
    total_bodies_scanned: int = 0
    first_discoveries: int = 0
    first_mapped: int = 0
    first_footfall: int = 0
    most_common_planet_type: str = "None"
    most_common_star_type: str = "None"
    landable_bodies_found: int = 0
    terraformable_bodies_found: int = 0


class FirstDiscoveryBody(BaseModel):
    """Detailed body information for first discovery report"""
    body_name: Optional[str] = None
    body_id: Optional[int] = None
    body_type: str  # "Star", "Planet", or "Moon"
    scan_type: str = "Unknown"
    timestamp: Optional[str] = None
    distance_ls: float = 0

    # Discovery status
    first_discovered: bool = False
    first_mapped: bool = False
    first_footfall: bool = False

    # Planet properties
    planet_class: Optional[str] = None
    atmosphere: Optional[str] = None
    volcanism: Optional[str] = None
    landable: Optional[bool] = None
    terraform_state: Optional[str] = None
    mass_em: Optional[float] = None
    radius: Optional[float] = None
    surface_gravity: Optional[float] = None
    surface_temp: Optional[float] = None
    surface_pressure: Optional[float] = None

    # Star properties
    star_type: Optional[str] = None
    star_class: Optional[int] = None
    stellar_mass: Optional[float] = None
    luminosity: Optional[str] = None
    age_my: Optional[int] = None

    # Additional features
    has_rings: bool = False
    ring_count: int = 0
    signals: Optional[List[str]] = None
    materials: Optional[List[Dict[str, Any]]] = None


class FirstDiscoverySystem(BaseModel):
    """System information for first discovery report"""
    system_name: str
    system_address: int
    visit_timestamp: str
    total_bodies: int = 0
    bodies_scanned: int = 0

    # Discovery counts
    first_discoveries_count: int = 0
    first_mapped_count: int = 0
    first_footfall_count: int = 0

    # Body counts
    star_count: int = 0
    planet_count: int = 0
    landable_count: int = 0
    terraformable_count: int = 0

    # Valuable finds flags
    has_earth_like: bool = False
    has_water_world: bool = False
    has_ammonia_world: bool = False

    # Body lists
    stars: List[FirstDiscoveryBody] = Field(default_factory=list)
    planets: List[FirstDiscoveryBody] = Field(default_factory=list)
    moons: List[FirstDiscoveryBody] = Field(default_factory=list)

    # Type breakdowns
    planet_type_breakdown: Dict[str, int] = Field(default_factory=dict)
    star_type_breakdown: Dict[str, int] = Field(default_factory=dict)


class FirstDiscoveryReport(BaseModel):
    """Comprehensive first discovery report"""
    generated_at: str
    scan_date_range: Dict[str, str]  # {'start': timestamp, 'end': timestamp}

    # Overall statistics
    total_systems: int = 0
    total_first_discoveries: int = 0
    total_first_mapped: int = 0
    total_first_footfall: int = 0

    # Valuable body counts
    earth_like_count: int = 0
    water_world_count: int = 0
    ammonia_world_count: int = 0
    terraformable_count: int = 0

    # System list
    systems: List[FirstDiscoverySystem] = Field(default_factory=list)