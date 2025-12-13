from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CarrierCrewMember(BaseModel):
    """Individual crew member on carrier."""
    CrewRole: str                    # e.g., "Captain", "Refuel", "Commodities"
    Activated: bool                  # Whether the service is active
    Enabled: Optional[bool] = None   # Whether the service is enabled
    CrewName: Optional[str] = None   # Name of crew member (if activated)

class CarrierSpaceUsage(BaseModel):
    """Carrier space usage statistics."""
    TotalCapacity: int          # Total carrier capacity (usually 25000)
    Crew: int                   # Space used by crew
    Cargo: int                  # Space used by cargo
    CargoSpaceReserved: int     # Reserved cargo space
    ShipPacks: int              # Space used by ships
    ModulePacks: int            # Space used by modules
    FreeSpace: int              # Available free space

class CarrierFinance(BaseModel):
    """Carrier financial information."""
    CarrierBalance: int              # Total carrier balance
    ReserveBalance: int              # Reserved balance (for upkeep)
    AvailableBalance: int            # Available to spend
    ReservePercent: int              # Percentage in reserve
    TaxRate_refuel: Optional[int] = None    # Refuel tax rate %
    TaxRate_repair: Optional[int] = None    # Repair tax rate %
    TaxRate_rearm: Optional[int] = None     # Rearm tax rate %

class CarrierStatsResponse(BaseModel):
    """Response for carrier statistics - GET /carrier/stats"""
    CarrierID: int                   # Unique carrier ID
    CarrierType: str                 # Type (usually "FleetCarrier")
    Callsign: str                    # Carrier callsign (e.g., "X6J-G5V")
    Name: str                        # Carrier name
    DockingAccess: str               # Docking access level ("all", "friends", "squadron")
    AllowNotorious: bool             # Whether notorious commanders can dock
    FuelLevel: int                   # Current fuel level
    JumpRangeCurr: float             # Current jump range in ly
    JumpRangeMax: float              # Maximum jump range in ly
    PendingDecommission: bool        # Whether carrier is being decommissioned
    SpaceUsage: CarrierSpaceUsage    # Nested space usage object
    Finance: CarrierFinance          # Nested finance object
    Crew: List[CarrierCrewMember]    # List of all crew members
    ShipPacks: List[Any]             # List of ship packs (usually empty)
    ModulePacks: List[Any]           # List of module packs (usually empty)

class CarrierJumpRequestResponse(BaseModel):
    """Response for carrier jump request - GET /carrier/jump-request"""
    CarrierType: str        # Type of carrier
    CarrierID: int          # Carrier ID
    SystemName: str         # Destination system name
    Body: str               # Destination body
    SystemAddress: int      # System address
    BodyID: int             # Body ID
    DepartureTime: str      # Scheduled departure time (ISO format)

class CarrierInfoResponse(BaseModel):
    """Combined carrier information - GET /carrier/info"""
    stats: Optional[CarrierStatsResponse] = None        # Full stats if available
    jump_request: Optional[CarrierJumpRequestResponse] = None  # Jump request if available
    timestamp: str                                       # Timestamp of data

class CarrierFuelResponse(BaseModel):
    """Carrier fuel information - GET /carrier/fuel"""
    fuel_level: int
    fuel_percentage: float
    jump_range_current: int
    jump_range_max: int
    carrier_id: int
    callsign: str

class CarrierBalanceResponse(BaseModel):
    """Carrier balance information - GET /carrier/balance"""
    carrier_balance: float
    reserve_balance: float
    available_balance: float
    reserve_percent: float
    carrier_name: str
    callsign: str

class CarrierCapacityResponse(BaseModel):
    """Carrier capacity information - GET /carrier/capacity"""
    total_capacity: int
    used_space: int
    free_space: int
    usage_percent: float
    cargo: int
    ship_packs: int
    module_packs: int
    crew: int
    cargo_reserved: float

class CarrierServicesResponse(BaseModel):
    carrier_name: str
    callsign: str
    services: Dict[Any, Any]

class CarrierCrewResponse(BaseModel):
    total_crew_slots: int
    active_crew: int
    inactive_crew: int
    crew_details: List[Any]
    active_services: List[Any]
