# src/agents/test_orchestrator_flow.py
"""
Example script to test the orchestrator flow with sample data
"""
from datetime import date
from .orchestrator import app
from ..models.user_model import User
from ..models.jd_model import JobDescription
from ..models.experience_model import Experience
from ..models.education_model import Education
from ..models.project_model import Project
from ..models.leadership_model import LeaderShip
from ..models.util_model import Emp_Type, Loc_Type, Salary

# Create sample User instance
sample_user = User(
    id="user-123",
    name="John Doe",
    email="john.doe@example.com",
    mobile="+1234567890",
    github_url="https://github.com/johndoe",
    linkedin_url="https://linkedin.com/in/johndoe",
    experience=Experience(
        role="Senior Software Engineer",
        company="Tech Corp",
        emp_type=Emp_Type.full_time,
        skills_used=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
        start_date=date(2021, 1, 15),
        end_date=date.today(),
        loc_type=Loc_Type.remote,
        location="San Francisco, CA",
        decription="Led development of microservices architecture using FastAPI and PostgreSQL"
    ),
    education=Education(
        institute_name="State University",
        degree="Bachelor of Science in Computer Science",
        grade=3.8,
        courses=["Data Structures", "Algorithms", "Database Systems", "Software Engineering"],
        start_date=date(2016, 9, 1),
        end_date=date(2020, 5, 15)
    ),
    skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS", "React", "TypeScript"],
    projects=Project(
        title="E-Commerce Platform",
        description="Built a scalable e-commerce platform with microservices architecture",
        skills_used=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        github_url="https://github.com/johndoe/ecommerce",
        deployed_url="https://ecommerce.example.com"
    ),
    leadership=LeaderShip(
        commitee_name="Tech Community",
        position="Lead Organizer",
        skills_used=["Event Management", "Public Speaking", "Community Building"],
        description="Organized monthly tech meetups with 200+ attendees",
        start_date=date(2022, 1, 1),
        end_date=date(2023, 12, 31)
    )
)

# Create sample JobDescription instance
sample_jd = JobDescription(
    job_title="Senior Backend Engineer",
    job_type=Emp_Type.full_time,
    loc_type=Loc_Type.remote,
    location="Remote, USA",
    salary=Salary(
        min_salary=120000.0,
        max_salary=180000.0
    ),
    min_experience=5.0,
    responsibilities=[
        "Design and develop scalable backend services using Python and FastAPI",
        "Implement and maintain database schemas and optimize queries",
        "Deploy and manage applications on cloud infrastructure (AWS)",
        "Collaborate with frontend team to design API contracts",
        "Mentor junior developers and conduct code reviews"
    ],
    required_qualification="Bachelor's degree in Computer Science or related field",
    required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
    preferred_skills=["Kubernetes", "Redis", "Microservices", "CI/CD"],
    description="We are looking for an experienced backend engineer to join our team..."
)

# Create proper GlobalState for invocation
initial_state = {
    "session_id": "test-session-001",
    "current_user": sample_user,
    "current_jd": sample_jd,
    "final_report": None,
    "user_summary": ""  # Will be filled by summarizer_node
}

# Run the orchestrator
print("=" * 60)
print("Running Orchestrator Flow Test")
print("=" * 60)
print(f"\nSession ID: {initial_state['session_id']}")
print(f"User: {sample_user.name}")
print(f"Job Title: {sample_jd.job_title}")
print("\nInvoking orchestrator...\n")

try:
    result = app.invoke(initial_state)
    
    print("=" * 60)
    print("Orchestrator Result:")
    print("=" * 60)
    print(f"\nSession ID: {result.get('session_id')}")
    print(f"\nUser Summary:")
    print("-" * 60)
    print(result.get('user_summary', 'No summary generated'))
    print("-" * 60)
    print(f"\nFinal Report: {result.get('final_report')}")
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ Error occurred: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    traceback.print_exc()