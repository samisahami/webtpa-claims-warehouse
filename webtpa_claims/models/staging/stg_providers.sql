{{ config(materialized='view') }}

select
    provider_id,
    npi,
    specialty,
    state

from {{ source('raw', 'providers') }}