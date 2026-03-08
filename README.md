<<<<<<< HEAD
# WebTPA Claims Warehouse (Snowflake + dbt + CI)

End-to-end healthcare claims reporting warehouse:
- Snowflake SQL transformations via dbt
- Data quality tests
- CI with GitHub Actions
- Reporting-ready marts (employer + member + claims)
=======
# Healthcare Claims Analytics Engineering Pipeline

End-to-end analytics engineering project modeling healthcare claims data using **dbt + Snowflake**.

This project simulates a real healthcare analytics environment where raw claims data is transformed into a clean analytics layer for reporting and downstream BI tools.

---

## Architecture

The pipeline follows a modern analytics engineering architecture:

Raw Data → Staging Layer → Dimension Tables → Fact Tables


Python Data Generator
        ↓
dbt Seeds (raw tables)
        ↓
Snowflake
        ↓
dbt Sources
        ↓
Staging Models
        ↓
Dimensional Models
        ↓
Fact Tables

## Tech Stack

• Snowflake — cloud data warehouse  
• dbt (Data Build Tool) — data transformations and modeling  
• SQL — transformation logic  
• Python — synthetic healthcare data generation  
• Git / GitHub — version control  
• dbt tests — data quality validation


## Data Model

The project models healthcare claims data using a dimensional analytics model.

### Staging Layer
Raw operational tables are cleaned and standardized.

- stg_claims
- stg_claim_lines
- stg_members
- stg_providers
- stg_employers

### Dimension Tables

- dim_employers

### Fact Tables

- fct_claim_lines

Grain: one row per **claim line**.

## Example Analytics Query


Example query to calculate employer healthcare spend:

```sql
SELECT
    employer_id,
    SUM(total_claim_cost) AS total_spend
FROM fct_claim_lines
GROUP BY employer_id
ORDER BY total_spend DESC;
```

This query demonstrates how the fact table can be used for employer healthcare spend analysis.

---

## Data Lineage

The project uses dbt documentation to visualize model dependencies and lineage.

![Data Lineage](https://raw.githubusercontent.com/samisahami/webtpa-claims-warehouse/main/docs/lineage_graph.png)
>>>>>>> 4714ce12ce901502aa9488e23ab1e78760fbfa89
