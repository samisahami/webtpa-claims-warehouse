{{ config(materialized='view') }}

select
    member_id,
    employer_id,
    dob,
    gender,
    state

from {{ source('raw', 'members') }}