# Smart Factory IoT Analytics on AWS (Free Tier Edition)

This project simulates a smart factory production line using AWS services — optimized to stay within AWS Free Tier limits. It features real-time IoT data ingestion, serverless processing, cloud storage, and analytics dashboards.

---

## Overview

- **Data Ingestion**: Simulated sensor data sent via MQTT using the **AWS IoT Device SDK for Python**
- **Processing**: Real-time triggers with **AWS Lambda**
- **Storage**: Raw and processed data stored in **Amazon S3**
- **Cataloging**: Managed by **AWS Glue**
- **Querying**: Performed with **Amazon Athena**
- **Visualization**: Dashboards built in **Amazon QuickSight**
---

## Architecture

```plaintext
------------------------+       MQTT        +------------------+       Trigger        +------------------+
|  Python IoT Simulator  +------------------->  AWS IoT Core     +--------------------->   AWS Lambda      |
+------------------------+                    +------------------+                      +------------------+
                                                                                                 |
                                                                                                 v
                                                                                          +--------------+
                                                                                          |  S3 (Raw Zone)|
                                                                                          +--------------+
                                                                                                 |
                                                                                                 v
                                                                                           AWS Glue Crawler
                                                                                                 |
                                                                                                 v
                                                                                         +----------------+
                                                                                         | S3 (Processed) |
                                                                                         +----------------+
                                                                                                 |
                                                                                                 v
                                                                                          Amazon Athena
                                                                                                 |
                                                                                                 v
                                                                                          QuickSight Dashboard

