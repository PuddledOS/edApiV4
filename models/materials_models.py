from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# 1. BASIC MATERIAL ITEM
class MaterialItem(BaseModel):
    """
    Individual material item.

    Represents a single material with its name and count.
    """
    Name: str  # Internal name (e.g., "iron", "shieldemitters")
    Name_Localised: Optional[str] = None  # Display name (e.g., "Iron", "Shield Emitters")
    Count: int  # Current quantity


# Example data:
# {
#     "Name": "iron",
#     "Count": 172
# }
#
# {
#     "Name": "shieldemitters",
#     "Name_Localised": "Shield Emitters",
#     "Count": 250
# }


# 2. COMPLETE MATERIALS INVENTORY
class MaterialsResponse(BaseModel):
    """
    Response for complete materials inventory.

    GET /materials/inventory
    """
    Raw: List[MaterialItem]  # All raw materials (elements)
    Manufactured: List[MaterialItem]  # All manufactured materials
    Encoded: List[MaterialItem]  # All encoded data materials
    timestamp: Optional[str] = None  # When this data was recorded


# Example full response:
# {
#     "Raw": [
#         {"Name": "iron", "Count": 172},
#         {"Name": "nickel", "Count": 101},
#         {"Name": "carbon", "Count": 300}
#     ],
#     "Manufactured": [
#         {
#             "Name": "shieldemitters",
#             "Name_Localised": "Shield Emitters",
#             "Count": 250
#         },
#         {
#             "Name": "focuscrystals",
#             "Name_Localised": "Focus Crystals",
#             "Count": 28
#         }
#     ],
#     "Encoded": [
#         {
#             "Name": "emissiondata",
#             "Name_Localised": "Unexpected Emission Data",
#             "Count": 44
#         }
#     ],
#     "timestamp": "2025-12-12T10:57:46Z"
# }


# 3. CATEGORY STATISTICS
class MaterialCategoryStats(BaseModel):
    """
    Statistics for a single material category.

    Used within MaterialsSummaryResponse.
    """
    total_types: int  # Number of different material types you have
    total_count: int  # Sum of all materials in this category
    capacity: int  # Maximum possible storage (types × max_per_type)
    usage_percent: float  # Percentage of capacity used
    at_capacity: int  # Number of materials at maximum (300 or 250)
    near_capacity: int  # Number within 10% of maximum


# Example data:
# {
#     "total_types": 21,      # You have 21 different raw materials
#     "total_count": 1456,    # Total of 1456 raw material units
#     "capacity": 6300,       # 21 types × 300 max = 6300 capacity
#     "usage_percent": 23.11, # Using 23.11% of available space
#     "at_capacity": 1,       # 1 material is at 300/300
#     "near_capacity": 2      # 2 materials are at 270-299
# }


# 4. SUMMARY OF ALL MATERIALS
class MaterialsSummaryResponse(BaseModel):
    """
    Summary statistics for all material categories.

    GET /materials/summary
    """
    raw: MaterialCategoryStats  # Raw materials stats
    manufactured: MaterialCategoryStats  # Manufactured materials stats
    encoded: MaterialCategoryStats  # Encoded materials stats
    total_materials: int  # Total units across all categories
    total_capacity: int  # Total possible storage
    overall_usage_percent: float  # Overall percentage used


# Example full response:
# {
#     "raw": {
#         "total_types": 21,
#         "total_count": 1456,
#         "capacity": 6300,
#         "usage_percent": 23.11,
#         "at_capacity": 1,
#         "near_capacity": 2
#     },
#     "manufactured": {
#         "total_types": 48,
#         "total_count": 2654,
#         "capacity": 12000,
#         "usage_percent": 22.12,
#         "at_capacity": 3,
#         "near_capacity": 5
#     },
#     "encoded": {
#         "total_types": 35,
#         "total_count": 725,
#         "capacity": 10500,
#         "usage_percent": 6.90,
#         "at_capacity": 0,
#         "near_capacity": 1
#     },
#     "total_materials": 4835,      # Sum of all material units
#     "total_capacity": 28800,      # Sum of all possible storage
#     "overall_usage_percent": 16.78 # 4835/28800 = 16.78%
# }


# 5. MATERIAL SEARCH RESULT
class MaterialSearchResult(BaseModel):
    """
    Result when searching for a specific material.

    GET /materials/search?name=iron
    """
    name: str  # Internal material name
    name_localised: Optional[str] = None  # Display name (if available)
    category: str  # "raw", "manufactured", or "encoded"
    count: int  # Current quantity
    max_capacity: int  # Maximum for this category (300/250/300)
    at_max: bool  # Whether at maximum capacity
    percentage: float  # Percentage of max (count/max × 100)

# Example responses:

# Searching for "iron":
# {
#     "name": "iron",
#     "name_localised": null,
#     "category": "raw",
#     "count": 172,
#     "max_capacity": 300,
#     "at_max": false,
#     "percentage": 57.33
# }

# Searching for "shield":
# {
#     "name": "shieldemitters",
#     "name_localised": "Shield Emitters",
#     "category": "manufactured",
#     "count": 250,
#     "max_capacity": 250,
#     "at_max": true,
#     "percentage": 100.0
# }

# Searching for "emission":
# {
#     "name": "emissiondata",
#     "name_localised": "Unexpected Emission Data",
#     "category": "encoded",
#     "count": 44,
#     "max_capacity": 300,
#     "at_max": false,
#     "percentage": 14.67
# }