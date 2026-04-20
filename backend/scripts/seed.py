"""
Seed script for demo data.
Run via: make seed (or python -m scripts.seed)
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.core.security import hash_password
from src.models.user import User
from src.models.document import Document
from src.models.analysis import Analysis, Clause
from src.models.job import Job


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionFactory() as db:
        # Check if demo user already exists
        result = await db.execute(select(User).where(User.email == "demo@example.com"))
        if result.scalar_one_or_none():
            print("Demo user already exists. Skipping seed.")
            await engine.dispose()
            return

        # Create demo user
        user = User(
            email="demo@example.com",
            password_hash=hash_password("Demo1234"),
        )
        db.add(user)
        await db.flush()
        print(f"Created demo user: demo@example.com")

        # Create sample documents with synthetic analysis data
        documents_data = [
            {
                "title": "Master Services Agreement - Acme Corp",
                "original_filename": "MSA_Acme_2024.pdf",
                "doc_type": "contract",
                "status": "completed",
                "page_count": 14,
                "word_count": 4821,
                "parties": ["Acme Corp", "Globex Ltd"],
                "risk_score": 72,
                "clauses": [
                    (
                        "liability_limitation",
                        "In no event shall either party's aggregate liability exceed the total fees paid in the 12 months preceding the claim.",
                        "Section 8.1",
                        "Liability is capped at 12 months of fees.",
                        "high",
                        "Cap at 12 months is below market standard of 24 months.",
                    ),
                    (
                        "indemnification",
                        "Client shall indemnify and hold harmless Provider against all claims arising from Client's use of the services.",
                        "Section 9.1",
                        "The client must cover all legal costs if their use of the service causes problems.",
                        "high",
                        "One-sided indemnification favoring the provider.",
                    ),
                    (
                        "termination",
                        "Either party may terminate with 30 days written notice.",
                        "Section 12.1",
                        "Either side can end the contract with 30 days notice.",
                        "low",
                        "Standard termination clause.",
                    ),
                    (
                        "governing_law",
                        "This agreement shall be governed by the laws of the State of Delaware.",
                        "Section 15.1",
                        "Delaware law applies to this contract.",
                        "info",
                        "Standard governing law clause.",
                    ),
                    (
                        "confidentiality",
                        "Both parties agree to maintain confidentiality of proprietary information for 3 years.",
                        "Section 7.1",
                        "Both sides must keep each other's secrets for 3 years.",
                        "medium",
                        "3-year term is shorter than typical 5-year NDA.",
                    ),
                    (
                        "payment_terms",
                        "Payment is due within 30 days of invoice. Late payments accrue interest at 1.5% per month.",
                        "Section 5.1",
                        "Bills must be paid within 30 days or interest charges apply.",
                        "medium",
                        "1.5% monthly interest is above market rate.",
                    ),
                ],
                "anomalies": [
                    {
                        "anomaly_type": "missing_clause",
                        "description": "No force majeure clause found.",
                        "severity": "warning",
                    },
                    {
                        "anomaly_type": "unusual_provision",
                        "description": "Indemnification is one-sided, favoring the provider.",
                        "severity": "critical",
                    },
                ],
                "summary_brief": "A Master Services Agreement between Acme Corp and Globex Ltd with above-average risk due to one-sided indemnification and below-market liability caps.",
                "summary_standard": "This MSA governs the provision of technology services from Globex Ltd to Acme Corp. Key terms include a 12-month liability cap, one-sided indemnification favoring the provider, 30-day termination notice, and Delaware governing law. Payment terms require settlement within 30 days with 1.5% monthly interest on late payments. The confidentiality period is 3 years. Notable concerns include the absence of a force majeure clause and the one-sided nature of the indemnification provision.",
            },
            {
                "title": "Non-Disclosure Agreement - Project Phoenix",
                "original_filename": "NDA_Phoenix_2024.pdf",
                "doc_type": "nda",
                "status": "completed",
                "page_count": 3,
                "word_count": 1250,
                "parties": ["TechStart Inc", "InnoVentures LLC"],
                "risk_score": 28,
                "clauses": [
                    (
                        "confidentiality",
                        "Both parties agree to maintain strict confidentiality of all shared information for a period of 5 years.",
                        "Section 2",
                        "Both sides must keep shared information secret for 5 years.",
                        "low",
                        "Standard mutual NDA confidentiality clause.",
                    ),
                    (
                        "termination",
                        "This agreement may be terminated by either party with 60 days written notice.",
                        "Section 6",
                        "Either party can end the NDA with 60 days notice.",
                        "info",
                        "Standard termination provision.",
                    ),
                    (
                        "governing_law",
                        "This agreement is governed by the laws of California.",
                        "Section 8",
                        "California law applies.",
                        "info",
                        "Standard governing law.",
                    ),
                    (
                        "dispute_resolution",
                        "Disputes shall be resolved through mediation, then binding arbitration.",
                        "Section 9",
                        "Disagreements go to mediation first, then arbitration.",
                        "low",
                        "Standard two-step dispute resolution.",
                    ),
                ],
                "anomalies": [],
                "summary_brief": "A standard mutual NDA between TechStart Inc and InnoVentures LLC with low risk and all expected clauses present.",
                "summary_standard": "This mutual Non-Disclosure Agreement establishes confidentiality obligations between TechStart Inc and InnoVentures LLC for Project Phoenix. The agreement includes a 5-year confidentiality period, 60-day termination notice, California governing law, and a two-step dispute resolution process (mediation then arbitration). All standard NDA clauses are present and the terms are balanced between both parties.",
            },
            {
                "title": "Employment Agreement - Senior Engineer",
                "original_filename": "Employment_Offer_2024.txt",
                "doc_type": "employment",
                "status": "completed",
                "page_count": 1,
                "word_count": 430,
                "parties": ["TechCorp Inc", "John Smith"],
                "risk_score": 55,
                "clauses": [
                    (
                        "non_compete",
                        "For 12 months following termination, employee shall not engage in competing business within the United States.",
                        "Section 6",
                        "Employee can't work for competitors for 12 months after leaving.",
                        "high",
                        "12-month nationwide non-compete is aggressive.",
                    ),
                    (
                        "intellectual_property",
                        "All inventions created during employment are company property.",
                        "Section 7",
                        "Anything you create at work belongs to the company.",
                        "medium",
                        "Standard IP assignment but lacks carve-out for personal projects.",
                    ),
                    (
                        "termination",
                        "Either party may terminate with 30 days notice. Severance of 3 months for termination without cause.",
                        "Section 8",
                        "30 days notice required. 3 months severance if fired without cause.",
                        "low",
                        "Reasonable termination terms.",
                    ),
                    (
                        "confidentiality",
                        "Employee must maintain confidentiality during and after employment.",
                        "Section 5",
                        "Must keep company secrets forever.",
                        "low",
                        "Standard employment confidentiality.",
                    ),
                    (
                        "governing_law",
                        "Governed by the laws of California.",
                        "Section 9",
                        "California law applies.",
                        "info",
                        "Standard governing law.",
                    ),
                ],
                "anomalies": [
                    {
                        "anomaly_type": "unusual_provision",
                        "description": "Non-compete clause covers the entire United States, which is unusually broad for a tech employment agreement.",
                        "severity": "warning",
                    },
                ],
                "summary_brief": "An employment offer for a Senior Engineer at TechCorp Inc with moderate risk due to an aggressive nationwide non-compete clause.",
                "summary_standard": "This employment agreement offers John Smith a Senior Software Engineer position at TechCorp Inc with a $185,000 salary and standard benefits. Key concerns include a 12-month nationwide non-compete clause, which is unusually broad. The IP assignment clause lacks a personal projects carve-out. Termination terms are reasonable with 30-day notice and 3-month severance. Confidentiality obligations survive termination indefinitely.",
            },
        ]

        for doc_data in documents_data:
            doc = Document(
                user_id=user.id,
                title=doc_data["title"],
                original_filename=doc_data["original_filename"],
                file_path=f"/data/uploads/{user.id}/placeholder",
                doc_type=doc_data["doc_type"],
                status=doc_data["status"],
                page_count=doc_data["page_count"],
                word_count=doc_data["word_count"],
                parties=doc_data["parties"],
                mime_type="application/pdf"
                if doc_data["original_filename"].endswith(".pdf")
                else "text/plain",
            )
            db.add(doc)
            await db.flush()

            # Create job
            job = Job(
                document_id=doc.id,
                job_type="process_document",
                status="completed",
                completed_at=datetime.now(timezone.utc),
            )
            db.add(job)

            # Create analysis
            analysis = Analysis(
                document_id=doc.id,
                risk_score=doc_data["risk_score"],
                summary_brief=doc_data["summary_brief"],
                summary_standard=doc_data["summary_standard"],
                summary_detailed=doc_data.get("summary_standard", ""),
                anomalies=doc_data["anomalies"],
            )
            db.add(analysis)
            await db.flush()

            # Create clauses
            for clause_data in doc_data["clauses"]:
                clause = Clause(
                    analysis_id=analysis.id,
                    clause_type=clause_data[0],
                    verbatim_text=clause_data[1],
                    section_reference=clause_data[2],
                    plain_english=clause_data[3],
                    risk_level=clause_data[4],
                    risk_reason=clause_data[5],
                )
                db.add(clause)

            print(f"  Created document: {doc_data['title']} (risk: {doc_data['risk_score']})")

        await db.commit()
        print("\nSeed complete!")
        print("\nLogin credentials:")
        print("  Email: demo@example.com")
        print("  Password: Demo1234")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
