{{ config(materialized='table') }}

select 
    employer_id,
    employer_name,
    industry

from {{ ref('stg_employers') }}
