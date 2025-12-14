# Elite Dangerous API Server

A FastAPI-based background service for accessing Elite Dangerous game data through a REST API.

** still very much a work in progress **

## Features

- Real-time game status monitoring
- Cargo and market data access
- Event and message tracking
- Exploration Data including first discoveries
- Biological data from completed scans
- Ship Loadouts and specs
- Inventory of materials
- Track Engineers status
- Construction site monitoring
- Keyboard control (optional)
- Historical data export
- System tray integration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

3. On first run, edit the generated `cfg.json` file with your Elite Dangerous log file location.

## Configuration

Edit `cfg.json`:

```json
{
    "json_location": "C:/Users/YourName/Saved Games/Frontier Developments/Elite Dangerous",
    "host": "0.0.0.0",
    "port": 5000,
    "workers": 3,
    "debug": false,
    "output_directory": "C:/Users/YourName/Desktop",
    "allowed_origins": ["*"],
    "enable_keyboard_control": true
}
```

## API Documentation

Once running, visit `http://localhost:5000/docs` for interactive API documentation.

## Security Notes

- Change `allowed_origins` in production
- Disable `enable_keyboard_control` if not needed
- Consider adding authentication for sensitive endpoints
