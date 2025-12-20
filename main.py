import sys
import time
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path
from importlib import import_module
import uvicorn
import tkinter as tk
from tkinter import messagebox
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pystray import Icon, Menu, MenuItem
from PIL import Image
from config import load_config, Config
from models.main_models import MainStatusResponse, MainRootResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_routes():
    """Dynamically load all route modules from the routes directory."""
    routes_dir = Path(__file__).parent / "routes"
    routers = []

    if not routes_dir.exists():
        logger.warning(f"Routes directory not found: {routes_dir}")
        return routers

    # Get all Python files in routes directory
    route_files = sorted(routes_dir.glob("*.py"))

    for route_file in route_files:
        # Skip __init__.py and private modules
        if route_file.name.startswith("_"):
            continue

        module_name = route_file.stem

        try:
            # Import the module
            module = import_module(f"routes.{module_name}")

            # Check if module has a 'router' attribute
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                routers.append((module_name, module.router))
                logger.info(f"Loaded route module: {module_name}")
            else:
                logger.debug(f"Skipping {module_name}: no router found")

        except Exception as e:
            logger.error(f"Failed to load route module {module_name}: {e}")

    return routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Elite Dangerous API starting up...")
    logger.info(f"Using log location: {app.state.json_location}")
    logger.info(f"API Language: {app.state.config.language}")

    yield


# Initialize FastAPI app
app = FastAPI(
    title="Elite Dangerous API",
    description="API for accessing Elite Dangerous game data",
    version="2.0.0",
    lifespan=lifespan,
    openapi_url="/openapi.json"
)


@app.get("/", response_model=MainRootResponse)
async def root():
    """Root endpoint."""
    return MainRootResponse(
        message="Elite Dangerous API",
        version="2.0.0",
        language=app.state.config.language,
        docs="/docs",
        status="running"
    )


@app.get("/api_health", response_model=MainStatusResponse)
async def health_check():
    """Health check endpoint."""
    return MainStatusResponse(
        health="healthy"
    )


def setup_app(config: Config):
    """Setup the FastAPI application with configuration."""
    # Store config and json location in app.state
    json_location = config.json_location if not config.debug else config.json_test_location
    app.state.config = config
    app.state.json_location = json_location
    app.state.server_running = False

    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Dynamically load and include all routers
    routers = load_routes()
    for module_name, router in routers:
        app.include_router(router)
        logger.info(f"Registered router: {module_name}")

    logger.info(f"Application setup complete with {len(routers)} route modules")


def run_server(config: Config):
    """Run the FastAPI server."""
    app.state.server_running = True
    uvicorn_config = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        workers=1,  # Must be 1 when running in thread
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)
    server.run()


# System tray functions
def create_tray_image():
    """Create system tray icon image."""
    try:
        return Image.open('icon_running.png')
    except FileNotFoundError:
        # Create a simple fallback icon
        image = Image.new('RGB', (64, 64), color='green')
        return image


def on_open_browser(icon, item):
    """Open browser to API docs."""
    port = app.state.config.port
    import webbrowser
    webbrowser.open(f"http://localhost:{port}/docs")


def on_show_status(icon, item):
    """Show server status dialog."""
    root = tk.Tk()
    root.withdraw()

    if app.state.server_running:
        config = app.state.config
        status_msg = (
            f"Server Status: Running ✓\n\n"
            f"Host: {config.host}\n"
            f"Port: {config.port}\n"
            f"URL: http://{config.host}:{config.port}\n"
            f"Docs: http://{config.host}:{config.port}/docs\n\n"
            f"Log Location: {app.state.json_location}"
        )
        messagebox.showinfo("ED API Server Status", status_msg)
    else:
        messagebox.showwarning("ED API Server Status", "Server is not running ✗")

    root.destroy()


def on_show_about(icon, item):
    """Show about dialog."""
    root = tk.Tk()
    root.withdraw()

    about_msg = (
        "Elite Dangerous API Server\n\n"
        "Version: 2.0.0\n"
        "Framework: FastAPI + Uvicorn\n\n"
        "A background API service for retrieving\n"
        "Elite Dangerous game data for use in\n"
        "external applications and tools.\n\n"
        "Author: Cmdr Puddled"
    )
    messagebox.showinfo("About", about_msg)
    root.destroy()


def on_quit(icon, item):
    """Quit the application."""
    logger.info("Shutting down...")
    icon.stop()
    sys.exit(0)


def setup_tray():
    """Setup system tray icon."""
    image = create_tray_image()

    menu = Menu(
        MenuItem("Open API Docs", on_open_browser),
        MenuItem("Show Status", on_show_status),
        Menu.SEPARATOR,
        MenuItem("About", on_show_about),
        Menu.SEPARATOR,
        MenuItem("Quit", on_quit)
    )

    icon = Icon("ED API Server", image, "ED API Server Running", menu)
    icon.run()


def main():
    """Main entry point."""
    # Load configuration
    config = load_config()

    # Setup application
    setup_app(config)

    # Start server in background thread
    server_thread = threading.Thread(target=run_server, args=(config,), daemon=True)
    server_thread.start()

    # Give server time to start
    time.sleep(1)
    logger.info(f"Server started at http://{config.host}:{config.port}")
    logger.info(f"API Documentation available at http://{config.host}:{config.port}/docs")

    # Run system tray (blocks until quit)
    setup_tray()


if __name__ == "__main__":
    main()