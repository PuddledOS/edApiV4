from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pathlib import Path
import logging
import uuid
from typing import Dict, Any

from models.export_models import ExportTaskResponse, TaskStatusResponse
from utils.journal import get_all_journal_files, parse_journal_line
from utils.file_utils import write_json_file, ensure_directory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/export", tags=["export"])

# Track export tasks
export_tasks: Dict[str, Dict[str, Any]] = {}


@router.post('/construction-history', response_model=ExportTaskResponse)
async def start_construction_export(request: Request, background_tasks: BackgroundTasks):
    """Start exporting construction history to file."""
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = {"status": "running", "progress": "0%"}

    json_location = request.app.state.json_location
    output_dir = request.app.state.config.output_directory

    background_tasks.add_task(export_construction_history, task_id, json_location, output_dir)

    return ExportTaskResponse(
        task_id=task_id,
        status="started",
        message="Export task started. Check status with /export/status/{task_id}"
    )


@router.post('/organic-history', response_model=ExportTaskResponse)
async def start_organic_export(request: Request, background_tasks: BackgroundTasks):
    """Start exporting organic scan history to file."""
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = {"status": "running", "progress": "0%"}

    json_location = request.app.state.json_location
    output_dir = request.app.state.config.output_directory

    background_tasks.add_task(export_organic_history, task_id, json_location, output_dir)

    return ExportTaskResponse(
        task_id=task_id,
        status="started",
        message="Export task started. Check status with /export/status/{task_id}"
    )


@router.post('/sell-organic-history', response_model=ExportTaskResponse)
async def start_sell_organic_export(request: Request, background_tasks: BackgroundTasks):
    """Start exporting organic sales history to file."""
    task_id = str(uuid.uuid4())
    export_tasks[task_id] = {"status": "running", "progress": "0%"}

    json_location = request.app.state.json_location
    output_dir = request.app.state.config.output_directory

    background_tasks.add_task(export_sell_organic_history, task_id, json_location, output_dir)

    return ExportTaskResponse(
        task_id=task_id,
        status="started",
        message="Export task started. Check status with /export/status/{task_id}"
    )


@router.get('/status/{task_id}', response_model=TaskStatusResponse)
async def get_export_status(task_id: str):
    """Check the status of an export task."""
    if task_id not in export_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = export_tasks[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task.get("progress"),
        error=task.get("error")
    )


def export_construction_history(task_id: str, json_location: Path, output_dir: Path):
    """Export construction history to JSON file."""
    try:
        ensure_directory(output_dir)

        output_file = output_dir / "construction_history.json"
        journal_files = get_all_journal_files(json_location)

        total_files = len(journal_files)
        processed = 0

        for filepath in journal_files:
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        data = parse_journal_line(line)
                        if not data or data.get('event') != 'ColonisationConstructionDepot':
                            continue

                        market_id = data.get('MarketID')
                        resources = data.get('ResourcesRequired', [])
                        complete = data.get('ConstructionComplete', False)

                        # Find station name
                        station_name = 'Unknown'
                        system_name = 'Unknown'

                        with open(filepath, 'r') as f2:
                            for line2 in f2:
                                dock_data = parse_journal_line(line2)
                                if (dock_data and dock_data.get('event') == 'Docked' and
                                        dock_data.get('MarketID') == market_id):
                                    station_name = dock_data.get('StationName', 'Unknown')
                                    station_name = station_name.replace('$EXT_PANEL_ColonisationShip;',
                                                                        'Colonisation Ship : ')
                                    system_name = dock_data.get('StarSystem', 'Unknown')
                                    break

                        result = {
                            "id": market_id,
                            "name": station_name,
                            "complete": complete,
                            "system": system_name,
                            "data": resources
                        }

                        write_json_file(output_file, result, append=True)

                processed += 1
                export_tasks[task_id]["progress"] = f"{int(processed / total_files * 100)}%"

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")

        export_tasks[task_id]["status"] = "completed"
        export_tasks[task_id]["progress"] = "100%"
        logger.info(f"Construction history export completed: {output_file}")

    except Exception as e:
        logger.error(f"Error in construction export: {e}")
        export_tasks[task_id]["status"] = "failed"
        export_tasks[task_id]["error"] = str(e)


def export_organic_history(task_id: str, json_location: Path, output_dir: Path):
    """Export organic scan history to JSON file."""
    try:
        ensure_directory(output_dir)

        output_file = output_dir / "organic_history.json"
        journal_files = get_all_journal_files(json_location)

        total_files = len(journal_files)
        processed = 0

        for filepath in journal_files:
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        data = parse_journal_line(line)
                        if not data or data.get('event') != 'ScanOrganic':
                            continue

                        system_address = data.get('SystemAddress')
                        body_id = data.get('Body')

                        # Find system and body name
                        system_name = ''
                        body_name = ''

                        with open(filepath, 'r') as f2:
                            for line2 in f2:
                                disembark_data = parse_journal_line(line2)
                                if (disembark_data and disembark_data.get('event') == 'Disembark' and
                                        disembark_data.get('SystemAddress') == system_address and
                                        disembark_data.get('BodyID') == body_id):
                                    system_name = disembark_data.get('StarSystem', '')
                                    body_name = disembark_data.get('Body', '')
                                    body_name = body_name.replace(system_name + ' ', '')
                                    break

                        result = {
                            "data": data,
                            "SystemName": system_name,
                            "Body": body_name
                        }

                        write_json_file(output_file, result, append=True)

                processed += 1
                export_tasks[task_id]["progress"] = f"{int(processed / total_files * 100)}%"

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")

        export_tasks[task_id]["status"] = "completed"
        export_tasks[task_id]["progress"] = "100%"
        logger.info(f"Organic history export completed: {output_file}")

    except Exception as e:
        logger.error(f"Error in organic export: {e}")
        export_tasks[task_id]["status"] = "failed"
        export_tasks[task_id]["error"] = str(e)


def export_sell_organic_history(task_id: str, json_location: Path, output_dir: Path):
    """Export organic sales history to JSON file."""
    try:
        ensure_directory(output_dir)

        output_file = output_dir / "sell_organic_history.json"
        journal_files = get_all_journal_files(json_location)

        total_files = len(journal_files)
        processed = 0

        for filepath in journal_files:
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        data = parse_journal_line(line)
                        if data and data.get('event') == 'SellOrganicData':
                            result = {"data": data}
                            write_json_file(output_file, result, append=True)

                processed += 1
                export_tasks[task_id]["progress"] = f"{int(processed / total_files * 100)}%"

            except Exception as e:
                logger.error(f"Error processing {filepath}: {e}")

        export_tasks[task_id]["status"] = "completed"
        export_tasks[task_id]["progress"] = "100%"
        logger.info(f"Sell organic history export completed: {output_file}")

    except Exception as e:
        logger.error(f"Error in sell organic export: {e}")
        export_tasks[task_id]["status"] = "failed"
        export_tasks[task_id]["error"] = str(e)

