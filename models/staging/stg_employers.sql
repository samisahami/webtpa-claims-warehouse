{{ config(materialized='view') }}

select
    employer_id,
    employer_name,
    industry

from {{ source('raw', 'employers') }}