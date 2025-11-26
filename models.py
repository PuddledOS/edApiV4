from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StatusResponse(BaseModel):
    """Response for active status check."""
    Value: bool


class BalanceResponse(BaseModel):
    """Response for wealth/balance query."""
    Balance: str


class FlagsResponse(BaseModel):
    """Response for flags query."""
    flags: str
    flags2: str


class ScreenResponse(BaseModel):
    """Response for current screen/GUI focus."""
    Focus: str


class PipsResponse(BaseModel):
    """Response for power distribution (pips)."""
    Systems: float
    Engines: float
    Weapons: float


class FuelResponse(BaseModel):
    """Response for fuel information."""
    Capacity: float
    Level: float
    Percentage: float


class MessageItem(BaseModel):
    """Individual message item."""
    From: str
    From_Localised: str
    Message: str
    Message_Localised: str
    Channel: str


class EventResponse(BaseModel):
    """Generic event response."""
    Value: Optional[str] = None
    Station: Optional[str] = None
    Time: Optional[str] = None


class PriceResponse(BaseModel):
    """Response for buy price queries."""
    Price: str


class ConstructionResponse(BaseModel):
    """Response for construction data."""
    id: Optional[str] = None
    name: str
    complete: bool = False
    system: str
    data: Any


class KeySendResponse(BaseModel):
    """Response for keyboard control."""
    status: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None


class ExportTaskResponse(BaseModel):
    """Response for export task initiation."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None

class LocationResponse(BaseModel):
    """Response for current location."""
    StarSystem: str
    SystemAddress: Optional[int] = None
    StarPos: list = []
    Body: Optional[str] = None
    BodyType: Optional[str] = None
    Docked: bool = False
    StationName: Optional[str] = None

class JumpHistoryResponse(BaseModel):
    system: str
    timestamp: str
    jump_dist: Optional[float] = None
    fuel_used: Optional[float] = None

class NavRouteResponse(BaseModel):
    timestamp: str
    event: str
    route: list = []

class DetailedHealthResponse(BaseModel):
    """Response for detailed health information."""
    Health: float
    Shields: float
    ShieldsUp: bool

class ShipResponse(BaseModel):
    """Response for current ship information."""
    Ship: str
    ShipName: Optional[str] = None
    ShipIdent: Optional[str] = None
    HullValue: Optional[int] = None
    ModulesValue: Optional[int] = None
    Rebuy: Optional[int] = None

class LoadoutResponse(BaseModel):
    ship: str
    modules: List[Dict[str, Any]]
    fuel_capacity: Optional[Dict[str, float]] = None
    cargo_capacity: Optional[int] = None

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

class ShipLoadout(BaseModel):
    """Ship load out."""
    ship: str
    modules: List[Any]
    fuel_capacity: int
    cargo_capacity: int