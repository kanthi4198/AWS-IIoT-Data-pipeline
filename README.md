# Smart Factory IoT Analytics on AWS

This is an end-to-end IoT data pipeline project that simulates a smart factory production line using AWS services. It ingests real-time sensor data, stores it in S3, processes and transforms it with Lambda and Athena, and visualizes it using Amazon QuickSight — all within (or near) AWS Free Tier limits.

---

## 📌 Project Overview

The goal is to demonstrate a scalable, event-driven data pipeline on AWS using simulated IoT sensor data from a production environment. The project includes:

- Real-time data ingestion via MQTT using AWS IoT Core
- Data processing and routing via AWS Lambda
- Storage in Amazon S3 (raw and processed zones)
- Data cataloging with AWS Glue
- Querying using Amazon Athena
- Dashboards built in Amazon QuickSight

---

## 🧱 Architecture

```plaintext
+-------------------+      MQTT       +-------------+        Lambda         +-----------+
| Python Simulator  +----------------> AWS IoT Core +-----------------------> S3 (Raw)  |
+-------------------+                 +-------------+                        +-----------+
                                                                                   |
                                                                                   v
                                                                               AWS Glue
                                                                                   |
                                                                                   v
                                                                              S3 (Processed)
                                                                                   |
                                                                                   v
                                                                              Amazon Athena
                                                                                   |
                                                                                   v
                                                                              QuickSight


