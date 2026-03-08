from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

# -------- CONFIG (Large but manageable) --------
N_EMPLOYERS = 500
N_MEMBERS = 50_000
N_PROVIDERS = 25_000
N_CLAIMS = 250_000
AVG_LINES_PER_CLAIM = 3.6  # ~900k lines

OUT_DIR = Path(__file__).resolve().parents[1] / "seeds" / "raw"
OUT_DIR.mkdir(parents=True, exist_ok=True)

START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 12, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

# Some realistic-ish code pools (not perfectly compliant, but plausible)
ICD10_CODES = ["E11.9", "I10", "J06.9", "M54.5", "F41.1", "K21.9", "N39.0", "R07.9", "J45.909", "E78.5"]
CPT_CODES = ["99213", "99214", "93000", "80053", "85025", "71046", "36415", "45378", "81001", "99396"]
PLACE_OF_SERVICE = ["11", "21", "22", "23"]  # Office, Inpatient, Outpatient, ER-ish
CLAIM_STATUS = ["PAID", "DENIED", "PENDED", "REVERSED"]

STATES = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","IA","ID","IL","IN","KS","KY","LA","MA","MD",
    "ME","MI","MN","MO","MS","MT","NC","ND","NE","NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI","SC",
    "SD","TN","TX","UT","VA","VT","WA","WI","WV","WY"
]

def rand_date() -> date:
    return START_DATE + timedelta(days=random.randint(0, DATE_RANGE_DAYS))

def money(x: float) -> float:
    # round to cents
    return round(x + 1e-9, 2)

def write_csv(path: Path, header: list[str], rows_iter):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows_iter:
            w.writerow(r)

def main():
    # ---------- EMPLOYERS ----------
    employers = []
    for i in range(1, N_EMPLOYERS + 1):
        employer_id = f"EMP{i:05d}"
        name = f"{fake.company()}".replace(",", "")
        industry = random.choice(["Manufacturing", "Retail", "Healthcare", "Technology", "Logistics", "Finance"])
        state = random.choice(STATES)
        employers.append((employer_id, name, industry, state))

    write_csv(
        OUT_DIR / "employers.csv",
        ["employer_id", "employer_name", "industry", "state"],
        employers
    )

    # ---------- MEMBERS ----------
    # Assign members to employers (skewed distribution)
    employer_ids = [e[0] for e in employers]
    members = []
    for i in range(1, N_MEMBERS + 1):
        member_id = f"MBR{i:06d}"
        employer_id = random.choice(employer_ids)
        dob = fake.date_of_birth(minimum_age=0, maximum_age=85)
        gender = random.choice(["F", "M", "U"])
        state = random.choice(STATES)
        members.append((member_id, employer_id, dob.isoformat(), gender, state))

    write_csv(
        OUT_DIR / "members.csv",
        ["member_id", "employer_id", "dob", "gender", "state"],
        members
    )

    # ---------- PROVIDERS ----------
    providers = []
    for i in range(1, N_PROVIDERS + 1):
        provider_id = f"PRV{i:06d}"
        npi = f"{random.randint(1000000000, 1999999999)}"
        specialty = random.choice([
            "Family Medicine","Internal Medicine","Pediatrics","Orthopedics","Cardiology",
            "Emergency Medicine","Radiology","Dermatology","OBGYN","Psychiatry"
        ])
        state = random.choice(STATES)
        providers.append((provider_id, npi, specialty, state))

    write_csv(
        OUT_DIR / "providers.csv",
        ["provider_id", "npi", "specialty", "state"],
        providers
    )

    # Prepare lookup arrays for faster random choice
    member_ids = [m[0] for m in members]
    provider_ids = [p[0] for p in providers]

    # ---------- CLAIMS ----------
    claims = []
    claim_rows = []
    for i in range(1, N_CLAIMS + 1):
        claim_id = f"CLM{i:08d}"
        member_id = random.choice(member_ids)
        provider_id = random.choice(provider_ids)

        service_date = rand_date()
        received_date = service_date + timedelta(days=random.randint(0, 60))

        pos = random.choice(PLACE_OF_SERVICE)
        status = random.choices(CLAIM_STATUS, weights=[0.78, 0.14, 0.06, 0.02], k=1)[0]
        icd10 = random.choice(ICD10_CODES)

        # We'll compute amounts from lines later, but store status & dates here
        claim_rows.append((claim_id, member_id, provider_id, service_date.isoformat(), received_date.isoformat(), pos, status, icd10))

    write_csv(
        OUT_DIR / "claims.csv",
        ["claim_id", "member_id", "provider_id", "service_date", "received_date", "place_of_service", "claim_status", "primary_icd10"],
        claim_rows
    )

    # ---------- CLAIM LINES ----------
    # Generate approximately N_CLAIMS * AVG_LINES_PER_CLAIM lines
    total_lines = int(N_CLAIMS * AVG_LINES_PER_CLAIM)
    line_rows = []

    for line_num in range(1, total_lines + 1):
        # pick a claim; this creates multiple lines per claim naturally
        claim_idx = random.randint(1, N_CLAIMS)
        claim_id = f"CLM{claim_idx:08d}"
        line_id = f"{claim_id}-L{random.randint(1, 9):02d}"

        cpt = random.choice(CPT_CODES)
        units = random.choices([1, 2, 3, 4], weights=[0.78, 0.15, 0.05, 0.02], k=1)[0]

        # Allowed amount distribution
        base = random.lognormvariate(4.2, 0.6)  # right-skewed
        allowed = money(base * units)

        # Paid depends on denial/reversal; we'll approximate by making some lines $0 paid
        # We'll infer claim status later in marts; for now store line-level paid
        # Roughly 15% lines pay $0
        if random.random() < 0.15:
            paid = 0.00
        else:
            paid = money(allowed * random.uniform(0.65, 0.95))

        member_resp = money(max(allowed - paid, 0.0))
        line_rows.append((line_id, claim_id, cpt, units, allowed, paid, member_resp))

    write_csv(
        OUT_DIR / "claim_lines.csv",
        ["claim_line_id", "claim_id", "cpt_code", "units", "allowed_amount", "paid_amount", "member_responsibility"],
        line_rows
    )

    print(f"Wrote CSVs to: {OUT_DIR}")
    print(f"Employers: {N_EMPLOYERS}")
    print(f"Members:   {N_MEMBERS}")
    print(f"Providers: {N_PROVIDERS}")
    print(f"Claims:    {N_CLAIMS}")
    print(f"Lines:     {total_lines}")

if __name__ == "__main__":
    main()