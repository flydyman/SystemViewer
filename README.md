# System Viewer

A real-time system monitoring web application built with FastAPI and Plotly.js that provides comprehensive insights into your system's performance.

![System Viewer Dashboard](screenshots/dashboard.png)

## Features

- **Real-time Monitoring**: Track CPU, memory, and disk usage with automatic updates every 5 seconds
- **Interactive Graphs**: Visualize system performance trends with dynamic, interactive charts
- **CPU Metrics**: Monitor CPU usage percentage, load averages, and per-core utilization
- **Memory Metrics**: Track RAM usage, available memory, and swap utilization
- **Disk Analytics**: Monitor disk usage across all partitions and I/O statistics
- **Responsive Design**: Access system metrics from any device with a web browser
- **WebSocket Updates**: Receive real-time metric updates without page refreshes
- **JSON API**: Access raw system metrics data via REST API endpoints

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SystemViewer.git
   cd SystemViewer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:
   ```bash
   python app.py
   ```
   Alternatively, you can use Uvicorn directly:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

5. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

## Dependencies

The application requires the following Python packages:

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **psutil**: Cross-platform library for retrieving system information
- **Jinja2**: Template engine for Python
- **plotly**: Interactive visualization library
- **aiofiles**: Handling file operations asynchronously
- **python-multipart**: Support for multipart form data

These dependencies are specified in the `requirements.txt` file and will be installed automatically during setup.

## Usage Guide

### Dashboard

The main dashboard provides an overview of your system's current state, including:
- CPU usage and load averages
- Memory consumption (RAM and swap)
- Disk utilization across partitions

### CPU Page

The CPU page offers detailed metrics about your processor:
- Overall CPU usage percentage
- Per-core utilization
- Historical CPU usage graph
- System load averages (1min, 5min, 15min)

### Memory Page

The memory page provides comprehensive memory statistics:
- RAM usage and availability
- Swap memory usage
- Memory allocation breakdown
- Historical memory usage trends

### Disk Page

The disk page displays detailed storage information:
- Partition table with mount points and file systems
- Space usage per partition with visual indicators
- Disk I/O statistics (read/write operations)
- Per-partition detailed view with usage gauges

### API Endpoints

The application provides JSON API endpoints for programmatic access:

- `/api/metrics`: All system metrics
- `/api/metrics/cpu`: CPU-specific metrics
- `/api/metrics/memory`: Memory-specific metrics
- `/api/metrics/disk`: Disk-specific metrics
- `/api/metrics/history`: Historical data for all metrics

## Development

### Project Structure

```
SystemViewer/
├── app.py                  # Main FastAPI application
├── requirements.txt        # Python dependencies
├── static/                 # Static assets (CSS, JS)
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base template with common layout
│   ├── dashboard.html      # Main dashboard view
│   ├── cpu.html            # CPU metrics page
│   ├── memory.html         # Memory metrics page
│   ├── disk.html           # Disk metrics page
│   ├── about.html          # About page
│   └── includes/           # Reusable template components
│       └── metrics.html    # Metrics visualization components
└── utils/                  # Utility modules
    ├── __init__.py
    └── metrics.py          # System metrics collection logic
```

### Running in Development Mode

For development, use the `--reload` flag with Uvicorn to enable auto-reloading when files change:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Contributing

Contributions are welcome! To contribute to System Viewer:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Configuration Options

The application can be configured through environment variables or by modifying the source code:

| Option | Environment Variable | Default | Description |
|--------|---------------------|---------|-------------|
| Host | `HOST` | 0.0.0.0 | IP address to bind the server to |
| Port | `PORT` | 8000 | Port to run the application on |
| Update Interval | `UPDATE_INTERVAL` | 5 | Metrics update interval in seconds |
| History Size | - | 60 | Number of historical data points to keep |
| Debug Mode | `DEBUG` | False | Enable debug logging |

To set environment variables before running the application:

```bash
export PORT=8080
export UPDATE_INTERVAL=10
python app.py
```

## Screenshots

*Placeholder for screenshots - replace with actual application screenshots*

![Dashboard](screenshots/dashboard.png)
![CPU Metrics](screenshots/cpu.png)
![Memory Metrics](screenshots/memory.png)
![Disk Metrics](screenshots/disk.png)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [psutil](https://github.com/giampaolo/psutil) for system metrics collection
- [Plotly.js](https://plotly.com/javascript/) for interactive visualizations
- [Bootstrap](https://getbootstrap.com/) for responsive UI components

