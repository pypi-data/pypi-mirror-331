# py-HiveFlow

A scalable, distributed producer/consumer framework for Python that simplifies building resilient task processing systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-support-blue)](https://www.docker.com/)
![PyPI](https://img.shields.io/pypi/v/hiveflow.svg)

## Overview

py-HiveFlow provides a flexible architecture for distributing and processing tasks across multiple workers. Built on modern Python and containerization practices, it enables developers to create highly available, fault-tolerant data processing pipelines with minimal boilerplate code.

## Key Features

- **Modular Architecture**: Easily extendable coordinator and worker components
- **Flexible Task Processing**: Define custom task types and processing logic
- **Real-time Monitoring**: Web dashboard for system health and performance metrics
- **Scalable Design**: Seamlessly add workers to increase processing capacity
- **Fault Tolerance**: Automatic task recovery and worker health monitoring
- **Containerized**: Docker and docker-compose support for simple deployment
- **Resource Management**: Smart resource allocation and rate limiting

## Quick Start

### Using Docker

All Docker-related configurations are maintained in the `./docker` directory:

```bash
# Clone the repository
git clone https://github.com/changyy/py-HiveFlow.git
cd py-HiveFlow

# Start the basic system using the docker-compose file in the docker directory
docker-compose -f docker/docker-compose.yml up -d

# For development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# For production environment
docker-compose -f docker/docker-compose.prod.yml up -d
```

Visit http://localhost:8080 to access the monitoring dashboard.

### Using Python Package

```bash
# Install the package
pip install py-hiveflow

# Initialize a new project
hiveflow init my-project
cd my-project

# Create a custom worker
hiveflow create worker my-custom-worker

# Start the system
hiveflow start
```

## Example Usage

### Defining Tasks

```python
from hiveflow import Task

class DataProcessingTask(Task):
    def __init__(self, data_source, parameters=None):
        self.data_source = data_source
        self.parameters = parameters or {}
        
    def process(self, worker):
        # Processing logic here
        result = worker.process_data(self.data_source, **self.parameters)
        return {"status": "completed", "result": result}
```

### Creating Custom Workers

```python
from hiveflow import Worker

class DataProcessor(Worker):
    def setup(self):
        # Initialize resources
        self.processor = self.load_processor()
        
    def can_process(self, task):
        return isinstance(task, DataProcessingTask)
        
    def process_task(self, task):
        # Process the task
        return task.process(self)
        
    def process_data(self, data_source, **kwargs):
        # Implementation of data processing
        return self.processor.process(data_source, **kwargs)
```

### Submitting Tasks

```python
from hiveflow import Coordinator

# Connect to the coordinator
coordinator = Coordinator("redis://localhost:6379")

# Submit tasks
task = DataProcessingTask("s3://my-bucket/data.csv", {"format": "csv"})
task_id = coordinator.submit_task(task)

# Check task status
status = coordinator.get_task_status(task_id)
print(f"Task status: {status}")

# Get task result when completed
result = coordinator.get_task_result(task_id)
```

## Architecture

py-HiveFlow consists of the following components:

- **Coordinator**: Manages task distribution and worker coordination
- **Workers**: Process assigned tasks based on capability
- **Storage**: Persists task data and system state (Redis & PostgreSQL)
- **Monitor**: Web interface for system visibility and management

## Use Cases

- Web crawling and data extraction
- Batch processing and ETL workflows
- Distributed data analysis
- Background job processing
- Service integration and webhooks processing
- Scheduled task execution

## Docker Container Structure

```
docker/
├── coordinator/                   # Coordinator service
│   ├── Dockerfile
│   └── requirements.txt
├── worker/                        # Generic worker
│   ├── Dockerfile
│   └── requirements.txt
├── monitor/                       # Web monitoring interface
│   ├── Dockerfile
│   └── requirements.txt
├── postgres/                      # PostgreSQL configuration
│   └── init.sql
├── redis/                         # Redis configuration
│   └── redis.conf
├── docker-compose.yml             # Main compose file
├── docker-compose.dev.yml         # Development setup
└── docker-compose.prod.yml        # Production setup
```

## Documentation

For full documentation, visit [docs/](docs/README.md) or the [official documentation](https://py-hiveflow.readthedocs.io/).

## Development

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional)
- Redis
- PostgreSQL

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/changyy/py-HiveFlow.git
cd py-HiveFlow

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Using Docker for Development

```bash
# Run the development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Run tests in Docker
docker-compose -f docker/docker-compose.test.yml up
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

py-HiveFlow was inspired by various distributed systems and task processing frameworks, aiming to provide a simpler yet powerful alternative for Python developers.
