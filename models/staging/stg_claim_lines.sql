{{ config(materialized='view') }}

select
    claim_line_id,
    claim_id,
    cpt_code,
    units,
    allowed_amount,
    paid_amount,
    member_responsibility

from {{ source('raw', 'claim_lines') }}