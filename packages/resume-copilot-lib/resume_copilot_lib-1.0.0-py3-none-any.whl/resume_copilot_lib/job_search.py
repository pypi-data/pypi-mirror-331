import requests
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class JobSearchRequest:
    title: str
    size: int
    company_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    is_remote: Optional[bool] = None

    def to_dict(self):
        result = {
            "title": self.title,
            "size": self.size
        }
        
        if self.company_name:
            result["companyName"] = self.company_name
        if self.city:
            result["city"] = self.city
        if self.state:
            result["state"] = self.state
        if self.country:
            result["country"] = self.country
        if self.is_remote is not None:
            result["isRemote"] = self.is_remote
            
        return result


@dataclass
class GeographicLocation:
    lat: float
    lon: float


@dataclass
class JobLocation:
    city: str
    country: str
    state: str
    loc: GeographicLocation
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            city=data.get("city", ""),
            country=data.get("country", ""),
            state=data.get("state", ""),
            loc=GeographicLocation(
                lat=data.get("loc", {}).get("lat", 0.0),
                lon=data.get("loc", {}).get("lon", 0.0)
            )
        )


@dataclass
class Job:
    name: str
    company_name: str
    location: JobLocation
    feed: str
    id: str
    created: str
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            company_name=data.get("companyName", ""),
            location=JobLocation.from_dict(data.get("location", {})),
            feed=data.get("feed", ""),
            id=data.get("id", ""),
            created=data.get("created", "")
        )


@dataclass
class JobSearchResult:
    jobs: List[Job]
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            jobs=[Job.from_dict(job) for job in data.get("jobs", [])]
        )


class JobSearchHelper:
    BASE_URL = "https://api.resumecopilot.net"
    
    @classmethod
    def search_jobs(cls, request: JobSearchRequest) -> JobSearchResult:
        """
        Search for jobs based on the provided request parameters.
        
        Args:
            request: A JobSearchRequest object with search parameters
            
        Returns:
            JobSearchResult object containing the search results
            
        Raises:
            Exception: If there's an error connecting to the job search service
        """
        try:
            response = requests.post(f"{cls.BASE_URL}/api/v1/search", json=request.to_dict())
            response.raise_for_status()
            return JobSearchResult.from_dict(response.json())
        except Exception as e:
            print(f"Error searching jobs: {str(e)}")
            raise Exception("There was an error connecting to the job search service.")