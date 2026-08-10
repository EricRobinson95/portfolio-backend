from app.models.project_technology import ProjectTechnology


PROJECT_TECHNOLOGIES: list[ProjectTechnology] = [

    # =====================================================
    # Project 1 - Enterprise Network Infrastructure
    # =====================================================

    ProjectTechnology(project_id=1, technology_id=2),   # Git
    ProjectTechnology(project_id=1, technology_id=7),   # Cisco IOS
    ProjectTechnology(project_id=1, technology_id=8),   # Cisco Packet Tracer
    ProjectTechnology(project_id=1, technology_id=9),   # draw.io

    # =====================================================
    # Project 2 - Enterprise Hybrid Cloud Platform
    # =====================================================

    ProjectTechnology(project_id=2, technology_id=2),   # Git
    ProjectTechnology(project_id=2, technology_id=3),   # PowerShell
    ProjectTechnology(project_id=2, technology_id=4),   # VMware Workstation
    ProjectTechnology(project_id=2, technology_id=5),   # Windows Server 2025
    ProjectTechnology(project_id=2, technology_id=6),   # Active Directory
    ProjectTechnology(project_id=2, technology_id=9),   # draw.io
    ProjectTechnology(project_id=2, technology_id=10),  # SSH
    ProjectTechnology(project_id=2, technology_id=12),  # WireGuard
    ProjectTechnology(project_id=2, technology_id=25),  # Cloudflare
    ProjectTechnology(project_id=2, technology_id=26),  # AWS
    ProjectTechnology(project_id=2, technology_id=27),  # Microsoft Azure

    # =====================================================
    # Project 3 - Enterprise Infrastructure Automation
    # =====================================================

    ProjectTechnology(project_id=3, technology_id=1),   # Python
    ProjectTechnology(project_id=3, technology_id=2),   # Git
    ProjectTechnology(project_id=3, technology_id=3),   # PowerShell
    ProjectTechnology(project_id=3, technology_id=9),   # draw.io
    ProjectTechnology(project_id=3, technology_id=10),  # SSH
    ProjectTechnology(project_id=3, technology_id=11),  # Netmiko
    ProjectTechnology(project_id=3, technology_id=12),  # WireGuard
    ProjectTechnology(project_id=3, technology_id=25),  # Cloudflare

    # =====================================================
    # Project 4 - Portfolio Platform Backend
    # =====================================================

    ProjectTechnology(project_id=4, technology_id=1),   # Python
    ProjectTechnology(project_id=4, technology_id=2),   # Git
    ProjectTechnology(project_id=4, technology_id=13),  # FastAPI
    ProjectTechnology(project_id=4, technology_id=14),  # Pydantic
    ProjectTechnology(project_id=4, technology_id=15),  # SQLAlchemy
    ProjectTechnology(project_id=4, technology_id=16),  # PostgreSQL
    ProjectTechnology(project_id=4, technology_id=17),  # Uvicorn
    ProjectTechnology(project_id=4, technology_id=18),  # Alembic

    # =====================================================
    # Project 5 - Portfolio Platform Frontend
    # =====================================================

    ProjectTechnology(project_id=5, technology_id=2),   # Git
    ProjectTechnology(project_id=5, technology_id=19),  # React
    ProjectTechnology(project_id=5, technology_id=20),  # TypeScript
    ProjectTechnology(project_id=5, technology_id=21),  # Vite
    ProjectTechnology(project_id=5, technology_id=22),  # Tailwind CSS
    ProjectTechnology(project_id=5, technology_id=23),  # Axios
    ProjectTechnology(project_id=5, technology_id=24),  # TanStack Query

]