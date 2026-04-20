"""Seed the database with HR policy PDFs."""

from pathlib import Path

from app.db.bootstrap import init_database
from app.db.engine import SessionLocal
from app.db.repositories import fetch_documents
from app.ingestion.pipeline import ingest_policy_pdf


SEED_POLICIES = [
    {
        "file_path": "data/leave_pto_policy.pdf",
        "title": "Leave & PTO Policy",
        "policy_type": "leave",
        "version": "v1",
    },
    {
        "file_path": "data/health_insurance_policy.pdf",
        "title": "Health Insurance Policy",
        "policy_type": "health_insurance",
        "version": "v1",
    },
    {
        "file_path": "data/remote_work_policy.pdf",
        "title": "Remote Work Policy",
        "policy_type": "remote_work",
        "version": "v1",
    },
]


def seed():
    # Ensure tables exist
    init_database()

    session = SessionLocal()
    try:
        existing = fetch_documents(session)
        existing_titles = {doc.title for doc in existing}

        for policy in SEED_POLICIES:
            if policy["title"] in existing_titles:
                print(f"Skipping '{policy['title']}' -- already exists")
                continue

            print(f"Ingesting '{policy['title']}'...")
            ingest_policy_pdf(
                session=session,
                file_path=policy["file_path"],
                title=policy["title"],
                policy_type=policy["policy_type"],
                version=policy["version"],
                uploaded_by="admin",
            )
            print(f"  Done.")

        print("Seed complete.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
