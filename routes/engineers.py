from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional
import logging

from models.engineers_models import (
    EngineersResponse,
    EngineerItem,
    EngineersSummaryResponse,
    EngineerSearchResult
)
from utils.journal import find_latest_event
import lang.descriptions_en as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/engineers", tags=["engineers"])


@router.get(
    '/progress',
    response_model=EngineersResponse,
    summary="Get Engineers Progress",
    description=desc.ENGINEERS_PROGRESS
)
async def get_engineers_progress(request: Request):
    """
    Get complete engineer progress information.

    Returns all engineers with their unlock status, rank, and progress.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    try:
        return EngineersResponse(
            Engineers=[EngineerItem(**eng) for eng in engineers_event.get('Engineers', [])],
            timestamp=engineers_event.get('timestamp')
        )
    except Exception as e:
        logger.error(f"Error parsing engineer data: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing engineers: {str(e)}")


@router.get(
    '/summary',
    response_model=EngineersSummaryResponse,
    summary="Get Engineers Summary",
    description=desc.ENGINEERS_SUMMARY
)
async def get_engineers_summary(request: Request):
    """
    Get summary statistics for all engineers.

    Returns counts by status and average rank information.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    try:
        engineers = engineers_event.get('Engineers', [])

        total = len(engineers)
        known = sum(1 for e in engineers if e.get('Progress') == 'Known')
        invited = sum(1 for e in engineers if e.get('Progress') == 'Invited')
        unlocked = sum(1 for e in engineers if e.get('Progress') == 'Unlocked')
        barred = sum(1 for e in engineers if e.get('Progress') == 'Barred')

        max_rank_engineers = sum(1 for e in engineers if e.get('Rank') == 5)

        # Calculate average rank of unlocked engineers
        unlocked_engineers = [e for e in engineers if e.get('Progress') == 'Unlocked' and e.get('Rank')]
        average_rank = sum(e.get('Rank', 0) for e in unlocked_engineers) / len(
            unlocked_engineers) if unlocked_engineers else 0

        return EngineersSummaryResponse(
            total_engineers=total,
            known=known,
            invited=invited,
            unlocked=unlocked,
            barred=barred,
            max_rank_engineers=max_rank_engineers,
            average_rank=round(average_rank, 2)
        )

    except Exception as e:
        logger.error(f"Error calculating engineer summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")


@router.get(
    '/unlocked',
    summary="Get Unlocked Engineers",
    description=desc.ENGINEERS_UNLOCKED
)
async def get_unlocked_engineers(request: Request) -> List[EngineerItem]:
    """
    Get all engineers that have been unlocked.

    Returns only engineers with "Unlocked" status.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    unlocked = [EngineerItem(**e) for e in engineers if e.get('Progress') == 'Unlocked']

    return unlocked


@router.get(
    '/invited',
    summary="Get Invited Engineers",
    description=desc.ENGINEERS_INVITED
)
async def get_invited_engineers(request: Request) -> List[EngineerItem]:
    """
    Get all engineers that have sent invitations.

    Returns engineers with "Invited" status - ready to be unlocked.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    invited = [EngineerItem(**e) for e in engineers if e.get('Progress') == 'Invited']

    return invited


@router.get(
    '/known',
    summary="Get Known Engineers",
    description=desc.ENGINEERS_KNOWN
)
async def get_known_engineers(request: Request) -> List[EngineerItem]:
    """
    Get all engineers that are known but not yet unlocked.

    Returns engineers with "Known" status - requirements not yet met.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    known = [EngineerItem(**e) for e in engineers if e.get('Progress') == 'Known']

    return known


@router.get(
    '/max-rank',
    summary="Get Max Rank Engineers",
    description=desc.ENGINEERS_MAX_RANK
)
async def get_max_rank_engineers(request: Request) -> List[EngineerItem]:
    """
    Get all engineers at maximum rank (5).

    Returns unlocked engineers who have reached Grade 5 access.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    max_rank = [EngineerItem(**e) for e in engineers if e.get('Rank') == 5]

    return max_rank


@router.get(
    '/search',
    response_model=EngineerSearchResult,
    summary="Search for Engineer",
    description=desc.ENGINEERS_SEARCH
)
async def search_engineer(
        request: Request,
        name: str = Query(..., description="Engineer name (case-insensitive, partial match)")
):
    """
    Search for a specific engineer by name.

    Returns detailed information including rank progress and status.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    name_lower = name.lower()
    engineers = engineers_event.get('Engineers', [])

    for engineer in engineers:
        eng_name = engineer.get('Engineer', '').lower()

        if name_lower in eng_name:
            rank = engineer.get('Rank')
            rank_progress = engineer.get('RankProgress')
            is_unlocked = engineer.get('Progress') == 'Unlocked'
            is_max_rank = rank == 5
            next_rank = rank + 1 if rank and rank < 5 else None

            return EngineerSearchResult(
                Engineer=engineer.get('Engineer'),
                EngineerID=engineer.get('EngineerID'),
                Progress=engineer.get('Progress'),
                Rank=rank,
                RankProgress=rank_progress,
                next_rank=next_rank,
                is_unlocked=is_unlocked,
                is_max_rank=is_max_rank
            )

    raise HTTPException(status_code=404, detail=f"Engineer '{name}' not found")


@router.get(
    '/by-rank',
    summary="Get Engineers by Rank",
    description=desc.ENGINEERS_BY_RANK
)
async def get_engineers_by_rank(
        request: Request,
        rank: int = Query(..., ge=1, le=5, description="Engineer rank (1-5)")
) -> List[EngineerItem]:
    """
    Get all engineers at a specific rank.

    Returns only unlocked engineers at the specified grade level.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    at_rank = [EngineerItem(**e) for e in engineers if e.get('Rank') == rank]

    return at_rank


@router.get(
    '/in-progress',
    summary="Get Engineers In Progress",
    description=desc.ENGINEERS_IN_PROGRESS
)
async def get_engineers_in_progress(request: Request) -> List[EngineerItem]:
    """
    Get engineers currently being ranked up.

    Returns unlocked engineers below rank 5 with their progress percentage.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    in_progress = [
        EngineerItem(**e) for e in engineers
        if e.get('Progress') == 'Unlocked' and e.get('Rank', 0) < 5
    ]

    # Sort by rank progress descending (closest to next rank first)
    in_progress.sort(key=lambda x: (x.Rank or 0, x.RankProgress or 0), reverse=True)

    return in_progress


@router.get(
    '/statistics',
    summary="Get Detailed Engineer Statistics",
    description=desc.ENGINEERS_STATISTICS
)
async def get_engineer_statistics(request: Request) -> Dict:
    """
    Get detailed statistics about engineer progress.

    Returns comprehensive breakdown including completion percentages.
    """
    json_location = request.app.state.json_location

    engineers_event = find_latest_event(json_location, 'EngineerProgress')

    if not engineers_event:
        raise HTTPException(status_code=404, detail="No engineer progress data found")

    engineers = engineers_event.get('Engineers', [])
    total = len(engineers)

    # Count by status
    known = sum(1 for e in engineers if e.get('Progress') == 'Known')
    invited = sum(1 for e in engineers if e.get('Progress') == 'Invited')
    unlocked = sum(1 for e in engineers if e.get('Progress') == 'Unlocked')
    barred = sum(1 for e in engineers if e.get('Progress') == 'Barred')

    # Rank distribution
    rank_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for eng in engineers:
        rank = eng.get('Rank')
        if rank:
            rank_distribution[rank] += 1

    # Calculate percentages
    unlock_percent = (unlocked / total * 100) if total > 0 else 0
    max_rank_count = rank_distribution[5]
    max_rank_percent = (max_rank_count / unlocked * 100) if unlocked > 0 else 0

    # Average progress
    unlocked_engineers = [e for e in engineers if e.get('Progress') == 'Unlocked']
    total_rank_progress = sum(
        (e.get('Rank', 0) - 1) * 100 + e.get('RankProgress', 0)
        for e in unlocked_engineers
    )
    max_possible_progress = len(unlocked_engineers) * 500  # 5 ranks × 100%
    overall_progress_percent = (total_rank_progress / max_possible_progress * 100) if max_possible_progress > 0 else 0

    return {
        "total_engineers": total,
        "status_breakdown": {
            "known": known,
            "invited": invited,
            "unlocked": unlocked,
            "barred": barred
        },
        "percentages": {
            "unlocked_percent": round(unlock_percent, 2),
            "max_rank_percent": round(max_rank_percent, 2)
        },
        "rank_distribution": rank_distribution,
        "progress": {
            "engineers_at_max": max_rank_count,
            "engineers_in_progress": unlocked - max_rank_count,
            "overall_progress_percent": round(overall_progress_percent, 2)
        }
    }