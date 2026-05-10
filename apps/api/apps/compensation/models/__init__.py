"""Compensation models — Ley 30709 CCF + Category + SalaryBand + factor scoring."""

from .job_factor import JobFactor, JobSubfactor

__all__ = [
    "JobFactor",
    "JobSubfactor",
]
