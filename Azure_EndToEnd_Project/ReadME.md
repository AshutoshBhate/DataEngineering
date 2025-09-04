# End-to-End Data Engineering Pipeline on Azure Databricks

![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-004B5E?style=for-the-badge&logo=linux-foundation&logoColor=white)

## Project Overview

This project demonstrates a complete, end-to-end data engineering pipeline built on the Azure cloud platform using Azure Databricks. It ingests raw transactional data, processes it through a multi-layered **Medallion Architecture** (Bronze, Silver, Gold), and models it into a **Star Schema** optimized for analytics.

The pipeline leverages modern data engineering practices, including incremental data loading with **Spark Structured Streaming** and **Autoloader**, implementation of **Slowly Changing Dimensions (SCD Type 1 & 2)**, and automated workflow orchestration using **Databricks Jobs**.

---

## Technology Stack

* **Cloud Platform**: Microsoft Azure
* **Data Lake**: Azure Data Lake Storage (ADLS) Gen2
* **Processing Engine**: Azure Databricks, Apache Spark (PySpark)
* **Data Format**: Delta Lake
* **Ingestion**: Databricks Autoloader, Spark Structured Streaming
* **Orchestration**: Databricks Jobs, Delta Live Tables
* **Governance**: Unity Catalog

---

## Architecture Diagram

The entire pipeline is orchestrated within Azure Databricks, reading from and writing to ADLS Gen2. The flow follows the Bronze-Silver-Gold paradigm to progressively refine the data into a Star Schema.

```mermaid
graph LR
    %% 1. Define all nodes first
    RawFiles["Raw Parquet Files"]
    AutoLoader["Autoloader (Incremental Ingestion)"]
    SilverCustomers["Silver_Customers"]
    SilverProducts["Silver_Products"]
    SilverOrders["Silver_Orders"]
    DimCustomers["Dim_Customers (SCD Type 2)"]
    DimProducts["Dim_Products (SCD Type 1)"]
    FactOrders["Fact_Orders"]
    BI["BI Tools / Analytics"]

    %% 2. Group nodes into subgraphs
    subgraph "Data Source (ADLS Gen2)"
        RawFiles
    end

    subgraph "Bronze Layer (Raw Ingestion)"
        AutoLoader
    end

    subgraph "Silver Layer"
        SilverCustomers
        SilverProducts
        SilverOrders
    end

    subgraph "Gold Layer (Business Aggregates)"
        DimCustomers
        DimProducts
        FactOrders
    end
    
    subgraph "Consumption"
        BI
    end

    %% 3. Define the data flow (connections)
    RawFiles --> AutoLoader;
    AutoLoader --> SilverCustomers;
    AutoLoader --> SilverProducts;
    AutoLoader --> SilverOrders;
    
    SilverCustomers --> DimCustomers;
    SilverProducts --> DimProducts;
    
    SilverOrders --> FactOrders;
    DimCustomers --> FactOrders;
    DimProducts --> FactOrders;
    
    FactOrders --> BI;
    DimCustomers --> BI;
    DimProducts --> BI;

    %% 4. Apply styling at the end
    style RawFiles fill:#E3F2FD,stroke:#333,stroke-width:2px,color:black
    style AutoLoader fill:#FFF3E0,stroke:#333,stroke-width:2px,color:black
    style SilverCustomers fill:#E8EAF6,stroke:#333,stroke-width:2px,color:black
    style SilverProducts fill:#E8EAF6,stroke:#333,stroke-width:2px,color:black
    style SilverOrders fill:#E8EAF6,stroke:#333,stroke-width:2px,color:black
    style DimCustomers fill:#FFF9C4,stroke:#333,stroke-width:2px,color:black
    style DimProducts fill:#FFF9C4,stroke:#333,stroke-width:2px,color:black
    style FactOrders fill:#FFCDD2,stroke:#333,stroke-width:2px,color:black
    style BI fill:#E8F5E9,stroke:#333,stroke-width:2px,color:black
```
---

## Key Features

* **Medallion Architecture**: Segregates data into Bronze (raw), Silver (cleaned), and Gold (aggregated) layers.
* **Incremental Ingestion**: Uses Autoloader to efficiently process only new data, avoiding full re-scans.
* **Slowly Changing Dimensions**: Implements SCD Type 1 (overwrite) and Type 2 (historical tracking) for dimension tables.
* **Star Schema Modeling**: Creates optimized dimension and fact tables in the Gold layer for fast analytical queries.
* **Automated Orchestration**: Utilizes Databricks Jobs to define dependencies and automate the end-to-end workflow.
* **Schema Enforcement & Evolution**: Leverages Delta Lake's capabilities to ensure data quality and handle schema changes over time.

---

## Pipeline in Action

Here are some snapshots of the key components of the project running in Databricks.

**1. End-to-End Job Orchestration**
*This image shows the directed acyclic graph (DAG) of the entire pipeline, with tasks for each layer and their dependencies.*
![Databricks Job Workflow](./assets/databricks_job_dag.png)

**2. Delta Live Tables (DLT) Pipeline**
*This is an example of a DLT pipeline graph used for developing the Gold layer tables.*
![DLT Pipeline](./assets/dlt_pipeline_graph.png)

**3. Final Star Schema in Catalog Explorer**
*The final dimension and fact tables are registered in Unity Catalog and ready for consumption.*
![Final Gold Tables](./assets/catalog_explorer_gold_tables.png)
