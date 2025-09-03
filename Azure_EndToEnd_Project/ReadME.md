# End-to-End Data Engineering Pipeline on Azure Databricks

![Azure](https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apache-spark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-004B5E?style=for-the-badge&logo=linux-foundation&logoColor=white)

## Project Overview

This project demonstrates a complete, end-to-end data engineering pipeline built on the Azure cloud platform using Azure Databricks. It ingests raw transactional data, processes it through a multi-layered **Medallion Architecture** (Bronze, Silver, Gold), and models it into a **Star Schema** optimized for analytics.

The pipeline leverages modern data engineering practices, including incremental data loading with **Spark Structured Streaming** and **Autoloader**, implementation of **Slowly Changing Dimensions (SCD Type 1 & 2)**, and automated workflow orchestration using **Databricks Jobs**.

## Architecture Diagram

The entire pipeline is orchestrated within Azure Databricks, reading from and writing to Azure Data Lake Storage (ADLS) Gen2. The flow follows the Bronze-Silver-Gold layer paradigm to progressively refine and structure the data.

```mermaid
graph TD
    subgraph "Inputs"
        Param["Parameters"]
    end

    subgraph "Bronze Layer"
        Bronze["Bronze_Autoloader_iteration"]
    end

    subgraph "Silver Layer"
        Silver_P["Silver_Products"]
        Silver_C["Silver_Customers"]
        Silver_O["Silver_Orders"]
    end

    subgraph "Gold Layer"
        Gold_C["Gold_Customers"]
        Gold_P["Gold_Products"]
        Fact_O["Fact_Orders"]
    end

    subgraph "Downstream Consumption"
        J[("BI Tools / Analytics / ML")]
    end

    %% --- Define the correct connections ---
    Param --> Bronze
    Bronze --> Silver_P
    Bronze --> Silver_C
    Bronze --> Silver_O

    Silver_P --> Gold_C
    Silver_C --> Gold_C
    Silver_O --> Gold_C

    Silver_P --> Gold_P
    Silver_C --> Gold_P
    Silver_O --> Gold_P

    Gold_C --> Fact_O
    Gold_P --> Fact_O

    Fact_O --> J
    Gold_C --> J
    Gold_P --> J

    %% --- Apply the styling with black text ---
    style Param fill:#d4a373,color:black
    style Bronze fill:#c77dff,color:black
    style Silver_P fill:#90e0ef,color:black
    style Silver_C fill:#90e0ef,color:black
    style Silver_O fill:#90e0ef,color:black
    style Gold_C fill:#ffd6a5,color:black
    style Gold_P fill:#ffd6a5,color:black
    style Fact_O fill:#ffadad,color:black
    style J fill:#a8dadc,color:black
