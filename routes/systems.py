from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional, Any
from collections import defaultdict, Counter
import logging

from models.systems_models import (
    ScanBody,
    SystemScanSummary,
    DiscoveryStatus,
    ExplorationStats, FirstDiscoveryReport, FirstDiscoveryBody, FirstDiscoverySystem
)
from utils.journal import (
    get_latest_journal_file,
    get_all_journal_files,
    parse_journal_line
)
import lang.descriptions_en as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exploration", tags=["exploration"])


@router.get(
    '/current-system',
    response_model=SystemScanSummary,
    summary="Get Current System Scan Summary",
    description=desc.EXPLORATION_CURRENT_SYSTEM
)
async def get_current_system_summary(request: Request):
    """
    Get summary of bodies scanned in the current system.

    Returns counts of discoveries, planet types, and completion status.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    # Find current system and scans
    current_system = None
    system_address = None
    scans = []
    fss_body_count = 0

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                event = data.get('event')

                # Track system changes
                if event in ('FSDJump', 'Location', 'CarrierJump'):
                    current_system = data.get('StarSystem')
                    system_address = data.get('SystemAddress')
                    scans = []  # Reset scans for new system

                # Track FSS discovery scan
                elif event == 'FSSDiscoveryScan' and data.get('SystemAddress') == system_address:
                    fss_body_count = data.get('BodyCount', 0)

                # Track body scans
                elif event == 'Scan' and data.get('SystemAddress') == system_address:
                    scans.append(data)

        if not current_system:
            raise HTTPException(status_code=404, detail="No current system found")

        # Analyze scans
        first_discoveries = sum(1 for s in scans if not s.get('WasDiscovered', True))
        first_mapped = sum(1 for s in scans if not s.get('WasMapped', True))
        first_footfall = sum(1 for s in scans if not s.get('WasFootfalled', True))

        stars = sum(1 for s in scans if s.get('StarType'))
        planets = sum(1 for s in scans if s.get('PlanetClass'))

        landable = sum(1 for s in scans if s.get('Landable', False))
        terraformable = sum(1 for s in scans if s.get('TerraformState') and s.get('TerraformState') != '')

        # Count planet types
        planet_types = Counter(s.get('PlanetClass') for s in scans if s.get('PlanetClass'))
        star_types = Counter(s.get('StarType') for s in scans if s.get('StarType'))

        return SystemScanSummary(
            SystemName=current_system,
            SystemAddress=system_address,
            TotalBodies=fss_body_count,
            ScannedBodies=len(scans),
            FirstDiscoveries=first_discoveries,
            FirstMapped=first_mapped,
            FirstFootfall=first_footfall,
            Stars=stars,
            Planets=planets,
            LandableBodies=landable,
            TerraformableBodies=terraformable,
            planet_types=dict(planet_types),
            star_types=dict(star_types)
        )

    except Exception as e:
        logger.error(f"Error analyzing system: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing system: {str(e)}")


@router.get(
    '/scanned-bodies',
    summary="Get Scanned Bodies in Current System",
    description=desc.EXPLORATION_SCANNED_BODIES
)
async def get_scanned_bodies(request: Request) -> List[ScanBody]:
    """
    Get all bodies scanned in the current system.

    Returns detailed information about each scanned body.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    current_system = None
    system_address = None
    scans = []

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                event = data.get('event')

                if event in ('FSDJump', 'Location', 'CarrierJump'):
                    current_system = data.get('StarSystem')
                    system_address = data.get('SystemAddress')
                    scans = []

                elif event == 'Scan' and data.get('SystemAddress') == system_address:
                    body_type = "Star" if data.get('StarType') else "Planet"

                    scan_body = ScanBody(
                        BodyName=data.get('BodyName'),
                        BodyID=data.get('BodyID'),
                        BodyType=body_type,
                        StarSystem=data.get('StarSystem'),
                        SystemAddress=data.get('SystemAddress'),
                        DistanceFromArrivalLS=data.get('DistanceFromArrivalLS', 0),
                        WasDiscovered=data.get('WasDiscovered', True),
                        WasMapped=data.get('WasMapped', True),
                        WasFootfalled=data.get('WasFootfalled'),
                        PlanetClass=data.get('PlanetClass'),
                        TerraformState=data.get('TerraformState'),
                        Atmosphere=data.get('Atmosphere'),
                        Landable=data.get('Landable'),
                        MassEM=data.get('MassEM'),
                        SurfaceTemperature=data.get('SurfaceTemperature'),
                        StarType=data.get('StarType'),
                        StellarMass=data.get('StellarMass')
                    )
                    scans.append(scan_body)

        return scans

    except Exception as e:
        logger.error(f"Error getting scanned bodies: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/first-discoveries',
    summary="Get First Discoveries in Current System",
    description=desc.EXPLORATION_FIRST_DISCOVERIES
)
async def get_first_discoveries(request: Request) -> List[DiscoveryStatus]:
    """
    Get all first discoveries in the current system.

    Returns bodies where you were the first to discover, map, or footfall.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    current_system = None
    system_address = None
    discoveries = []

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                event = data.get('event')

                if event in ('FSDJump', 'Location', 'CarrierJump'):
                    current_system = data.get('StarSystem')
                    system_address = data.get('SystemAddress')
                    discoveries = []

                elif event == 'Scan' and data.get('SystemAddress') == system_address:
                    was_discovered = data.get('WasDiscovered', True)
                    was_mapped = data.get('WasMapped', True)
                    was_footfalled = data.get('WasFootfalled', True)

                    # Only include if it's a first of something
                    if not was_discovered or not was_mapped or not was_footfalled:
                        discoveries.append(DiscoveryStatus(
                            name=data.get('BodyName'),
                            first_discovered=not was_discovered,
                            first_mapped=not was_mapped,
                            first_footfall=not was_footfalled,
                            scan_type=data.get('ScanType', 'Unknown'),
                            timestamp=data.get('timestamp')
                        ))

        return discoveries

    except Exception as e:
        logger.error(f"Error getting first discoveries: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/statistics',
    response_model=ExplorationStats,
    summary="Get Exploration Statistics",
    description=desc.EXPLORATION_STATISTICS
)
async def get_exploration_statistics(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files (slow)")
):
    """
    Get overall exploration statistics.

    By default scans only the current journal file.
    Set scan_all_logs=true to scan all historical journals (this may take time).
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    systems_visited = set()
    total_scans = 0
    first_discoveries = 0
    first_mapped = 0
    first_footfall = 0
    planet_types = Counter()
    star_types = Counter()
    landable_count = 0
    terraformable_count = 0

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        system = data.get('StarSystem')
                        if system:
                            systems_visited.add(system)

                    elif event == 'Scan':
                        total_scans += 1

                        if not data.get('WasDiscovered', True):
                            first_discoveries += 1
                        if not data.get('WasMapped', True):
                            first_mapped += 1
                        if not data.get('WasFootfalled', True):
                            first_footfall += 1

                        planet_class = data.get('PlanetClass')
                        if planet_class:
                            planet_types[planet_class] += 1

                        star_type = data.get('StarType')
                        if star_type:
                            star_types[star_type] += 1

                        if data.get('Landable'):
                            landable_count += 1

                        if data.get('TerraformState') and data.get('TerraformState') != '':
                            terraformable_count += 1

        most_common_planet = planet_types.most_common(1)[0][0] if planet_types else "None"
        most_common_star = star_types.most_common(1)[0][0] if star_types else "None"

        return ExplorationStats(
            total_systems_visited=len(systems_visited),
            total_bodies_scanned=total_scans,
            first_discoveries=first_discoveries,
            first_mapped=first_mapped,
            first_footfall=first_footfall,
            most_common_planet_type=most_common_planet,
            most_common_star_type=most_common_star,
            landable_bodies_found=landable_count,
            terraformable_bodies_found=terraformable_count
        )

    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/search-system',
    response_model=SystemScanSummary,
    summary="Search for System in History",
    description=desc.EXPLORATION_SEARCH_SYSTEM
)
async def search_system_history(
        request: Request,
        system_name: str = Query(..., description="System name to search for")
):
    """
    Search all journal files for a specific system's scan data.

    Returns the most recent scan summary for the specified system.
    """
    json_location = request.app.state.json_location
    journal_files = get_all_journal_files(json_location, reverse=True)  # Newest first

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    system_name_lower = system_name.lower()

    try:
        for journal_file in journal_files:
            current_system = None
            system_address = None
            scans = []
            fss_body_count = 0
            found_system = False

            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        sys_name = data.get('StarSystem', '')
                        if sys_name.lower() == system_name_lower:
                            current_system = sys_name
                            system_address = data.get('SystemAddress')
                            scans = []
                            fss_body_count = 0
                            found_system = True
                        elif found_system:
                            # Moved to different system, analyze what we found
                            break

                    elif found_system:
                        if event == 'FSSDiscoveryScan' and data.get('SystemAddress') == system_address:
                            fss_body_count = data.get('BodyCount', 0)

                        elif event == 'Scan' and data.get('SystemAddress') == system_address:
                            scans.append(data)

            if found_system and current_system:
                # Found the system, analyze it
                first_discoveries = sum(1 for s in scans if not s.get('WasDiscovered', True))
                first_mapped = sum(1 for s in scans if not s.get('WasMapped', True))
                first_footfall = sum(1 for s in scans if not s.get('WasFootfalled', True))

                stars = sum(1 for s in scans if s.get('StarType'))
                planets = sum(1 for s in scans if s.get('PlanetClass'))

                landable = sum(1 for s in scans if s.get('Landable', False))
                terraformable = sum(1 for s in scans if s.get('TerraformState') and s.get('TerraformState') != '')

                planet_types = Counter(s.get('PlanetClass') for s in scans if s.get('PlanetClass'))
                star_types = Counter(s.get('StarType') for s in scans if s.get('StarType'))

                return SystemScanSummary(
                    SystemName=current_system,
                    SystemAddress=system_address,
                    TotalBodies=fss_body_count,
                    ScannedBodies=len(scans),
                    FirstDiscoveries=first_discoveries,
                    FirstMapped=first_mapped,
                    FirstFootfall=first_footfall,
                    Stars=stars,
                    Planets=planets,
                    LandableBodies=landable,
                    TerraformableBodies=terraformable,
                    planet_types=dict(planet_types),
                    star_types=dict(star_types)
                )

        raise HTTPException(status_code=404, detail=f"System '{system_name}' not found in journal history")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching for system: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/planet-types',
    summary="Get Planet Type Distribution",
    description=desc.EXPLORATION_PLANET_TYPES
)
async def get_planet_type_distribution(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
) -> Dict[str, int]:
    """
    Get distribution of planet types discovered.

    Returns count of each planet class encountered.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    planet_types = Counter()

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if data and data.get('event') == 'Scan':
                        planet_class = data.get('PlanetClass')
                        if planet_class:
                            planet_types[planet_class] += 1

        return dict(planet_types.most_common())

    except Exception as e:
        logger.error(f"Error getting planet types: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/valuable-finds',
    summary="Get Valuable Exploration Finds",
    description=desc.EXPLORATION_VALUABLE_FINDS
)
async def get_valuable_finds(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get valuable exploration finds (terraformable, Earth-likes, water worlds, etc.).

    Returns categorized list of high-value bodies.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    valuable = {
        'earth_like': [],
        'water_worlds': [],
        'ammonia_worlds': [],
        'terraformable': [],
        'first_discoveries': []
    }

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data or data.get('event') != 'Scan':
                        continue

                    planet_class = data.get('PlanetClass', '')
                    terraform = data.get('TerraformState', '')
                    body_name = data.get('BodyName')
                    system = data.get('StarSystem')
                    first_discovered = not data.get('WasDiscovered', True)

                    body_info = {
                        'body': body_name,
                        'system': system,
                        'first_discovered': first_discovered
                    }

                    if planet_class == 'Earthlike body':
                        valuable['earth_like'].append(body_info)
                    elif planet_class == 'Water world':
                        valuable['water_worlds'].append(body_info)
                    elif planet_class == 'Ammonia world':
                        valuable['ammonia_worlds'].append(body_info)

                    if terraform and terraform != '':
                        valuable['terraformable'].append(body_info)

                    if first_discovered:
                        valuable['first_discoveries'].append(body_info)

        return valuable

    except Exception as e:
        logger.error(f"Error getting valuable finds: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/first-discovery-report',
    response_model=FirstDiscoveryReport,
    summary="Generate First Discovery Report",
    description=desc.EXPLORATION_FIRST_DISCOVERY_REPORT
)
async def generate_first_discovery_report(
        request: Request,
        scan_all_logs: bool = Query(True, description="Scan all journal files (recommended)"),
        include_already_discovered: bool = Query(False,
                                                 description="Include systems where some bodies were already discovered")
):
    """
    Generate comprehensive first discovery report.

    Creates detailed report of all systems with first discoveries including:
    - Complete system breakdown with star types
    - All planets with classifications
    - Discovery status for each body
    - High-value finds (Earth-likes, water worlds, etc.)
    - Material composition for landable bodies

    **Note:** This may take 30-60 seconds for extensive exploration history.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    from datetime import datetime
    from collections import defaultdict

    systems_data = defaultdict(lambda: {
        'system_name': '',
        'system_address': 0,
        'visit_timestamp': '',
        'bodies': [],
        'fss_body_count': 0
    })

    first_timestamp = None
    last_timestamp = None

    try:
        for journal_file in journal_files:
            current_system = None
            system_address = None

            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')
                    timestamp = data.get('timestamp')

                    if not first_timestamp:
                        first_timestamp = timestamp
                    last_timestamp = timestamp

                    # Track system entry
                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')

                        if system_address and current_system:
                            systems_data[system_address]['system_name'] = current_system
                            systems_data[system_address]['system_address'] = system_address
                            systems_data[system_address]['visit_timestamp'] = timestamp

                    # Track FSS scan
                    elif event == 'FSSDiscoveryScan' and system_address:
                        systems_data[system_address]['fss_body_count'] = data.get('BodyCount', 0)

                    # Track body scans
                    elif event == 'Scan' and system_address:
                        # Only include if there's a first discovery/mapping/footfall
                        was_discovered = data.get('WasDiscovered', True)
                        was_mapped = data.get('WasMapped', True)
                        was_footfalled = data.get('WasFootfalled', True)

                        if not was_discovered or not was_mapped or not was_footfalled or include_already_discovered:
                            systems_data[system_address]['bodies'].append(data)

        # Process systems into structured report
        report_systems = []
        total_first_discoveries = 0
        total_first_mapped = 0
        total_first_footfall = 0
        earth_like_count = 0
        water_world_count = 0
        ammonia_world_count = 0
        terraformable_count = 0

        for sys_addr, sys_data in systems_data.items():
            if not sys_data['bodies']:
                continue

            # Process bodies
            stars = []
            planets = []
            moons = []

            first_disc_count = 0
            first_map_count = 0
            first_foot_count = 0

            planet_types = Counter()
            star_types = Counter()

            has_earth_like = False
            has_water_world = False
            has_ammonia_world = False
            landable_count = 0
            terraform_count = 0

            for body_data in sys_data['bodies']:
                # Determine body type
                is_star = bool(body_data.get('StarType'))
                is_moon = len(body_data.get('Parents', [])) > 2  # Moons have multiple parents
                body_type = "Star" if is_star else ("Moon" if is_moon else "Planet")

                # Count discoveries
                if not body_data.get('WasDiscovered', True):
                    first_disc_count += 1
                    total_first_discoveries += 1
                if not body_data.get('WasMapped', True):
                    first_map_count += 1
                    total_first_mapped += 1
                if not body_data.get('WasFootfalled', True):
                    first_foot_count += 1
                    total_first_footfall += 1

                # Check for valuable bodies
                planet_class = body_data.get('PlanetClass', '')
                if planet_class == 'Earthlike body':
                    has_earth_like = True
                    earth_like_count += 1
                elif planet_class == 'Water world':
                    has_water_world = True
                    water_world_count += 1
                elif planet_class == 'Ammonia world':
                    has_ammonia_world = True
                    ammonia_world_count += 1

                if body_data.get('TerraformState') and body_data.get('TerraformState') != '':
                    terraform_count += 1
                    terraformable_count += 1

                if body_data.get('Landable'):
                    landable_count += 1

                # Count types
                if planet_class:
                    planet_types[planet_class] += 1
                if body_data.get('StarType'):
                    star_types[body_data.get('StarType')] += 1

                # Extract signals
                signals = None
                if body_data.get('Signals'):
                    signals = [s.get('Type_Localised', s.get('Type')) for s in body_data.get('Signals', [])]

                # Create body record
                body_record = FirstDiscoveryBody(
                    body_name=body_data.get('BodyName'),
                    body_id=body_data.get('BodyID'),
                    body_type=body_type,
                    scan_type=body_data.get('ScanType', 'Unknown'),
                    timestamp=body_data.get('timestamp'),
                    distance_ls=body_data.get('DistanceFromArrivalLS', 0),
                    first_discovered=not body_data.get('WasDiscovered', True),
                    first_mapped=not body_data.get('WasMapped', True),
                    first_footfall=not body_data.get('WasFootfalled', True),
                    planet_class=body_data.get('PlanetClass'),
                    atmosphere=body_data.get('Atmosphere'),
                    volcanism=body_data.get('Volcanism'),
                    landable=body_data.get('Landable'),
                    terraform_state=body_data.get('TerraformState'),
                    mass_em=body_data.get('MassEM'),
                    radius=body_data.get('Radius'),
                    surface_gravity=body_data.get('SurfaceGravity'),
                    surface_temp=body_data.get('SurfaceTemperature'),
                    surface_pressure=body_data.get('SurfacePressure'),
                    star_type=body_data.get('StarType'),
                    star_class=body_data.get('Subclass'),
                    stellar_mass=body_data.get('StellarMass'),
                    luminosity=body_data.get('Luminosity'),
                    age_my=body_data.get('Age_MY'),
                    has_rings=bool(body_data.get('Rings')),
                    ring_count=len(body_data.get('Rings', [])),
                    signals=signals,
                    materials=body_data.get('Materials')
                )

                if is_star:
                    stars.append(body_record)
                elif is_moon:
                    moons.append(body_record)
                else:
                    planets.append(body_record)

            # Create system record
            system_record = FirstDiscoverySystem(
                system_name=sys_data['system_name'],
                system_address=sys_data['system_address'],
                visit_timestamp=sys_data['visit_timestamp'],
                total_bodies=sys_data['fss_body_count'],
                bodies_scanned=len(sys_data['bodies']),
                first_discoveries_count=first_disc_count,
                first_mapped_count=first_map_count,
                first_footfall_count=first_foot_count,
                star_count=len(stars),
                planet_count=len(planets),
                landable_count=landable_count,
                terraformable_count=terraform_count,
                has_earth_like=has_earth_like,
                has_water_world=has_water_world,
                has_ammonia_world=has_ammonia_world,
                stars=stars,
                planets=planets,
                moons=moons,
                planet_type_breakdown=dict(planet_types),
                star_type_breakdown=dict(star_types)
            )

            report_systems.append(system_record)

        # Sort systems by visit timestamp (most recent first)
        report_systems.sort(key=lambda x: x.visit_timestamp, reverse=True)

        return FirstDiscoveryReport(
            generated_at=datetime.now().isoformat(),
            scan_date_range={
                'start': first_timestamp or '',
                'end': last_timestamp or ''
            },
            total_systems=len(report_systems),
            total_first_discoveries=total_first_discoveries,
            total_first_mapped=total_first_mapped,
            total_first_footfall=total_first_footfall,
            earth_like_count=earth_like_count,
            water_world_count=water_world_count,
            ammonia_world_count=ammonia_world_count,
            terraformable_count=terraformable_count,
            systems=report_systems
        )

    except Exception as e:
        logger.error(f"Error generating first discovery report: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/first-discovery-systems',
    summary="Get List of First Discovery Systems",
    description=desc.EXPLORATION_FIRST_DISCOVERY_SYSTEMS
)
async def get_first_discovery_systems(
        request: Request,
        scan_all_logs: bool = Query(True, description="Scan all journal files"),
        min_discoveries: int = Query(1, ge=1, description="Minimum first discoveries to include system")
) -> List[Dict[str, Any]]:
    """
    Get simplified list of systems with first discoveries.

    Returns basic information about each system where you made first discoveries.
    Faster than the full report.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    from collections import defaultdict

    systems = defaultdict(lambda: {
        'system_name': '',
        'visit_timestamp': '',
        'first_discoveries': 0,
        'first_mapped': 0,
        'first_footfall': 0,
        'bodies_scanned': 0,
        'valuable_finds': []
    })

    try:
        for journal_file in journal_files:
            current_system = None
            system_address = None

            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')

                        if system_address:
                            systems[system_address]['system_name'] = current_system
                            systems[system_address]['visit_timestamp'] = data.get('timestamp')

                    elif event == 'Scan' and system_address:
                        if not data.get('WasDiscovered', True):
                            systems[system_address]['first_discoveries'] += 1
                        if not data.get('WasMapped', True):
                            systems[system_address]['first_mapped'] += 1
                        if not data.get('WasFootfalled', True):
                            systems[system_address]['first_footfall'] += 1

                        systems[system_address]['bodies_scanned'] += 1

                        # Track valuable finds
                        planet_class = data.get('PlanetClass', '')
                        if planet_class in ('Earthlike body', 'Water world', 'Ammonia world'):
                            if planet_class not in systems[system_address]['valuable_finds']:
                                systems[system_address]['valuable_finds'].append(planet_class)

        # Filter and format results
        result = []
        for sys_addr, sys_data in systems.items():
            if sys_data['first_discoveries'] >= min_discoveries:
                result.append({
                    'system_name': sys_data['system_name'],
                    'system_address': sys_addr,
                    'visit_timestamp': sys_data['visit_timestamp'],
                    'first_discoveries': sys_data['first_discoveries'],
                    'first_mapped': sys_data['first_mapped'],
                    'first_footfall': sys_data['first_footfall'],
                    'bodies_scanned': sys_data['bodies_scanned'],
                    'valuable_finds': sys_data['valuable_finds']
                })

        # Sort by first discoveries (most first)
        result.sort(key=lambda x: x['first_discoveries'], reverse=True)

        return result

    except Exception as e:
        logger.error(f"Error getting first discovery systems: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")