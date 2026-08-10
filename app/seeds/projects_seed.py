from app.schemas.project import ProjectCreate

PROJECTS: list[ProjectCreate] = [

    ProjectCreate(
        title="Enterprise Network Infrastructure",
        github_url="https://github.com/EricRobinson95/Cisco-networking-lab",
        image_thumbnail_url="/static/images/projects/enterprise-network-infrastructure/thumbnail.png",
        description=(
            "Designed and deployed a simulated enterprise network using Cisco Packet Tracer. "
            "Configured VLANs, inter-VLAN routing, DHCP, ACLs, static routing, switch security, "
            "and network segmentation while documenting the architecture and validating "
            "connectivity across the environment."
        )
    ),

    ProjectCreate(
        title="Enterprise Hybrid Cloud Platform",
        github_url="https://github.com/EricRobinson95/enterprise-hybrid-cloud-platform",
        image_thumbnail_url="/static/images/projects/enterprise-hybrid-cloud-platform/thumbnail.png",
        description=(
            "Designed and implemented a hybrid cloud environment connecting AWS, Microsoft Azure, "
            "and an on-premises VMware environment using WireGuard VPN tunnels. Configured cloud "
            "networking, routing, Windows Server infrastructure, and cross-environment connectivity "
            "while validating communication between the hybrid environments."
        )
    ),

    ProjectCreate(
        title="Enterprise Infrastructure Automation",
        github_url="https://github.com/EricRobinson95/enterprise-hybrid-cloud-Infrastructure-automation",
        image_thumbnail_url="/static/images/projects/enterprise-infrastructure-automation/thumbnail.png",
        description=(
            "Developed a Python-based infrastructure automation platform for managing hybrid "
            "enterprise resources across AWS, Microsoft Azure, and VMware Workstation. Built a "
            "CLI for starting and stopping VPN, domain controller, and security resources with "
            "health checks, resource validation, structured logging, and automated state management."
            )
    ),
    ProjectCreate(
        title="Portfolio Web Application Backend",
        github_url="",
        image_thumbnail_url="/static/images/projects/backend/thumbnail.png",
        description=(
            "Developed a production-style backend platform using FastAPI, PostgreSQL, SQLAlchemy, "
            "and Pydantic. Implemented layered architecture, dependency injection, repositories, "
            "services, custom exception handling, and RESTful APIs to power my portfolio "
            "application."
        )
    ),

    ProjectCreate(
        title="Portfolio Web Application Frontend",
        github_url="",
        image_thumbnail_url="/static/images/projects/frontend/thumbnail.png",
        description=(
            "Modern portfolio frontend built with React and TypeScript, designed to consume "
            "the portfolio backend API and provide responsive project pages and interactive "
            "user experiences."
        )
    ),
]