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
This process may take a while when running, depending upon how 
many journal files are present.

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

SHIP_MODULES = """

"""

NAVIGATION_ROUTE = """

"""


# Materials Endpoints
MATERIALS_INVENTORY = """
Get complete engineering materials inventory.

Returns all raw, manufactured, and encoded materials with their current counts.

**Categories:**
- **Raw Materials**: Collected from surface/space mining, meteorites, and missions (max 300 each)
- **Manufactured Materials**: Obtained from ships, installations, and missions (max 250 each)
- **Encoded Materials**: Scanned from ships, wakes, and data points (max 300 each)

**Note:** Materials data updates when you collect, use, or trade materials.
"""

MATERIALS_SUMMARY = """
Get summary statistics for all material categories.

Returns aggregate information including:
- Total types and counts per category
- Capacity usage percentages
- Number of materials at or near capacity

**Use this to:** Quickly assess your material storage situation.
"""

MATERIALS_RAW = """
Get only raw materials inventory.

Returns all raw materials (elements) collected from mining and surface prospecting.

**Common raw materials:** Iron, Nickel, Carbon, Sulphur, Phosphorus, etc.
"""

MATERIALS_MANUFACTURED = """
Get only manufactured materials inventory.

Returns all manufactured materials obtained from ships, installations, and missions.

**Examples:** Shield Emitters, Heat Exchangers, Chemical Processors, etc.
"""

MATERIALS_ENCODED = """
Get only encoded materials inventory.

Returns all encoded data materials scanned from ships, wakes, and data points.

**Examples:** Emission Data, Wake Echoes, Shield Analysis, Encryption Archives, etc.
"""

MATERIALS_SEARCH = """
Search for a specific material by name.

Searches across all categories and returns detailed information including:
- Material category (raw/manufactured/encoded)
- Current count
- Maximum capacity
- Usage percentage
- Whether at maximum capacity

**Search tips:** 
- Case-insensitive
- Searches both internal name and localized name
- Partial matches supported
"""

MATERIALS_AT_CAPACITY = """
Get all materials that are at maximum capacity.

Returns materials at their storage limit:
- Raw: 300
- Manufactured: 250  
- Encoded: 300

**Use this to:** Identify materials to trade or avoid collecting.
"""

MATERIALS_LOW_STOCK = """
Get materials below a specified count threshold.

Returns all materials with counts below your specified threshold.

**Use this to:** 
- Plan material gathering sessions
- Identify materials needed for engineering
- Prepare for expeditions

**Default threshold:** 10 units
"""

MATERIALS_BY_GRADE = """
Get materials filtered by grade/rarity (1-5).

**Grades:**
- Grade 1: Common (Basic, Standard, Worn)
- Grade 2: Standard (Modified, Flawed, Salvaged)
- Grade 3: Rare (Refined, Anomalous, Unusual)
- Grade 4: Very Rare (Conductive, Exquisite, Classified)
- Grade 5: Legendary (Biotech, Exceptional, Proprietary)

**Note:** Grade detection is simplified. Raw materials don't have traditional grades.
"""

# Engineers Endpoints
ENGINEERS_PROGRESS = """
Get complete engineer progress information.

Returns all engineers with their current status:
- **Known**: Engineer discovered but requirements not met
- **Invited**: Requirements met, can now unlock
- **Unlocked**: Engineer unlocked and available
- **Barred**: No longer available (rare)

For unlocked engineers, also shows:
- Current rank (1-5, Grade 1-5 access)
- Progress to next rank (0-100%)

**Note:** Data updates when you unlock engineers or complete crafts.
"""

ENGINEERS_SUMMARY = """
Get summary statistics for all engineers.

Returns aggregate information including:
- Total number of engineers
- Count by status (known/invited/unlocked/barred)
- Number at maximum rank (5)
- Average rank of unlocked engineers

**Use this to:** Quick overview of your engineering progression.
"""

ENGINEERS_UNLOCKED = """
Get all engineers that have been unlocked.

Returns only engineers you can currently visit and use for modifications.

**Use this to:** See which engineers are available for crafting.
"""

ENGINEERS_INVITED = """
Get all engineers that have sent invitations.

Returns engineers whose requirements you've met and are ready to unlock.

**Next step:** Visit these engineers to unlock them and start crafting.
"""

ENGINEERS_KNOWN = """
Get all engineers that are known but not yet unlocked.

Returns engineers you've discovered but haven't met requirements for yet.

**Use this to:** Plan which engineers to unlock next.
"""

ENGINEERS_MAX_RANK = """
Get all engineers at maximum rank (Grade 5).

Returns engineers who have reached the highest access level.

**At Grade 5:**
- Access to all blueprint modifications
- Maximum experimental effects available
- No further rank progression needed

**Use this to:** See your fully progressed engineers.
"""

ENGINEERS_SEARCH = """
Search for a specific engineer by name.

Returns detailed information including:
- Current unlock status
- Rank and progress (if unlocked)
- Next rank information
- Whether at maximum rank

**Search tips:**
- Case-insensitive
- Partial matches supported
- Example: "farseer", "dweller", "martuuk"
"""

ENGINEERS_BY_RANK = """
Get all engineers at a specific rank (1-5).

Returns unlocked engineers at the specified grade level.

**Ranks:**
- Rank 1: Basic modifications
- Rank 2: Improved modifications
- Rank 3: Advanced modifications
- Rank 4: High-end modifications
- Rank 5: Maximum modifications + all experimentals

**Use this to:** See progression at each grade level.
"""

ENGINEERS_IN_PROGRESS = """
Get engineers currently being ranked up.

Returns unlocked engineers below rank 5, sorted by progress.

**Use this to:**
- See which engineers are closest to next rank
- Plan crafting to progress specific engineers
- Track overall engineering progression
"""

ENGINEERS_STATISTICS = """
Get detailed statistics about engineer progress.

Returns comprehensive breakdown including:
- Status distribution
- Rank distribution
- Completion percentages
- Overall progress metrics

**Includes:**
- Total and percentage unlocked
- Rank 5 completion rate
- Overall progression percentage
- Engineers in progress vs completed
"""


# Exploration Endpoints
EXPLORATION_CURRENT_SYSTEM = """
Get summary of bodies scanned in the current system.

Returns comprehensive information including:
- Total bodies in system (from FSS scan)
- Number of bodies you've scanned
- First discoveries, mapping, and footfall counts
- Star and planet counts
- Landable and terraformable body counts
- Breakdown of planet and star types

**Use this to:** Track exploration progress in your current system.
"""

EXPLORATION_SCANNED_BODIES = """
Get detailed information about all bodies scanned in the current system.

Returns list of all scanned bodies with:
- Discovery status (first discovered/mapped/footfall)
- Body type and classification
- Physical properties (mass, temperature, atmosphere)
- Distance from arrival point
- Landability and terraformability

**Use this to:** Review what you've scanned and plan further exploration.
"""

EXPLORATION_FIRST_DISCOVERIES = """
Get all first discoveries in the current system.

Returns only bodies where you were the first to:
- Discover (first to scan)
- Map (first to surface scan)
- Footfall (first to land on)

**Use this to:** Track your exploration achievements and valuable finds.
"""

EXPLORATION_STATISTICS = """
Get overall exploration statistics from your journals.

**Parameters:**
- `scan_all_logs=false` (default): Only current journal
- `scan_all_logs=true`: All historical journals (slower)

Returns:
- Total systems visited
- Total bodies scanned
- First discovery/mapping/footfall counts
- Most common planet and star types
- Landable and terraformable body counts

**Note:** Scanning all logs may take 30+ seconds for extensive exploration history.
"""

EXPLORATION_SEARCH_SYSTEM = """
Search all journal files for a specific system's exploration data.

Scans through historical journals to find the most recent visit to the specified system.

Returns complete scan summary including:
- All discoveries made
- Planet type breakdown
- Valuable finds

**Use this to:** Review past exploration of specific systems.
"""

EXPLORATION_PLANET_TYPES = """
Get distribution of all planet types you've encountered.

Returns count of each planet class:
- Icy bodies
- Rocky bodies
- High metal content
- Gas giants
- Earth-likes, water worlds, etc.

**Parameters:**
- `scan_all_logs`: Include all historical data

**Use this to:** Understand your exploration patterns and focus areas.
"""

EXPLORATION_VALUABLE_FINDS = """
Get high-value exploration finds from your history.

Returns categorized valuable bodies:
- **Earth-like worlds**: Highest value
- **Water worlds**: High value
- **Ammonia worlds**: High value
- **Terraformable**: Candidate planets
- **First discoveries**: Your unique finds

**Parameters:**
- `scan_all_logs`: Include all historical journals

**Use this to:** Track your most valuable exploration achievements.
"""

# Add to descriptions_en.py

EXPLORATION_FIRST_DISCOVERY_REPORT = """
Generate comprehensive first discovery report.

Creates detailed report of ALL systems where you made first discoveries including:
- **Complete system breakdown** with all stars, planets, and moons
- **Star classifications** (type, class, mass, luminosity, age)
- **Planet details** (class, atmosphere, volcanism, gravity, temperature)
- **Discovery status** for each body (discovered/mapped/footfall)
- **Material composition** for landable bodies
- **Geological/biological signals**
- **High-value finds** (Earth-likes, water worlds, ammonia worlds)
- **Terraformable candidates**

**Parameters:**
- `scan_all_logs=true` (default): Scan entire exploration history
- `scan_all_logs=false`: Current session only
- `include_already_discovered=false` (default): Only systems with first discoveries
- `include_already_discovered=true`: Include all scanned systems

**Output:** Complete JSON report with full system details

**Performance:**
- Small history (< 100 systems): ~5-10 seconds
- Medium history (100-500 systems): ~15-30 seconds
- Large history (500+ systems): ~30-60 seconds

**Use this to:**
- Generate complete exploration records
- Submit EDSM data
- Track valuable discoveries
- Create personal exploration database
- Share discoveries with squadron
"""

EXPLORATION_FIRST_DISCOVERY_SYSTEMS = """
Get simplified list of systems with first discoveries.

Faster alternative to full report - returns basic summary for each system:
- System name and address
- Visit timestamp
- Count of first discoveries/mapped/footfall
- Bodies scanned
- Valuable finds present

**Parameters:**
- `scan_all_logs`: Include all history
- `min_discoveries`: Minimum first discoveries to include (default: 1)

**Performance:** 5-10x faster than full report

**Use this to:**
- Quick overview of exploration achievements
- Find systems worth revisiting
- Identify most profitable discoveries
"""