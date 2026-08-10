from app.models.project_image import ProjectImage


PROJECT_IMAGES: list[ProjectImage] = [

    # =====================================================
    # Project 1 - Enterprise Network Infrastructure
    # =====================================================

    ProjectImage(
        project_id=1,
        title="Cisco Enterprise Network Diagram",
        description=(
            "Cisco Packet Tracer network topology showing the enterprise "
            "infrastructure, including the ISP connection, core switch, "
            "access switches, server infrastructure, and connected "
            "departmental workstations."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/cisco-diagram.png",
        display_order=1,
    ),

    ProjectImage(
        project_id=1,
        title="Enterprise Physical Topology",
        description=(
            "Physical network topology illustrating the enterprise network "
            "layout, including the core infrastructure, access switches, "
            "server infrastructure, and connected endpoints."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/Physical-Topology.png",
        display_order=2,
    ),

    ProjectImage(
        project_id=1,
        title="Inter-VLAN Routing Design",
        description=(
            "Layer 3 switching architecture showing VLAN gateways, subnet "
            "assignments, and network segmentation used for inter-VLAN routing."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/inter-vlan-routing.png",
        display_order=3,
    ),

    ProjectImage(
        project_id=1,
        title="VLAN Configuration Verification",
        description=(
            "Verified VLAN creation and activation on the core switch using "
            "the 'show vlan brief' command."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/show-vlan-brief.png",
        display_order=4,
    ),

    ProjectImage(
        project_id=1,
        title="Layer 3 Interface Verification",
        description=(
            "Verified Switch Virtual Interfaces (SVIs) and gateway addresses "
            "for each VLAN using the 'show ip interface brief' command."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/show-ip-interface-brief.png",
        display_order=5,
    ),

    ProjectImage(
        project_id=1,
        title="DHCP Scope Configuration",
        description=(
            "Configured DHCP address pools for each VLAN, including default "
            "gateway, DNS server, subnet mask, and address ranges."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/dhcp-server-scopes.png",
        display_order=6,
    ),

    ProjectImage(
        project_id=1,
        title="DHCP Client Lease",
        description=(
            "Client workstation successfully obtained its IPv4 address, "
            "subnet mask, default gateway, and DNS server from the "
            "enterprise DHCP service."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/dhcp-client-ip-configuration.png",
        display_order=7,
    ),

    ProjectImage(
        project_id=1,
        title="Inter-VLAN Connectivity Verification",
        description=(
            "Verified Layer 3 routing by successfully reaching hosts across "
            "multiple VLANs from a client workstation."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/inter-vlan-ping.png",
        display_order=8,
    ),

    ProjectImage(
        project_id=1,
        title="End-to-End Network Validation",
        description=(
            "Validated end-to-end network connectivity by successfully "
            "reaching enterprise servers and devices across multiple VLANs."
        ),
        image_url="/static/images/projects/enterprise-network-infrastructure/dhcp-intervlan-ping-test.png",
        display_order=9,
    ),


    # =====================================================
    # Project 2 - Enterprise Hybrid Cloud Platform
    # =====================================================

    ProjectImage(
        project_id=2,
        title="Hybrid Cloud Architecture",
        description=(
            "High-level architecture connecting AWS, Microsoft Azure, and an "
            "on-premises environment using WireGuard site-to-site VPN tunnels."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/logical-network.png",
        display_order=1,
    ),

    ProjectImage(
        project_id=2,
        title="AWS Cloud Architecture",
        description=(
            "AWS VPC architecture containing an Application Load Balancer, "
            "ECS cluster, Amazon RDS PostgreSQL, and a WireGuard VPN gateway."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/aws-architecture.png",
        display_order=2,
    ),

    ProjectImage(
        project_id=2,
        title="Azure Cloud Architecture",
        description=(
            "Azure Virtual Network hosting Windows Server 2025 Active Directory "
            "Domain Services, DNS, internal services, and a WireGuard gateway."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/azure-architecture.png",
        display_order=3,
    ),

    ProjectImage(
        project_id=2,
        title="On-Premises Architecture",
        description=(
            "VMware Workstation environment representing the enterprise "
            "on-premises network with development and security workstations "
            "connected through WireGuard."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/on-premises-architecture.png",
        display_order=4,
    ),

    ProjectImage(
        project_id=2,
        title="WireGuard Hub-and-Spoke VPN",
        description=(
            "Hub-and-spoke WireGuard topology securely connecting AWS, Azure, "
            "and the on-premises environment through encrypted VPN tunnels."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/vpn-architecture.png",
        display_order=5,
    ),

    ProjectImage(
        project_id=2,
        title="AWS Linux Routing Table",
        description=(
            "Linux routing table showing AWS routes configured for Azure and "
            "on-premises networks through the WireGuard interface."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/aws-ip-route.png",
        display_order=6,
    ),

    ProjectImage(
        project_id=2,
        title="Azure Linux Routing Table",
        description=(
            "Linux routing table for the Azure WireGuard gateway demonstrating "
            "hybrid network routing."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/azure-ip-route.png",
        display_order=7,
    ),

    ProjectImage(
        project_id=2,
        title="On-Premises Linux Routing Table",
        description=(
            "Linux routing table for the on-premises WireGuard gateway providing "
            "connectivity to AWS and Azure."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/on-premises-ip-route.png",
        display_order=8,
    ),

    ProjectImage(
        project_id=2,
        title="AWS VPC Route Table",
        description=(
            "AWS route table forwarding Azure and on-premises traffic to the "
            "WireGuard VPN gateway."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/aws-routing-table.png",
        display_order=9,
    ),

    ProjectImage(
        project_id=2,
        title="Azure Route Table",
        description=(
            "Azure route table forwarding AWS and on-premises traffic through "
            "the WireGuard virtual appliance."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/azure-route-table.png",
        display_order=10,
    ),

    ProjectImage(
        project_id=2,
        title="Windows Persistent Routes",
        description=(
            "Persistent Windows routing configuration enabling communication "
            "with remote hybrid cloud networks."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/windows-persistent-routes.png",
        display_order=11,
    ),

    ProjectImage(
        project_id=2,
        title="Traceroute to Azure",
        description=(
            "Traceroute validating successful end-to-end connectivity from "
            "the on-premises network to Azure through the WireGuard VPN."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/traceroute-to-azure.png",
        display_order=12,
    ),

    ProjectImage(
        project_id=2,
        title="Traceroute to On-Premises",
        description=(
            "Traceroute validating successful connectivity from Azure to the "
            "on-premises network through the encrypted WireGuard tunnel."
        ),
        image_url="/static/images/projects/enterprise-hybrid-cloud-platform/traceroute-to-onprem.png",
        display_order=13,
    ),


    # =====================================================
    # Project 3 - Enterprise Infrastructure Automation
    # =====================================================

    ProjectImage(
        project_id=3,
        title="VPN Resource Automation",
        description=(
            "CLI automation successfully starting and stopping the hybrid VPN "
            "resources across AWS, Azure, and VMware environments with health "
            "checks and operation status reporting."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/vpn_start_stop.png",
        display_order=1,
    ),

    ProjectImage(
        project_id=3,
        title="VPN Automation Logs",
        description=(
            "Application logs showing health checks, VPN startup and shutdown "
            "operations, WireGuard virtual machines, and successful resource "
            "state transitions across the hybrid environment."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/vpn_log.png",
        display_order=2,
    ),

    ProjectImage(
        project_id=3,
        title="Domain Controller Automation",
        description=(
            "CLI automation successfully starting and stopping the domain "
            "controller resource while performing Azure and on-premises "
            "health checks."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/domain_controller_start_stop.png",
        display_order=3,
    ),

    ProjectImage(
        project_id=3,
        title="Domain Controller Automation Logs",
        description=(
            "Application logs showing domain controller health verification, "
            "ONPREM-DC01 startup and shutdown operations, and successful "
            "resource state transitions."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/domain_controller_log.png",
        display_order=4,
    ),

    ProjectImage(
        project_id=3,
        title="Security Resource Automation",
        description=(
            "CLI automation successfully starting and stopping the security "
            "environment while verifying VMware availability and the configured "
            "Kali Linux virtual machine."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/security_start_stop.png",
        display_order=5,
    ),

    ProjectImage(
        project_id=3,
        title="Security Automation Logs",
        description=(
            "Application logs showing VMware health checks, Kali Linux virtual "
            "machine verification, and successful security environment startup "
            "and shutdown operations."
        ),
        image_url="/static/images/projects/enterprise-infrastructure-automation/security_log.png",
        display_order=6,
    ),


    # =====================================================
    # Project 4 - Portfolio Backend API
    # =====================================================

    ProjectImage(
        project_id=4,
        title="Project API Endpoints",
        description=(
            "FastAPI project endpoints providing operations for retrieving, "
            "creating, updating, and deleting portfolio projects."
        ),
        image_url="/static/images/projects/portfolio-backend/api-project-endpoints.png",
        display_order=1,
    ),

    ProjectImage(
        project_id=4,
        title="Project Relationship Endpoints",
        description=(
            "FastAPI endpoints managing project relationships with technologies "
            "and skills through nested resource operations."
        ),
        image_url="/static/images/projects/portfolio-backend/api-project-relations.png",
        display_order=2,
    ),

    ProjectImage(
        project_id=4,
        title="Skill API Endpoints",
        description=(
            "FastAPI skill endpoints providing operations for retrieving, "
            "creating, updating, and deleting technical skills."
        ),
        image_url="/static/images/projects/portfolio-backend/api-skill-endpoints.png",
        display_order=3,
    ),

    ProjectImage(
        project_id=4,
        title="Technology API Endpoints",
        description=(
            "FastAPI technology endpoints providing operations for retrieving, "
            "creating, updating, and deleting technologies."
        ),
        image_url="/static/images/projects/portfolio-backend/api-technology-endpoints.png",
        display_order=4,
    ),

    ProjectImage(
        project_id=4,
        title="Project Image Database Model",
        description=(
            "SQLAlchemy database model defining project images, including image "
            "URLs, titles, descriptions, display ordering, and the relationship "
            "to projects."
        ),
        image_url="/static/images/projects/portfolio-backend/backend-project-image-model.png",
        display_order=5,
    ),

    ProjectImage(
        project_id=4,
        title="Project Database Model",
        description=(
            "SQLAlchemy project model defining project metadata and relationships "
            "with technologies, skills, and project images."
        ),
        image_url="/static/images/projects/portfolio-backend/backend-project-model.png",
        display_order=6,
    ),

    ProjectImage(
        project_id=4,
        title="Project Technology Database Model",
        description=(
            "SQLAlchemy association model defining the many-to-many relationship "
            "between portfolio projects and technologies."
        ),
        image_url="/static/images/projects/portfolio-backend/backend-project-technology-model.png",
        display_order=7,
    ),
]