# ============================================================================
# FILE: descriptions.py
# ============================================================================
"""API endpoint descriptions for documentation."""

# Status Endpoints
STATUS_ACTIVE = """
Check if Elite Dangerous is currently running.

Returns the current game status by checking for the presence of Flags2 
in the Status.json file, which indicates an active game session.

**Returns:**
- `true` - Game is currently active
- `false` - Game is not running
"""

STATUS_WEALTH = """
Get the commander's current credit balance.

Retrieves the current balance from the Status.json file.

**Note:** This value updates in real-time as you earn or spend credits, when the game is running.
"""

STATUS_FLAGS = """
Get current game status flags.

Returns two sets of binary flags that indicate various game states:
- **Flags**: 32-bit flags for basic states (docked, landed, shields up, etc.)
- **Flags2**: 19-bit flags for additional states

**Format:** Binary strings with LSB first (reversed)
"""

STATUS_PIPS = """
Get current pip setting for engines, systems and weapons.

Will accept a single parameter specifying either raw or percent

- **raw**: returns a single digit integer from 0 - 8 representing current pip setting)
- **percent**: returns an integer between 0 - 100 for us with gauges to represent current pip setting

"""

SHIPS_CURRENT = """
Get basic current ship information.

Returns, name, ship type, identifier, value, modules value, and rebuy cost
"""

SHIPS_LOADOUT = """
Get current ship loadout information.

Returns all fitted modules, price, and any engineering completed, fuel and cargo capacity
"""

# Carrier Endpoints
CARRIER_STATS = """
Get complete carrier statistics.

Returns comprehensive information about your Fleet Carrier including:
- Fuel level and jump range
- Financial information (balance, reserves, taxes)
- Space usage and capacity
- Active crew members and services
- Ship and module storage

**Note:** This data updates when you dock at your carrier or view carrier management.
"""

CARRIER_FUEL = """
Get carrier fuel level and jump range.

Quick endpoint to check fuel status without retrieving full carrier stats.

**Returns:**
- Current fuel level (max 1000 tons)
- Current jump range based on fuel and mass
- Maximum possible jump range (500 ly)
"""

CARRIER_BALANCE = """
Get carrier financial information.

Returns detailed financial breakdown:
- **Carrier Balance**: Total funds
- **Reserve Balance**: Funds set aside for upkeep
- **Available Balance**: Funds available for purchases
- **Reserve Percent**: Percentage of total reserved

**Note:** Reserve balance covers weekly upkeep costs.
"""

CARRIER_CAPACITY = """
Get carrier space usage and capacity.

Returns detailed breakdown of how carrier storage (25,000 tons) is used:
- Total and free capacity
- Space used by cargo, ships, modules, and crew
- Usage percentage

**Note:** Crew always takes 800 tons of space.
"""

CARRIER_CREW = """
Get carrier crew members and their status.

Returns information about all 14 potential crew positions:
- Which services are activated
- Crew member names (if assigned)
- Active vs inactive services

**Services available:**
BlackMarket, Captain, Refuel, Repair, Rearm, Commodities, 
VoucherRedemption, Exploration, Shipyard, Outfitting, 
CarrierFuel, VistaGenomics, PioneerSupplies, Bartender
"""

CARRIER_SERVICES = """
Get available carrier services with detailed status.

Returns a detailed breakdown of each service showing:
- Activation status
- Enabled status
- Assigned crew member name

**Use this to:** Check which services are operational before planning activities.
"""

CARRIER_JUMP_REQUEST = """
Get the most recent carrier jump request.

Returns information about scheduled carrier jumps including:
- Destination system and body
- Scheduled departure time
- System coordinates

**Note:** This only shows if a jump has been scheduled.
"""

CARRIER_INFO = """
Get combined carrier information.

Convenience endpoint that returns both carrier statistics and 
any pending jump request in a single call.

**Use this to:** Get complete carrier overview with one API call.
"""

# Construction Endpoints
CONSTRUCTION_CURRENT = """
Get current colonization construction depot information.

Returns details about the active construction site if docked at one:
- Site name and location
- Required resources and amounts
- Current completion status
- Completion rewards

**Note:** Only available when docked at a colonization construction depot.
"""

# Cargo Endpoints
CARGO_INVENTORY = """
Get current ship cargo inventory.

Returns list of all commodities currently in your ship's cargo hold 
with quantities.

**Note:** Updates in real-time as you buy, sell, or transfer cargo.
"""

CARGO_MARKET = """
Get current market data.

Returns all commodities available at the current station with:
- Buy and sell prices
- Stock levels
- Demand

**Note:** Only available when docked at a station with a commodity market.
"""

CARGO_TRANSFER_HISTORY = """
Calculate net carrier cargo inventory from transfer history.

Scans **all** journal files to calculate current carrier cargo by 
tracking all CargoTransfer events (to/from carrier).

**Returns:** Dictionary with commodity names as keys and net quantities as values.

**Note:** This is a calculated value based on historical transfers, 
not real-time carrier inventory.
"""

# Events Endpoints
EVENTS_MESSAGES = """
Get recent in-game messages.

Retrieves the most recent messages from a specified channel.

**Channels:**
- `npc` - NPC communications (missions, station services)
- `starsystem` - System-wide messages
- `squadron` - Squadron communications

**Parameters:**
- `count` (1-100): Number of messages to retrieve
- `channel`: Message channel to filter
"""

EVENTS_EVENT = """
Get the latest occurrence of a specific event.

Search for the most recent instance of any game event and extract 
a specific property from it.

**Common events:** Docked, Undocked, FSDJump, Location, MarketBuy, MarketSell

**Use cases:**
- Get last docked station: event=Docked, property=StationName
- Get current system: event=FSDJump, property=StarSystem
"""

EVENTS_BUY_PRICE = """
Get the purchase price for a specific commodity.

Searches recent MarketBuy events to find what you paid for a commodity.

**Use this to:** Calculate profit margins when selling commodities.

**Note:** Returns the most recent purchase price found in the journal.
"""

# Export Endpoints
EXPORT_CONSTRUCTION_HISTORY = """
Export all colonization construction history to file.

Scans all journal files and exports every ColonisationConstructionDepot 
event with associated station information.

**Output:** JSON file with one record per construction site visited.

**Use this to:** Track colonization contributions across multiple sites.

**Note:** This is a background task - use the status endpoint to check progress.
"""

EXPORT_ORGANIC_HISTORY = """
Export all organic scan history to file.

Scans all journal files and exports every ScanOrganic event with 
system and body information.

**Output:** JSON file with scan data including:
- Organism type and variant
- System and body location
- Scan timestamps

**Use this to:** Track exobiology discoveries and earnings.
"""

EXPORT_SELL_ORGANIC_HISTORY = """
Export all organic data sales history to file.

Scans all journal files and exports every SellOrganicData event.

**Output:** JSON file with sale records including credits earned.

**Use this to:** Calculate total exobiology earnings.
"""

EXPORT_STATUS = """
Check the status of an export task.

Returns the current status and progress of a background export job.

**Status values:**
- `running` - Export in progress
- `completed` - Export finished successfully
- `failed` - Export encountered an error

**Progress:** Percentage complete (0-100%)
"""