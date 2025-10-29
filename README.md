# Smart Factory IoT Analytics on AWS

This project simulates an End-to-end IIoT data pipeline demo for smart devices, built entirely using AWS free-tier services.
---

## Features

1. IoT Data simulation
2. Serverless ingestion (AWS Lambda)
3. DynamoDB buffering
4. Hourly batch process to S3
5. Scalable, reproducible infrastructure-as-code (AWS CDK)

## Overview

- **Data Ingestion**: Simulated sensor data sent via MQTT using the **AWS IoT Device SDK for Python**
- **Processing**: Real-time triggers with **AWS Lambda**
- **Storage**: Raw and processed data stored in **Amazon S3**
- **Cataloging**: Managed by **AWS Glue**
- **Querying(Future Scope)**: Performed with **Amazon Athena**
- **Visualization(Future Scope)**: Dashboards built in **Amazon QuickSight**
---

##Pre-requiisites
Prerequisites
AWS Account
An active AWS account with Free Tier eligibility (recommended for hands-on deployment with no cost).

AWS CLI
Installed and configured. Install Guide

AWS CDK v2
Installed globally (for infrastructure deployment).

Git
For cloning and version control.

Basic AWS Permissions
User/role must have enough rights to create/manage S3, DynamoDB, IAM, Lambda, IoT Core, and CloudWatch within your AWS account.

Note:
All core services are fully covered by AWS Free Tier, enabling you to deploy and test without extra cost if limits are not exceeded.


## Architecture

<img width="1848" height="835" alt="image" src="https://github.com/user-attachments/assets/0253334f-8b22-459c-954f-e9c026938def" />

Boxes indicated in Blue represent free tier services and yellow boxes indicate paid services presented here for future scope


## Repository Structure

Repository Structure
This project is organized as follows:

cdk/ — AWS CDK (Infrastructure-as-Code)

Contains the stack scripts for creating AWS resources: S3, DynamoDB, IAM, Lambda, IoT Core, EventBridge.

lambda/ — Lambda Function Code

Python scripts for IoT message ingestion, transformation, and batch processing to S3.

simulator/ — IoT Data Simulator

Python script for simulating factory sensor messages and publishing via MQTT to AWS IoT Core.

venv/ — Python Virtual Environment (already initialized for dependencies)

README.md, LICENSE, .gitignore — Metadata and documentation files

