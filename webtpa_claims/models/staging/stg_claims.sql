{{ config(materialized='view') }}

select
    claim_id,
    member_id,
    provider_id,
    service_date,
    received_date,
    place_of_service,
    claim_status,
    primary_icd10

from {{ source('raw', 'claims') }}