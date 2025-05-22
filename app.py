import asyncio
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState

from utils.metrics import MetricsCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("system_viewer")

# Initialize FastAPI application
app = FastAPI(
    title="System Viewer",
    description="A web application for monitoring system metrics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates and static files
templates = Jinja2Templates(directory="templates")

# Initialize metrics collector
metrics_collector = MetricsCollector()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    async def broadcast(self, data: Dict[str, Any]):
        """Send data to all connected clients"""
        closed_websockets = []
        for connection in self.active_connections:
            try:
                # Only send if the connection is still open
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending data to WebSocket: {str(e)}")
                closed_websockets.append(connection)
        
        # Clean up closed connections
        for ws in closed_websockets:
            if ws in self.active_connections:
                self.active_connections.remove(ws)

manager = ConnectionManager()

# Background task to collect metrics periodically
async def periodic_metrics_collection():
    """Collect metrics every 5 seconds and broadcast to all connected clients"""
    while True:
        try:
            metrics = metrics_collector.collect_metrics()
            await manager.broadcast(metrics)
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
        
        # Wait 5 seconds before next collection
        await asyncio.sleep(5)

# Start the background task when the application starts
@app.on_event("startup")
async def startup_event():
    """Start the background task for metrics collection"""
    logger.info("Starting System Viewer application")
    asyncio.create_task(periodic_metrics_collection())

# Route for the main dashboard
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the main dashboard page"""
    try:
        # Get initial metrics
        metrics_summary = metrics_collector.get_metrics_summary()
        return templates.TemplateResponse(
            "dashboard.html", 
            {"request": request, "metrics": metrics_summary}
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Routes for specific metric pages
@app.get("/cpu", response_class=HTMLResponse)
async def cpu_metrics(request: Request):
    """Render the CPU metrics page"""
    try:
        return templates.TemplateResponse(
            "cpu.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering CPU page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/memory", response_class=HTMLResponse)
async def memory_metrics(request: Request):
    """Render the memory metrics page"""
    try:
        return templates.TemplateResponse(
            "memory.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering memory page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/disk", response_class=HTMLResponse)
async def disk_metrics(request: Request):
    """Render the disk metrics page"""
    try:
        return templates.TemplateResponse(
            "disk.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering disk page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Route for the about page
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Render the about page"""
    try:
        return templates.TemplateResponse(
            "about.html", 
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering about page: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# API endpoints for metrics data
@app.get("/api/metrics", response_class=JSONResponse)
async def get_all_metrics():
    """Get all current metrics"""
    try:
        metrics = metrics_collector.collect_metrics()
        return JSONResponse(content=metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

@app.get("/api/metrics/cpu", response_class=JSONResponse)
async def get_cpu_metrics():
    """Get CPU metrics"""
    try:
        metrics = metrics_collector.collect_metrics()
        return JSONResponse(content=metrics["cpu"])
    except Exception as e:
        logger.error(f"Error getting CPU metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting CPU metrics: {str(e)}")

@app.get("/api/metrics/memory", response_class=JSONResponse)
async def get_memory_metrics():
    """Get memory metrics"""
    try:
        metrics = metrics_collector.collect_metrics()
        return JSONResponse(content=metrics["memory"])
    except Exception as e:
        logger.error(f"Error getting memory metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting memory metrics: {str(e)}")

@app.get("/api/metrics/disk", response_class=JSONResponse)
async def get_disk_metrics():
    """Get disk metrics"""
    try:
        metrics = metrics_collector.collect_metrics()
        return JSONResponse(content=metrics["disk"])
    except Exception as e:
        logger.error(f"Error getting disk metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting disk metrics: {str(e)}")

@app.get("/api/metrics/history", response_class=JSONResponse)
async def get_metrics_history():
    """Get historical metrics data"""
    try:
        history = metrics_collector.get_history()
        return JSONResponse(content=history)
    except Exception as e:
        logger.error(f"Error getting metrics history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics history: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time metrics updates"""
    await manager.connect(websocket)
    try:
        # Send initial metrics when client connects
        metrics = metrics_collector.collect_metrics()
        await websocket.send_text(json.dumps(metrics))
        
        # Keep connection open and handle disconnects
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

