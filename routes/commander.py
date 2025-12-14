from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Dict, Optional, Any
import logging

from models.commander_models import (
    CommanderRank,
    CommanderProgress,
    CommanderReputation,
    CommanderStatus,
    RankHistory,
    ProgressHistory,
    ReputationHistory
)
from utils.journal import (
    get_latest_journal_file,
    get_all_journal_files,
    parse_journal_line
)
import lang.descriptions_en as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/commander", tags=["commander"])


@router.get(
    '/current-status',
    response_model=CommanderStatus,
    summary="Get Current Commander Status",
    description="Get current rank, progress, and reputation for the commander"
)
async def get_current_commander_status(request: Request):
    """
    Get the most recent rank, progress, and reputation data.

    Returns the latest status from the current journal file.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    latest_rank = None
    latest_progress = None
    latest_reputation = None
    timestamp = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                event = data.get('event')

                if event == 'Rank':
                    latest_rank = CommanderRank(
                        timestamp=data.get('timestamp'),
                        combat=data.get('Combat', 0),
                        trade=data.get('Trade', 0),
                        explore=data.get('Explore', 0),
                        soldier=data.get('Soldier', 0),
                        exobiologist=data.get('Exobiologist', 0),
                        empire=data.get('Empire', 0),
                        federation=data.get('Federation', 0),
                        cqc=data.get('CQC', 0)
                    )
                    timestamp = data.get('timestamp')

                elif event == 'Progress':
                    latest_progress = CommanderProgress(
                        timestamp=data.get('timestamp'),
                        combat=data.get('Combat', 0),
                        trade=data.get('Trade', 0),
                        explore=data.get('Explore', 0),
                        soldier=data.get('Soldier', 0),
                        exobiologist=data.get('Exobiologist', 0),
                        empire=data.get('Empire', 0),
                        federation=data.get('Federation', 0),
                        cqc=data.get('CQC', 0)
                    )

                elif event == 'Reputation':
                    latest_reputation = CommanderReputation(
                        timestamp=data.get('timestamp'),
                        empire=data.get('Empire', 0.0),
                        federation=data.get('Federation', 0.0),
                        independent=data.get('Independent', 0.0),
                        alliance=data.get('Alliance', 0.0)
                    )

        if not latest_rank and not latest_progress and not latest_reputation:
            raise HTTPException(status_code=404, detail="No commander status found in journal")

        return CommanderStatus(
            timestamp=timestamp,
            rank=latest_rank,
            progress=latest_progress,
            reputation=latest_reputation
        )

    except Exception as e:
        logger.error(f"Error getting commander status: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/rank',
    response_model=CommanderRank,
    summary="Get Current Ranks",
    description="Get current rank levels across all categories"
)
async def get_current_rank(request: Request):
    """
    Get the most recent rank data.

    Returns rank levels for Combat, Trade, Exploration, Soldier, Exobiologist,
    Empire, Federation, and CQC.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    latest_rank = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'Rank':
                    latest_rank = CommanderRank(
                        timestamp=data.get('timestamp'),
                        combat=data.get('Combat', 0),
                        trade=data.get('Trade', 0),
                        explore=data.get('Explore', 0),
                        soldier=data.get('Soldier', 0),
                        exobiologist=data.get('Exobiologist', 0),
                        empire=data.get('Empire', 0),
                        federation=data.get('Federation', 0),
                        cqc=data.get('CQC', 0)
                    )

        if not latest_rank:
            raise HTTPException(status_code=404, detail="No rank data found")

        return latest_rank

    except Exception as e:
        logger.error(f"Error getting rank: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/progress',
    response_model=CommanderProgress,
    summary="Get Current Progress",
    description="Get current progress percentages toward next rank"
)
async def get_current_progress(request: Request):
    """
    Get the most recent progress data.

    Returns progress percentages (0-100) toward the next rank level
    for each category.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    latest_progress = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'Progress':
                    latest_progress = CommanderProgress(
                        timestamp=data.get('timestamp'),
                        combat=data.get('Combat', 0),
                        trade=data.get('Trade', 0),
                        explore=data.get('Explore', 0),
                        soldier=data.get('Soldier', 0),
                        exobiologist=data.get('Exobiologist', 0),
                        empire=data.get('Empire', 0),
                        federation=data.get('Federation', 0),
                        cqc=data.get('CQC', 0)
                    )

        if not latest_progress:
            raise HTTPException(status_code=404, detail="No progress data found")

        return latest_progress

    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/reputation',
    response_model=CommanderReputation,
    summary="Get Current Reputation",
    description="Get current reputation with major powers"
)
async def get_current_reputation(request: Request):
    """
    Get the most recent reputation data.

    Returns reputation percentages with Empire, Federation, Independent,
    and Alliance factions.
    """
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    latest_reputation = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'Reputation':
                    latest_reputation = CommanderReputation(
                        timestamp=data.get('timestamp'),
                        empire=data.get('Empire', 0.0),
                        federation=data.get('Federation', 0.0),
                        independent=data.get('Independent', 0.0),
                        alliance=data.get('Alliance', 0.0)
                    )

        if not latest_reputation:
            raise HTTPException(status_code=404, detail="No reputation data found")

        return latest_reputation

    except Exception as e:
        logger.error(f"Error getting reputation: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/rank-history',
    response_model=RankHistory,
    summary="Get Rank History",
    description="Get historical rank progression"
)
async def get_rank_history(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get historical rank progression over time.

    Returns all rank events showing progression through ranks.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    rank_events = []

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    if data.get('event') == 'Rank':
                        rank = CommanderRank(
                            timestamp=data.get('timestamp'),
                            combat=data.get('Combat', 0),
                            trade=data.get('Trade', 0),
                            explore=data.get('Explore', 0),
                            soldier=data.get('Soldier', 0),
                            exobiologist=data.get('Exobiologist', 0),
                            empire=data.get('Empire', 0),
                            federation=data.get('Federation', 0),
                            cqc=data.get('CQC', 0)
                        )
                        rank_events.append(rank)

        # Sort by timestamp
        rank_events.sort(key=lambda x: x.timestamp if x.timestamp else '')

        return RankHistory(
            total_events=len(rank_events),
            earliest_timestamp=rank_events[0].timestamp if rank_events else None,
            latest_timestamp=rank_events[-1].timestamp if rank_events else None,
            current_rank=rank_events[-1] if rank_events else None,
            history=rank_events
        )

    except Exception as e:
        logger.error(f"Error getting rank history: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/progress-history',
    response_model=ProgressHistory,
    summary="Get Progress History",
    description="Get historical progress tracking"
)
async def get_progress_history(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get historical progress data over time.

    Returns all progress events showing advancement toward ranks.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    progress_events = []

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    if data.get('event') == 'Progress':
                        progress = CommanderProgress(
                            timestamp=data.get('timestamp'),
                            combat=data.get('Combat', 0),
                            trade=data.get('Trade', 0),
                            explore=data.get('Explore', 0),
                            soldier=data.get('Soldier', 0),
                            exobiologist=data.get('Exobiologist', 0),
                            empire=data.get('Empire', 0),
                            federation=data.get('Federation', 0),
                            cqc=data.get('CQC', 0)
                        )
                        progress_events.append(progress)

        # Sort by timestamp
        progress_events.sort(key=lambda x: x.timestamp if x.timestamp else '')

        return ProgressHistory(
            total_events=len(progress_events),
            earliest_timestamp=progress_events[0].timestamp if progress_events else None,
            latest_timestamp=progress_events[-1].timestamp if progress_events else None,
            current_progress=progress_events[-1] if progress_events else None,
            history=progress_events
        )

    except Exception as e:
        logger.error(f"Error getting progress history: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/reputation-history',
    response_model=ReputationHistory,
    summary="Get Reputation History",
    description="Get historical reputation tracking"
)
async def get_reputation_history(
        request: Request,
        scan_all_logs: bool = Query(False, description="Scan all journal files")
):
    """
    Get historical reputation data over time.

    Returns all reputation events showing changes with major powers.
    """
    json_location = request.app.state.json_location

    if scan_all_logs:
        journal_files = get_all_journal_files(json_location)
    else:
        latest = get_latest_journal_file(json_location)
        journal_files = [latest] if latest else []

    if not journal_files:
        raise HTTPException(status_code=404, detail="No journal files found")

    reputation_events = []

    try:
        for journal_file in journal_files:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if not data:
                        continue

                    if data.get('event') == 'Reputation':
                        reputation = CommanderReputation(
                            timestamp=data.get('timestamp'),
                            empire=data.get('Empire', 0.0),
                            federation=data.get('Federation', 0.0),
                            independent=data.get('Independent', 0.0),
                            alliance=data.get('Alliance', 0.0)
                        )
                        reputation_events.append(reputation)

        # Sort by timestamp
        reputation_events.sort(key=lambda x: x.timestamp if x.timestamp else '')

        return ReputationHistory(
            total_events=len(reputation_events),
            earliest_timestamp=reputation_events[0].timestamp if reputation_events else None,
            latest_timestamp=reputation_events[-1].timestamp if reputation_events else None,
            current_reputation=reputation_events[-1] if reputation_events else None,
            history=reputation_events
        )

    except Exception as e:
        logger.error(f"Error getting reputation history: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get(
    '/rank-names',
    summary="Get Rank Names",
    description="Get human-readable rank names for current rank levels"
)
async def get_rank_names(request: Request) -> Dict[str, Any]:
    """
    Get human-readable rank names for the current rank levels.

    Converts numerical rank values to their corresponding rank titles.
    """
    # Rank name mappings
    COMBAT_RANKS = ["Harmless", "Mostly Harmless", "Novice", "Competent", "Expert",
                    "Master", "Dangerous", "Deadly", "Elite", "Elite I", "Elite II", "Elite III"]
    TRADE_RANKS = ["Penniless", "Mostly Penniless", "Peddler", "Dealer", "Merchant",
                   "Broker", "Entrepreneur", "Tycoon", "Elite", "Elite I", "Elite II", "Elite III"]
    EXPLORE_RANKS = ["Aimless", "Mostly Aimless", "Scout", "Surveyor", "Trailblazer",
                     "Pathfinder", "Ranger", "Pioneer", "Elite", "Elite I", "Elite II", "Elite III"]
    SOLDIER_RANKS = ["Defenceless", "Mostly Defenceless", "Rookie", "Soldier", "Gunslinger",
                     "Warrior", "Gladiator", "Deadeye", "Elite", "Elite I", "Elite II", "Elite III"]
    EXOBIOLOGIST_RANKS = ["Directionless", "Mostly Directionless", "Compiler", "Collector", "Cataloguer",
                          "Taxonomist", "Ecologist", "Geneticist", "Elite", "Elite I", "Elite II", "Elite III"]
    EMPIRE_RANKS = ["None", "Outsider", "Serf", "Master", "Squire", "Knight", "Lord",
                    "Baron", "Viscount", "Count", "Earl", "Marquis", "Duke", "Prince", "King"]
    FEDERATION_RANKS = ["None", "Recruit", "Cadet", "Midshipman", "Petty Officer", "Chief Petty Officer",
                        "Warrant Officer", "Ensign", "Lieutenant", "Lieutenant Commander", "Post Commander",
                        "Post Captain", "Rear Admiral", "Vice Admiral", "Admiral"]
    CQC_RANKS = ["Helpless", "Mostly Helpless", "Amateur", "Semi Professional", "Professional",
                 "Champion", "Hero", "Legend", "Elite", "Elite I", "Elite II", "Elite III"]

    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    latest_rank = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'Rank':
                    latest_rank = data
                    break

        if not latest_rank:
            raise HTTPException(status_code=404, detail="No rank data found")

        def get_rank_name(rank_list, rank_value):
            return rank_list[rank_value] if 0 <= rank_value < len(rank_list) else "Unknown"

        return {
            "timestamp": latest_rank.get('timestamp'),
            "ranks": {
                "combat": {
                    "level": latest_rank.get('Combat', 0),
                    "name": get_rank_name(COMBAT_RANKS, latest_rank.get('Combat', 0))
                },
                "trade": {
                    "level": latest_rank.get('Trade', 0),
                    "name": get_rank_name(TRADE_RANKS, latest_rank.get('Trade', 0))
                },
                "explore": {
                    "level": latest_rank.get('Explore', 0),
                    "name": get_rank_name(EXPLORE_RANKS, latest_rank.get('Explore', 0))
                },
                "soldier": {
                    "level": latest_rank.get('Soldier', 0),
                    "name": get_rank_name(SOLDIER_RANKS, latest_rank.get('Soldier', 0))
                },
                "exobiologist": {
                    "level": latest_rank.get('Exobiologist', 0),
                    "name": get_rank_name(EXOBIOLOGIST_RANKS, latest_rank.get('Exobiologist', 0))
                },
                "empire": {
                    "level": latest_rank.get('Empire', 0),
                    "name": get_rank_name(EMPIRE_RANKS, latest_rank.get('Empire', 0))
                },
                "federation": {
                    "level": latest_rank.get('Federation', 0),
                    "name": get_rank_name(FEDERATION_RANKS, latest_rank.get('Federation', 0))
                },
                "cqc": {
                    "level": latest_rank.get('CQC', 0),
                    "name": get_rank_name(CQC_RANKS, latest_rank.get('CQC', 0))
                }
            }
        }

    except Exception as e:
        logger.error(f"Error getting rank names: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")