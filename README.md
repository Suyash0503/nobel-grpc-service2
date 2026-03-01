Nobel gRPC Service (Azure-Ready Python Microservice)

A production-style Python gRPC microservice designed for high-performance service-to-service communication and cloud deployment on Microsoft Azure.

This project demonstrates distributed system practices including Protocol Buffers, Docker containerization, API gateway abstraction, and optional Redis caching.

Project Overview

This repository implements:

Python gRPC server

Protocol Buffers service definition

gRPC client for testing

Gateway layer abstraction

Docker containerization

Azure deployment readiness

Optional Redis integration

It simulates a scalable microservice suitable for cloud-native environments.

Architecture

Client → Gateway → gRPC Service
↓
Redis (optional)

Component Breakdown
File	Description
proto/	gRPC service definitions (.proto files)
noble_pb2.py	Auto-generated protobuf message classes
noble_pb2_grpc.py	Auto-generated gRPC service stubs
gateway.py	Main gRPC server implementation
client.py	Test client for sending RPC requests
test_redis.py	Redis connectivity test
Dockerfile	Container configuration
requirements.txt	Python dependencies
.env	Environment variables
scripts/	Utility or helper scripts
Technologies Used

Python 3.x

gRPC

Protocol Buffers

Docker

Redis

Microsoft Azure (Container Apps, App Service, AKS ready)

How It Works

The service contract is defined inside the proto directory.

The Protobuf compiler generates Python classes.

gateway.py implements the service logic.

client.py communicates with the service via gRPC.

Redis (optional) can cache service responses.

The application can be containerized and deployed to Azure.

Running Locally

Install dependencies:

pip install -r requirements.txt

Start the gRPC server:

python gateway.py

Run the client:

python client.py

Running with Docker

Build Docker image:

docker build -t nobel-grpc-service .

Run container:

docker run -p 50051:50051 nobel-grpc-service

Azure Deployment (Container-Based)

This service is ready for deployment using:

Azure Container Apps

Azure App Service (Docker-based)

Azure Kubernetes Service (AKS)

Basic deployment flow:

Build Docker image

Push image to Azure Container Registry (ACR)

Deploy container to Azure service

Expose port 50051

Environment Variables

Example .env file:

GRPC_PORT=50051
REDIS_HOST=localhost
REDIS_PORT=6379

Learning Outcomes

This project demonstrates:

Remote Procedure Call architecture

Microservice communication patterns

Containerization best practices

Cloud deployment design

Gateway abstraction

Caching integration

Project Structure

nobel-grpc-service2/
│
├── proto/
├── scripts/
├── noble_pb2.py
├── noble_pb2_grpc.py
├── gateway.py
├── client.py
├── test_redis.py
├── Dockerfile
├── requirements.txt
└── .env

Future Improvements

Add authentication (JWT or OAuth)

Add logging and monitoring

Add CI/CD pipeline (GitHub Actions)

Implement streaming RPC

Add health checks

Add service discovery
