from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# 1. BASIC ENGINEER ITEM
class EngineerItem(BaseModel):
    """
    Individual engineer information.

    Represents a single engineer with their unlock status and rank.
    """
    Engineer: str  # Engineer name (e.g., "Felicity Farseer")
    EngineerID: int  # Unique engineer ID
    Progress: str  # "Known", "Invited", "Unlocked", "Barred"
    RankProgress: Optional[int] = None  # 0-100 percentage to next rank (if unlocked)
    Rank: Optional[int] = None  # Current rank 1-5 (only if unlocked)


# Example data:

# Unlocked engineer at max rank:
# {
#     "Engineer": "Felicity Farseer",
#     "EngineerID": 300100,
#     "Progress": "Unlocked",
#     "RankProgress": 0,
#     "Rank": 5
# }

# Unlocked engineer with progress:
# {
#     "Engineer": "Elvira Martuuk",
#     "EngineerID": 300160,
#     "Progress": "Unlocked",
#     "RankProgress": 47,    # 47% to Rank 3
#     "Rank": 2
# }

# Invited engineer (ready to unlock):
# {
#     "Engineer": "Domino Green",
#     "EngineerID": 400002,
#     "Progress": "Invited"
# }

# Known engineer (not yet unlockable):
# {
#     "Engineer": "Liz Ryder",
#     "EngineerID": 300080,
#     "Progress": "Known"
# }


# 2. COMPLETE ENGINEERS PROGRESS
class EngineersResponse(BaseModel):
    """
    Response for all engineers progress.

    GET /engineers/progress
    """
    Engineers: List[EngineerItem]  # List of all engineers
    timestamp: Optional[str] = None  # When this data was recorded


# Example full response:
# {
#     "Engineers": [
#         {
#             "Engineer": "Felicity Farseer",
#             "EngineerID": 300100,
#             "Progress": "Unlocked",
#             "RankProgress": 0,
#             "Rank": 5
#         },
#         {
#             "Engineer": "The Dweller",
#             "EngineerID": 300180,
#             "Progress": "Unlocked",
#             "RankProgress": 0,
#             "Rank": 5
#         },
#         {
#             "Engineer": "Elvira Martuuk",
#             "EngineerID": 300160,
#             "Progress": "Unlocked",
#             "RankProgress": 47,
#             "Rank": 2
#         },
#         {
#             "Engineer": "Domino Green",
#             "EngineerID": 400002,
#             "Progress": "Invited"
#         },
#         {
#             "Engineer": "Liz Ryder",
#             "EngineerID": 300080,
#             "Progress": "Known"
#         }
#     ],
#     "timestamp": "2025-12-12T10:57:46Z"
# }


# 3. ENGINEERS SUMMARY STATISTICS
class EngineersSummaryResponse(BaseModel):
    """
    Summary statistics for engineers.

    GET /engineers/summary
    """
    total_engineers: int  # Total number of engineers
    known: int  # Count with "Known" status
    invited: int  # Count with "Invited" status
    unlocked: int  # Count with "Unlocked" status
    barred: int  # Count with "Barred" status (rare)
    max_rank_engineers: int  # Number of engineers at Rank 5
    average_rank: float  # Average rank of unlocked engineers


# Example response:
# {
#     "total_engineers": 14,
#     "known": 5,              # 5 known but not unlocked
#     "invited": 2,            # 2 ready to unlock
#     "unlocked": 7,           # 7 currently unlocked
#     "barred": 0,             # None barred
#     "max_rank_engineers": 3, # 3 engineers at Rank 5
#     "average_rank": 3.14     # Average rank is 3.14
# }


# 4. ENGINEER SEARCH RESULT
class EngineerSearchResult(BaseModel):
    """
    Result when searching for a specific engineer.

    GET /engineers/search?name=farseer
    """
    Engineer: str  # Engineer name
    EngineerID: int  # Unique ID
    Progress: str  # Current status
    Rank: Optional[int] = None  # Current rank (if unlocked)
    RankProgress: Optional[int] = None  # Progress to next rank (if unlocked)
    next_rank: Optional[int] = None  # Next rank number (None if at rank 5)
    is_unlocked: bool  # Whether engineer is unlocked
    is_max_rank: bool  # Whether at maximum rank (5)

# Example responses:

# Searching for "farseer" (max rank):
# {
#     "Engineer": "Felicity Farseer",
#     "EngineerID": 300100,
#     "Progress": "Unlocked",
#     "Rank": 5,
#     "RankProgress": 0,
#     "next_rank": null,        # No next rank (already at 5)
#     "is_unlocked": true,
#     "is_max_rank": true
# }

# Searching for "martuuk" (in progress):
# {
#     "Engineer": "Elvira Martuuk",
#     "EngineerID": 300160,
#     "Progress": "Unlocked",
#     "Rank": 2,
#     "RankProgress": 47,       # 47% to rank 3
#     "next_rank": 3,
#     "is_unlocked": true,
#     "is_max_rank": false
# }

# Searching for "domino" (invited):
# {
#     "Engineer": "Domino Green",
#     "EngineerID": 400002,
#     "Progress": "Invited",
#     "Rank": null,
#     "RankProgress": null,
#     "next_rank": null,
#     "is_unlocked": false,
#     "is_max_rank": false
# }

# Searching for "ryder" (known):
# {
#     "Engineer": "Liz Ryder",
#     "EngineerID": 300080,
#     "Progress": "Known",
#     "Rank": null,
#     "RankProgress": null,
#     "next_rank": null,
#     "is_unlocked": false,
#     "is_max_rank": false
# }