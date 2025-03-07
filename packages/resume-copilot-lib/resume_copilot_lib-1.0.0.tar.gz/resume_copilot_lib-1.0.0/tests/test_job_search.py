import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_copilot_lib import JobSearchHelper, JobSearchRequest


def test_job_search():
    request = JobSearchRequest(
        title="developer",
        size=2
    )
    
    try:
        result = JobSearchHelper.search_jobs(request)
        print("Job search results:")
        for job in result.jobs:
            print(f"Job: {job.name} at {job.company_name}")
            print(f"Location: {job.location.city}, {job.location.state}, {job.location.country}")
            print(f"ID: {job.id}")
            print(f"Created: {job.created}")
            print("---")
    except Exception as e:
        print(f"Error during job search: {str(e)}")


if __name__ == "__main__":
    test_job_search()