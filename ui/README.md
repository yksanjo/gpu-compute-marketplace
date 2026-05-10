# UI Dashboard

## Overview

This directory contains the web-based UI dashboard for the GPU Compute Marketplace Platform.

## Files

- `dashboard.html` - Interactive web dashboard with real-time updates

## Running the Dashboard

### Option 1: Open Directly in Browser

```bash
# Simply open the HTML file in your browser
open ui/dashboard.html
# or
xdg-open ui/dashboard.html  # Linux
start ui/dashboard.html     # Windows
```

### Option 2: Using Python HTTP Server

```bash
cd ui
python3 -m http.server 8000
# Then open http://localhost:8000/dashboard.html in your browser
```

### Option 3: Using Node.js HTTP Server

```bash
cd ui
npx http-server -p 8000
# Then open http://localhost:8000/dashboard.html in your browser
```

## Features

The dashboard includes:

1. **Token Balance Display**
   - Current balance
   - Active vs reserved tokens
   - Real-time updates

2. **Platform Statistics**
   - Available resources
   - Active jobs
   - Platform utilization
   - Total transactions

3. **Resource Browser**
   - List of available GPU resources
   - Price per hour
   - Location and tier information
   - Availability status

4. **Quick Actions**
   - Purchase tokens
   - Submit compute jobs
   - Select GPU type and duration

5. **Job Management**
   - View your jobs
   - Job status (queued, running, completed)
   - Token consumption

## Simulating the Platform

See `../simulator/demo.py` for a command-line simulation of the trading platform.

## Future Enhancements

- Connect to backend API
- Real-time WebSocket updates
- Advanced filtering and search
- Job monitoring and logs
- Token transaction history
- Resource comparison charts








