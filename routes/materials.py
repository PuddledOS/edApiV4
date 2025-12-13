from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional
import logging

from models.materials_models import (
    MaterialsResponse,
    MaterialItem,
    MaterialsSummaryResponse,
    MaterialCategoryStats,
    MaterialSearchResult
)
from utils.journal import find_latest_event
import lang.descriptions_en as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/materials", tags=["materials"])

# Material capacity limits
CAPACITY = {
    "raw": 300,
    "manufactured": 250,
    "encoded": 300
}


@router.get(
    '/inventory',
    response_model=MaterialsResponse,
    summary="Get Materials Inventory",
    description=desc.MATERIALS_INVENTORY
)
async def get_materials_inventory(request: Request):
    """
    Get complete engineering materials inventory.

    Returns all raw, manufactured, and encoded materials with counts.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    try:
        return MaterialsResponse(
            Raw=[MaterialItem(**item) for item in materials_event.get('Raw', [])],
            Manufactured=[MaterialItem(**item) for item in materials_event.get('Manufactured', [])],
            Encoded=[MaterialItem(**item) for item in materials_event.get('Encoded', [])],
            timestamp=materials_event.get('timestamp')
        )
    except Exception as e:
        logger.error(f"Error parsing materials data: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing materials: {str(e)}")


@router.get(
    '/summary',
    response_model=MaterialsSummaryResponse,
    summary="Get Materials Summary",
    description=desc.MATERIALS_SUMMARY
)
async def get_materials_summary(request: Request):
    """
    Get summary statistics for all material categories.

    Returns counts, capacity usage, and statistics for raw, manufactured, and encoded materials.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    try:
        # Calculate stats for each category
        raw_materials = materials_event.get('Raw', [])
        manufactured_materials = materials_event.get('Manufactured', [])
        encoded_materials = materials_event.get('Encoded', [])

        def calculate_category_stats(materials: List[Dict], max_per_type: int) -> MaterialCategoryStats:
            """Calculate statistics for a material category."""
            total_types = len(materials)
            total_count = sum(m.get('Count', 0) for m in materials)
            capacity = total_types * max_per_type
            usage_percent = (total_count / capacity * 100) if capacity > 0 else 0

            at_capacity = sum(1 for m in materials if m.get('Count', 0) >= max_per_type)
            near_capacity = sum(1 for m in materials if max_per_type * 0.9 <= m.get('Count', 0) < max_per_type)

            return MaterialCategoryStats(
                total_types=total_types,
                total_count=total_count,
                capacity=capacity,
                usage_percent=round(usage_percent, 2),
                at_capacity=at_capacity,
                near_capacity=near_capacity
            )

        raw_stats = calculate_category_stats(raw_materials, CAPACITY['raw'])
        manufactured_stats = calculate_category_stats(manufactured_materials, CAPACITY['manufactured'])
        encoded_stats = calculate_category_stats(encoded_materials, CAPACITY['encoded'])

        total_materials = raw_stats.total_count + manufactured_stats.total_count + encoded_stats.total_count
        total_capacity = raw_stats.capacity + manufactured_stats.capacity + encoded_stats.capacity
        overall_usage = (total_materials / total_capacity * 100) if total_capacity > 0 else 0

        return MaterialsSummaryResponse(
            raw=raw_stats,
            manufactured=manufactured_stats,
            encoded=encoded_stats,
            total_materials=total_materials,
            total_capacity=total_capacity,
            overall_usage_percent=round(overall_usage, 2)
        )

    except Exception as e:
        logger.error(f"Error calculating materials summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")


@router.get(
    '/raw',
    summary="Get Raw Materials",
    description=desc.MATERIALS_RAW
)
async def get_raw_materials(request: Request) -> List[MaterialItem]:
    """Get only raw materials inventory."""
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    raw_materials = materials_event.get('Raw', [])
    return [MaterialItem(**item) for item in raw_materials]


@router.get(
    '/manufactured',
    summary="Get Manufactured Materials",
    description=desc.MATERIALS_MANUFACTURED
)
async def get_manufactured_materials(request: Request) -> List[MaterialItem]:
    """Get only manufactured materials inventory."""
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    manufactured_materials = materials_event.get('Manufactured', [])
    return [MaterialItem(**item) for item in manufactured_materials]


@router.get(
    '/encoded',
    summary="Get Encoded Materials",
    description=desc.MATERIALS_ENCODED
)
async def get_encoded_materials(request: Request) -> List[MaterialItem]:
    """Get only encoded materials inventory."""
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    encoded_materials = materials_event.get('Encoded', [])
    return [MaterialItem(**item) for item in encoded_materials]


@router.get(
    '/search',
    response_model=MaterialSearchResult,
    summary="Search for Material",
    description=desc.MATERIALS_SEARCH
)
async def search_material(
        request: Request,
        name: str = Query(..., description="Material name (case-insensitive)")
):
    """
    Search for a specific material by name.

    Returns details about the material including current count and capacity info.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    name_lower = name.lower()

    # Search in all categories
    categories = {
        'raw': (materials_event.get('Raw', []), CAPACITY['raw']),
        'manufactured': (materials_event.get('Manufactured', []), CAPACITY['manufactured']),
        'encoded': (materials_event.get('Encoded', []), CAPACITY['encoded'])
    }

    for category, (materials, max_capacity) in categories.items():
        for material in materials:
            mat_name = material.get('Name', '').lower()
            mat_name_loc = material.get('Name_Localised', '').lower()

            if name_lower in mat_name or name_lower in mat_name_loc:
                count = material.get('Count', 0)
                at_max = count >= max_capacity
                percentage = (count / max_capacity * 100) if max_capacity > 0 else 0

                return MaterialSearchResult(
                    name=material.get('Name'),
                    name_localised=material.get('Name_Localised'),
                    category=category,
                    count=count,
                    max_capacity=max_capacity,
                    at_max=at_max,
                    percentage=round(percentage, 2)
                )

    raise HTTPException(status_code=404, detail=f"Material '{name}' not found in inventory")


@router.get(
    '/at-capacity',
    summary="Get Materials at Capacity",
    description=desc.MATERIALS_AT_CAPACITY
)
async def get_materials_at_capacity(request: Request) -> Dict[str, List[MaterialItem]]:
    """
    Get all materials that are at maximum capacity.

    Useful for knowing which materials to trade or avoid collecting.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    result = {
        'raw': [],
        'manufactured': [],
        'encoded': []
    }

    # Check raw materials
    for material in materials_event.get('Raw', []):
        if material.get('Count', 0) >= CAPACITY['raw']:
            result['raw'].append(MaterialItem(**material))

    # Check manufactured materials
    for material in materials_event.get('Manufactured', []):
        if material.get('Count', 0) >= CAPACITY['manufactured']:
            result['manufactured'].append(MaterialItem(**material))

    # Check encoded materials
    for material in materials_event.get('Encoded', []):
        if material.get('Count', 0) >= CAPACITY['encoded']:
            result['encoded'].append(MaterialItem(**material))

    return result


@router.get(
    '/low-stock',
    summary="Get Low Stock Materials",
    description=desc.MATERIALS_LOW_STOCK
)
async def get_low_stock_materials(
        request: Request,
        threshold: int = Query(10, ge=1, le=100, description="Count threshold for 'low stock'")
) -> Dict[str, List[MaterialItem]]:
    """
    Get all materials below a specified count threshold.

    Useful for knowing which materials you need to collect.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    result = {
        'raw': [],
        'manufactured': [],
        'encoded': []
    }

    # Check each category
    for material in materials_event.get('Raw', []):
        if material.get('Count', 0) < threshold:
            result['raw'].append(MaterialItem(**material))

    for material in materials_event.get('Manufactured', []):
        if material.get('Count', 0) < threshold:
            result['manufactured'].append(MaterialItem(**material))

    for material in materials_event.get('Encoded', []):
        if material.get('Count', 0) < threshold:
            result['encoded'].append(MaterialItem(**material))

    return result


@router.get(
    '/grade',
    summary="Get Materials by Grade",
    description=desc.MATERIALS_BY_GRADE
)
async def get_materials_by_grade(
        request: Request,
        grade: int = Query(..., ge=1, le=5, description="Material grade (1-5)")
) -> Dict[str, List[MaterialItem]]:
    """
    Get materials filtered by grade/rarity.

    Note: This is a simplified implementation. For full grade detection,
    you would need a material database mapping names to grades.
    """
    json_location = request.app.state.json_location

    materials_event = find_latest_event(json_location, 'Materials')

    if not materials_event:
        raise HTTPException(status_code=404, detail="No materials data found")

    # Simplified grade detection based on naming patterns
    # In production, use a proper material database
    grade_keywords = {
        1: ['basic', 'worn', 'compact', 'standard'],
        2: ['modified', 'flawed', 'irregular', 'salvaged'],
        3: ['refined', 'anomalous', 'unusual', 'cracked'],
        4: ['conductive', 'exquisite', 'unexpected', 'classified'],
        5: ['biotech', 'exceptional', 'proprietary', 'imperial', 'federal']
    }

    keywords = grade_keywords.get(grade, [])

    result = {
        'raw': [],
        'manufactured': [],
        'encoded': []
    }

    for material in materials_event.get('Raw', []):
        name = material.get('Name', '').lower()
        # Raw materials don't have grades in the traditional sense
        result['raw'].append(MaterialItem(**material))

    for material in materials_event.get('Manufactured', []):
        name_loc = material.get('Name_Localised', '').lower()
        if any(keyword in name_loc for keyword in keywords):
            result['manufactured'].append(MaterialItem(**material))

    for material in materials_event.get('Encoded', []):
        name_loc = material.get('Name_Localised', '').lower()
        if any(keyword in name_loc for keyword in keywords):
            result['encoded'].append(MaterialItem(**material))

    return result