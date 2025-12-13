from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional, Any
from collections import defaultdict, Counter
import logging

from models.organics_models import (
    OrganicScan,
    OrganicSummary,
    OrganicStats,
    SystemOrganics,
    GenusDistribution
)
from utils.journal import (
    get_latest_journal_file,
    get_all_journal_files,
    parse_journal_line
)
import lang.descriptions_en as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organics", tags=["organics"])


@router.get(
    '/current-system',
    response_model=SystemOrganics,
    summary="Get Organic Scans in Current System",
    description="Get all organic scans (both Analyse and Log) in the current system"
)
async def get_current_system_organics(request: Request):
    """
    Get all organic scan data for the current system.

    Returns both Analyse (first contact) and Log (sample collection) events.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    current_system = None
    system_address = None
    current_body = None
    current_body_id = None
    scans = []

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
                    current_body = data.get('Body')
                    current_body_id = data.get('BodyID')
                    scans = []  # Reset scans for new system

                # Track body changes (landing/disembarking)
                elif event == 'Disembark' and data.get('SystemAddress') == system_address:
                    current_body = data.get('Body')
                    current_body_id = data.get('BodyID')

                # Track organic scans
                elif event == 'ScanOrganic' and data.get('SystemAddress') == system_address:
                    scan = OrganicScan(
                        timestamp=data.get('timestamp'),
                        scan_type=data.get('ScanType'),
                        genus=data.get('Genus_Localised', data.get('Genus', '')),
                        species=data.get('Species_Localised', data.get('Species', '')),
                        variant=data.get('Variant_Localised', data.get('Variant', '')),
                        system_name=current_system,
                        system_address=system_address,
                        body_name=current_body,
                        body_id=current_body_id or data.get('Body'),
                        was_logged=data.get('WasLogged', False)
                    )
                    scans.append(scan)

        if not current_system:
            raise HTTPException(status_code=404, detail="No current system found")

        # Group by body
        bodies = defaultdict(lambda: {'analyse': [], 'log': []})
        for scan in scans:
            if scan.scan_type == 'Analyse':
                bodies[scan.body_name]['analyse'].append(scan)
            elif scan.scan_type == 'Log':
                bodies[scan.body_name]['log'].append(scan)

        # Calculate stats
        total_analyse = sum(1 for s in scans if s.scan_type == 'Analyse')
        total_log = sum(1 for s in scans if s.scan_type == 'Log')
        unique_species = len(set(s.species for s in scans if s.species))
        unique_genus = len(set(s.genus for s in scans if s.genus))

        # Count first discoveries (not previously logged)
        first_discoveries = sum(1 for s in scans if s.scan_type == 'Analyse' and not s.was_logged)

        return SystemOrganics(
            system_name=current_system,
            system_address=system_address,
            total_analyse_scans=total_analyse,
            total_log_scans=total_log,
            unique_species=unique_species,
            unique_genus=unique_genus,
            first_discoveries=first_discoveries,
            bodies=dict(bodies),
            all_scans=scans
        )

    except Exception as e:
        logger.error(f"Error getting organic scans: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/all-scans',
    response_model=List[OrganicScan],
    summary="Get All Organic Scans",
    description="Get all organic scans across all or current journal files"
)
async def get_all_organic_scans(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files"),
        scan_type: Optional[str] = Query(None, description="Filter by scan type (Analyse or Log)")
):
    """
    Get all organic scans from journal files.

    Can filter by scan type and optionally scan all historical journals.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    scans = []
    current_system = None
    system_address = None
    current_body = None
    current_body_id = None

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'Disembark':
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'ScanOrganic':
                        scan_type_val = data.get('ScanType')

                        # Filter by scan type if specified
                        if scan_type and scan_type_val != scan_type:
                            continue

                        scan = OrganicScan(
                            timestamp=data.get('timestamp'),
                            scan_type=scan_type_val,
                            genus=data.get('Genus_Localised', data.get('Genus', '')),
                            species=data.get('Species_Localised', data.get('Species', '')),
                            variant=data.get('Variant_Localised', data.get('Variant', '')),
                            system_name=current_system,
                            system_address=system_address,
                            body_name=current_body,
                            body_id=current_body_id or data.get('Body'),
                            was_logged=data.get('WasLogged', False)
                        )
                        scans.append(scan)

        return scans

    except Exception as e:
        logger.error(f"Error getting organic scans: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/statistics',
    response_model=OrganicStats,
    summary="Get Organic Scan Statistics",
    description="Get comprehensive statistics about organic discoveries"
)
async def get_organic_statistics(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get comprehensive statistics about organic scans and discoveries.

    Includes counts by genus, species, and discovery status.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    total_analyse = 0
    total_log = 0
    first_discoveries = 0
    genus_counter = Counter()
    species_counter = Counter()
    variant_counter = Counter()
    systems_with_organics = set()
    bodies_with_organics = set()

    current_system = None
    system_address = None
    current_body = None

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')
                        current_body = data.get('Body')

                    elif event == 'Disembark':
                        current_body = data.get('Body')

                    elif event == 'ScanOrganic':
                        scan_type = data.get('ScanType')

                        if scan_type == 'Analyse':
                            total_analyse += 1
                            if not data.get('WasLogged', False):
                                first_discoveries += 1
                        elif scan_type == 'Log':
                            total_log += 1

                        genus = data.get('Genus_Localised', data.get('Genus', ''))
                        species = data.get('Species_Localised', data.get('Species', ''))
                        variant = data.get('Variant_Localised', data.get('Variant', ''))

                        if genus:
                            genus_counter[genus] += 1
                        if species:
                            species_counter[species] += 1
                        if variant:
                            variant_counter[variant] += 1

                        if current_system:
                            systems_with_organics.add(current_system)
                        if current_body:
                            bodies_with_organics.add(f"{current_system}:{current_body}")

        # Get most common
        most_common_genus = genus_counter.most_common(1)[0][0] if genus_counter else "None"
        most_common_species = species_counter.most_common(1)[0][0] if species_counter else "None"

        return OrganicStats(
            total_analyse_scans=total_analyse,
            total_log_scans=total_log,
            first_discoveries=first_discoveries,
            unique_genus=len(genus_counter),
            unique_species=len(species_counter),
            unique_variants=len(variant_counter),
            systems_with_organics=len(systems_with_organics),
            bodies_with_organics=len(bodies_with_organics),
            most_common_genus=most_common_genus,
            most_common_species=most_common_species,
            genus_distribution=dict(genus_counter.most_common()),
            species_distribution=dict(species_counter.most_common())
        )

    except Exception as e:
        logger.error(f"Error calculating organic statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/genus-distribution',
    response_model=List[GenusDistribution],
    summary="Get Genus Distribution",
    description="Get detailed distribution of discovered genus types"
)
async def get_genus_distribution(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get detailed breakdown of genus types discovered.

    Shows count and associated species for each genus.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    genus_data = defaultdict(lambda: {
        'count': 0,
        'species': set(),
        'first_discoveries': 0
    })

    current_system = None

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')

                    elif event == 'ScanOrganic':
                        genus = data.get('Genus_Localised', data.get('Genus', ''))
                        species = data.get('Species_Localised', data.get('Species', ''))

                        if genus:
                            genus_data[genus]['count'] += 1
                            if species:
                                genus_data[genus]['species'].add(species)

                            if data.get('ScanType') == 'Analyse' and not data.get('WasLogged', False):
                                genus_data[genus]['first_discoveries'] += 1

        # Convert to list of GenusDistribution objects
        result = []
        for genus, data in genus_data.items():
            result.append(GenusDistribution(
                genus=genus,
                total_scans=data['count'],
                unique_species=len(data['species']),
                species_list=sorted(list(data['species'])),
                first_discoveries=data['first_discoveries']
            ))

        # Sort by total scans (most common first)
        result.sort(key=lambda x: x.total_scans, reverse=True)

        return result

    except Exception as e:
        logger.error(f"Error getting genus distribution: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/first-discoveries',
    response_model=List[OrganicScan],
    summary="Get First Organic Discoveries",
    description="Get all organic scans where you were the first to log them"
)
async def get_first_organic_discoveries(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get all organic scans where you made the first discovery.

    Returns only Analyse scans where WasLogged was false.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    first_discoveries = []
    current_system = None
    system_address = None
    current_body = None
    current_body_id = None

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'Disembark':
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'ScanOrganic':
                        # Only include Analyse scans that were not previously logged
                        if data.get('ScanType') == 'Analyse' and not data.get('WasLogged', False):
                            scan = OrganicScan(
                                timestamp=data.get('timestamp'),
                                scan_type=data.get('ScanType'),
                                genus=data.get('Genus_Localised', data.get('Genus', '')),
                                species=data.get('Species_Localised', data.get('Species', '')),
                                variant=data.get('Variant_Localised', data.get('Variant', '')),
                                system_name=current_system,
                                system_address=system_address,
                                body_name=current_body,
                                body_id=current_body_id or data.get('Body'),
                                was_logged=False
                            )
                            first_discoveries.append(scan)

        return first_discoveries

    except Exception as e:
        logger.error(f"Error getting first discoveries: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/by-system',
    summary="Get Organics by System",
    description="Get organic scans grouped by system"
)
async def get_organics_by_system(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
) -> Dict[str, Any]:
    """
    Get organic scans organized by system.

    Returns a dictionary with system names as keys.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    systems = defaultdict(lambda: {
        'system_name': '',
        'system_address': None,
        'scans': [],
        'unique_species': set(),
        'unique_genus': set(),
        'first_discoveries': 0
    })

    current_system = None
    system_address = None
    current_body = None
    current_body_id = None

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    event = data.get('event')

                    if event in ('FSDJump', 'Location', 'CarrierJump'):
                        current_system = data.get('StarSystem')
                        system_address = data.get('SystemAddress')
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'Disembark':
                        current_body = data.get('Body')
                        current_body_id = data.get('BodyID')

                    elif event == 'ScanOrganic' and current_system:
                        genus = data.get('Genus_Localised', data.get('Genus', ''))
                        species = data.get('Species_Localised', data.get('Species', ''))

                        scan = {
                            'timestamp': data.get('timestamp'),
                            'scan_type': data.get('ScanType'),
                            'genus': genus,
                            'species': species,
                            'variant': data.get('Variant_Localised', data.get('Variant', '')),
                            'body_name': current_body,
                            'was_logged': data.get('WasLogged', False)
                        }

                        systems[current_system]['system_name'] = current_system
                        systems[current_system]['system_address'] = system_address
                        systems[current_system]['scans'].append(scan)

                        if genus:
                            systems[current_system]['unique_genus'].add(genus)
                        if species:
                            systems[current_system]['unique_species'].add(species)

                        if data.get('ScanType') == 'Analyse' and not data.get('WasLogged', False):
                            systems[current_system]['first_discoveries'] += 1

        # Convert sets to counts and format result
        result = {}
        for system_name, system_data in systems.items():
            result[system_name] = {
                'system_name': system_data['system_name'],
                'system_address': system_data['system_address'],
                'total_scans': len(system_data['scans']),
                'unique_genus': len(system_data['unique_genus']),
                'unique_species': len(system_data['unique_species']),
                'first_discoveries': system_data['first_discoveries'],
                'scans': system_data['scans']
            }

        return result

    except Exception as e:
        logger.error(f"Error getting organics by system: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")