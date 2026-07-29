# Homelab Directory Tree

```text
homelab
├── .github
│   └── workflows
│       ├── index-generation.yml
│       ├── ci.yml
│       ├── README.md
│       ├── metadata-validation.yml
│       └── documentation-validation.yml
├── Architecture
│   ├── ai
│   │   ├── Agents.md
│   │   ├── MCP.md
│   │   ├── Memory.md
│   │   ├── Models.md
│   │   ├── README.md
│   │   └── FuturePlans.md
│   ├── hardware
│   │   ├── Desktop.md
│   │   ├── AIServer.md
│   │   ├── Servers.md
│   │   ├── Rack.md
│   │   ├── README.md
│   │   └── UpgradePath.md
│   ├── networking
│   │   ├── DNS.md
│   │   ├── VLANs.md
│   │   ├── Firewall.md
│   │   ├── Routing.md
│   │   └── README.md
│   ├── standards
│   │   ├── AuditStandardImplementationPlan.md
│   │   ├── BackupStandard.md
│   │   ├── AI-Development-Standard.md
│   │   ├── Service Lifecycle Standard v1.0.md
│   │   ├── DockerStandard.md
│   │   ├── DocumentationStandard.md
│   │   ├── HomelabArchitectureStandard.md
│   │   ├── NamingConventionStandard.md
│   │   ├── SecurityStandard.md
│   │   ├── StandardsRoadmap.md
│   │   └── archive
│   │       ├── SelfHostingDocumentationGuide.md
│   │       └── InitialAIArchitectureProposal.md
│   ├── decisions
│   │   ├── ADRIndex.md
│   │   ├── ADRTemplate.md
│   │   └── README.md
│   └── Templates
├── ansible
│   └── README.md
├── audit
│   └── ComposeV1.md
├── compose
│   ├── ai
│   │   ├── README.md
│   │   ├── llama
│   │   │   └── compose.yml
│   │   └── ollama-openwebui
│   │       ├── compose.yaml
│   │       ├── backup-volumes.sh
│   │       ├── compose-nvidia.yaml
│   │       └── 20b-olla-compose.yaml
│   ├── automation
│   │   └── README.md
│   ├── development
│   │   └── README.md
│   ├── monitoring
│   │   └── README.md
│   ├── networking
│   │   └── README.md
│   ├── productivity
│   │   └── README.md
│   ├── security
│   │   └── README.md
│   ├── storage
│   │   └── README.md
│   └── media
│       └── README.md
├── docs
├── Documentation
│   ├── services
│   ├── runbooks
│   │   ├── AMDMaxLLMSetup.md
│   │   ├── DisasterRecovery.md
│   │   ├── Backup.md
│   │   ├── Deploy.md
│   │   ├── ZFSCleanupAndMonitoring.md
│   │   ├── ProxmoxTrixieUpgrade.md
│   │   ├── Restore.md
│   │   └── Updates.md
│   └── troubleshooting
│       ├── Docker.md
│       ├── GPU.md
│       ├── Traefik.md
│       ├── OpenWebUIRecoveryAndUpgrade.md
│       └── Networking.md
├── Indexes
│   ├── ADRIndex.md
│   ├── DocumentationIndex.md
│   ├── README.md
│   ├── StandardsIndex.md
│   └── TemplateIndex.md
├── Services
│   ├── ServiceCatalog.md
│   ├── ServiceIndex.md
│   ├── Anonaddy.md
│   ├── Beszel.md
│   ├── Ollama.md
│   ├── Traefik.md
│   ├── WireGuard.md
│   ├── Nextcloud.md
│   ├── Jellyfin.md
│   ├── PaperlessNGX.md
│   ├── Karakeep.md
│   └── ServiceCatalog.md
├── Scripts
│   ├── auto-sync.sh
│   ├── generate_kerberos_risk_assessment.py
│   ├── pdf_maker.py
│   ├── pdf_template_maker.py
│   ├── smart_doc_to_pdf.py
│   ├── smart_doc_to_pdf_v2.py
│   └── llm-updates
│       ├── pdf_maker.py
│       ├── ollama_resource_management.py
│       └── ...
├── Templates
│   ├── .env.example
│   ├── ComposeTemplate.yaml
│   ├── ReadmeTemplate.md
│   ├── README.md
│   ├── ServiceChecklist.md
│   └── Versions.md
├── Validation
│   ├── README.md
│   └── Phase8-Completion-Report.md
├── Assets
│   └── README.md
├── test
│   ├── ReadTest.md
│   └── WriteTest.md
├── scripts
│   └── README.md
├── .gitignore
├── LICENSE
├── Navigation.md
├── README.md
├── homelab_file_list.txt
├── homelab_folder_list.txt
├── duplicate_report.txt
├── validation_output.txt
└── MIGRATION_REPORT.md
```

This tree reflects all directories and files listed in `homelab_folder_list.txt` and `homelab_file_list.txt`, organized for readability.