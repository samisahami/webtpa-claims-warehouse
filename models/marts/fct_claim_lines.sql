{{ config(materialized='table') }}

select
    cl.claim_line_id,
    cl.claim_id,
    c.member_id,
    c.provider_id,
    m.employer_id,

    cl.cpt_code,
    cl.units,
    cl.allowed_amount,
    cl.paid_amount,
    cl.member_responsibility,
    cl.paid_amount + cl.member_responsibility as total_claim_cost,

    c.service_date,
    c.claim_status

from {{ ref('stg_claim_lines') }} cl

left join {{ ref('stg_claims') }} c
    on cl.claim_id = c.claim_id

left join {{ ref('stg_members') }} m
    on c.member_id = m.member_id