import os
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ----------------------------
# FUNCTION: ONLYOFFICE-COMPATIBLE HYPERLINK
# ----------------------------
def add_hyperlink(paragraph, url, text):
    """
    Adds a clickable hyperlink to a paragraph compatible with ONLYOFFICE, Word, LibreOffice, Google Docs.
    """
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0000FF")  # blue
    rPr.append(color)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    r.append(t)
    hyperlink.append(r)
    paragraph._p.append(hyperlink)

# ----------------------------
# BUILD DOCUMENT
# ----------------------------
doc = Document()
doc.add_heading("Azure Entra Cloud Kerberos Trust – Risk Assessment Guide for Hybrid Environments", level=1)

# Objective
doc.add_heading("Objective", level=2)
doc.add_paragraph(
    "The purpose of this assessment is to evaluate the security, operational, and technical risks "
    "associated with enabling Azure Entra Cloud Kerberos Trust in a hybrid Active Directory environment "
    "to support Windows Hello for Business (WHfB) passwordless authentication. "
    "The goal is to provide a clear understanding of expected benefits, potential challenges, "
    "and mitigation strategies before adopting this technology."
)

# Executive Summary
doc.add_heading("Executive Summary", level=2)
doc.add_paragraph(
    "Azure Entra Cloud Kerberos Trust is a modern, cloud-driven authentication model that enables "
    "passwordless sign-in using Windows Hello for Business while still supporting access to on-premises Kerberos-secured resources. "
    "It eliminates the complexity of issuing certificates to every device and reduces the attack surface created by traditional passwords."
)
doc.add_paragraph(
    "Overall, the risk level is moderate, with a high security improvement. Most risks stem not from the model itself but from dependencies such as Azure AD Connect synchronization, "
    "cloud availability, and the multi-step configuration process."
)
doc.add_paragraph(
    "When properly deployed with monitoring, fallback authentication, and a phased rollout, Cloud Kerberos Trust significantly strengthens identity security and user experience."
)
doc.add_paragraph("Risk Level: MODERATE | Security Improvement: HIGH | Deployment Complexity: MEDIUM")

# Detailed Risk Assessment
doc.add_heading("Detailed Risk Assessment", level=2)

# 1. Security Risks
doc.add_heading("1. Security Risks", level=3)

# High Priority
p = doc.add_paragraph("Elimination of Password-Based Attacks: ")
add_hyperlink(p,
              "https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/hello-hybrid-cloud-kerberos-trust",
              "Microsoft Learn – WHfB Overview")
doc.add_paragraph(
    "Cloud Kerberos Trust removes passwords from the authentication flow, reducing exposure to phishing, credential stuffing, password spraying, and other password-centric attack vectors. "
    "WHfB uses asymmetric key cryptography and TPM-backed credentials, offering stronger protection than traditional passwords."
)

# Medium Priority
p = doc.add_paragraph("Azure Entra ID Dependency: ")
add_hyperlink(p,
              "https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/hello-hybrid-cloud-kerberos-trust",
              "Hybrid Cloud Kerberos Trust")
doc.add_paragraph(
    "Cloud Kerberos Trust relies on Azure Entra ID for issuing Cloud TGTs (Kerberos tickets). "
    "If Azure services experience an outage or degraded performance, sign-ins may be affected. "
    "Cached credentials provide limited offline access, but devices may not obtain new tickets during a prolonged disruption."
)

p = doc.add_paragraph("Certificate and Sync Dependencies: ")
add_hyperlink(p,
              "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/whatis-azure-ad-connect",
              "Azure AD Connect Health Documentation")
doc.add_paragraph(
    "Azure issues and rotates Cloud Kerberos certificates every 28 days. If Azure AD Connect is unhealthy or certificate synchronization is interrupted, authentication may fail."
)

# Low Priority
doc.add_paragraph("Privileged Access Misconfiguration: Improperly configuring the Cloud Kerberos Trust object, device permissions, or Azure roles could inadvertently expose elevated privileges.")
doc.add_paragraph("Mitigation: Apply least-privilege principles and perform regular audits of directory permissions.")

# 2. Operational Risks
doc.add_heading("2. Operational Risks", level=3)
p = doc.add_paragraph("Azure AD Connect Dependency: ")
add_hyperlink(p,
              "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/whatis-azure-ad-connect",
              "Azure AD Connect Overview")
doc.add_paragraph(
    "Healthy synchronization is essential because device identity, key material, and certificate metadata must flow between on-premises AD and Azure Entra ID. "
    "Sync failures can prevent new WHfB registrations or block key/certificate updates."
)
doc.add_paragraph(
    "Mitigation: Deploy redundant sync nodes, enable AD Connect Health monitoring, and validate sync interval performance."
)

doc.add_paragraph("Rollback Complexity: Rolling back from Cloud Kerberos Trust to password-based authentication requires structured planning to avoid user disruption.")

doc.add_paragraph("User Training: Some users may require adjustment to WHfB PIN or biometric authentication. Mitigation includes pilot groups, training, and dedicated support channels.")

# 3. Technical Risks
doc.add_heading("3. Technical Risks", level=3)
p = doc.add_paragraph("Compatibility Requirements: ")
add_hyperlink(p,
              "https://learn.microsoft.com/ja-jp/entra/identity/authentication/kerberos-faq",
              "Microsoft Kerberos FAQ")
doc.add_paragraph(
    "Cloud Kerberos Trust requires Windows 10 (20H1+) or Windows 11, supported Azure AD Connect versions, and an appropriate domain functional level. Older devices or missing TPM 2.0 are incompatible."
)

doc.add_paragraph(
    "Network Connectivity: Devices must occasionally connect to Azure to refresh Cloud TGTs, sync WHfB keys, and renew certificates. VPN access and monitoring for remote/offline devices are recommended."
)

doc.add_paragraph(
    "Configuration Complexity: Multi-step coordination between Azure Entra ID, on-prem AD, Azure AD Connect, and Group Policy is required. Misconfigurations can prevent Kerberos ticket issuance or weaken security. Follow Microsoft deployment guides and test in non-production."
)

# 4. Compliance & Governance Risks
doc.add_heading("4. Compliance & Governance Risks", level=3)
p = doc.add_paragraph("Data Residency and Audit Considerations: ")
add_hyperlink(p,
              "https://learn.microsoft.com/en-us/entra/identity/global-secure-access/data-residency",
              "Microsoft Data Residency Guidelines")
doc.add_paragraph(
    "Authentication metadata is processed in Azure, which may impact organizations with strict local data sovereignty requirements. Audit logs shift from on-premises to hybrid cloud; SIEM integration may require updates."
)

# Risk Mitigation Recommendations
doc.add_heading("Risk Mitigation Recommendations", level=2)
doc.add_paragraph(
    "Before Implementation:\n"
    "- Pilot 5–10% of users\n"
    "- Keep password fallback methods available\n"
    "- Validate Azure AD Connect health and redundancy\n"
    "- Confirm device readiness (OS, TPM, hardware security)\n"
)
doc.add_paragraph(
    "During Implementation:\n"
    "- Stage rollout with stabilization periods\n"
    "- Enable real-time alerts for sync failures, Kerberos ticket issues, and authentication errors\n"
    "- Provide dedicated support channel for WHfB issues\n"
)
doc.add_paragraph(
    "Post-Implementation:\n"
    "- Monitor authentication success rates\n"
    "- Perform quarterly DR drills including Azure outage scenarios\n"
    "- Review Conditional Access and WHfB policies monthly\n"
)

# Final Recommendation
doc.add_heading("Final Recommendation", level=2)
doc.add_paragraph(
    "Proceed with implementation using a phased rollout. The security gains from eliminating password-based authentication outweigh the manageable operational risks when monitoring, training, and proper configuration are in place."
)

# References
doc.add_heading("References", level=2)
references = [
    ("Microsoft Learn – Cloud Kerberos Trust Documentation",
     "https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/hello-hybrid-cloud-kerberos-trust"),
    ("Microsoft Learn – Kerberos Authentication Overview",
     "https://learn.microsoft.com/en-us/entra/identity/authentication/kerberos"),
    ("Azure AD Connect Overview",
     "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/whatis-azure-ad-connect"),
    ("Microsoft Kerberos FAQ",
     "https://learn.microsoft.com/ja-jp/entra/identity/authentication/kerberos-faq"),
    ("Windows Hello for Business Hybrid Deployment Guide",
     "https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/deploy/hybrid-cloud-kerberos-trust"),
    ("Microsoft Data Residency Guidelines",
     "https://learn.microsoft.com/en-us/entra/identity/global-secure-access/data-residency"),
    ("Community Report #1",
     "https://www.reddit.com//r/entra/comments/1lk4hz9"),
    ("Community Report #2",
     "https://www.reddit.com//r/entra/comments/1o34c80")
]

for title, link in references:
    p = doc.add_paragraph(f"{title}: ")
    add_hyperlink(p, link, link)

#------OLD CODE------
# Save document
#doc.save("Azure_Entra_Cloud_Kerberos_Risk_Assessment.docx")
#print("Document successfully created: Azure_Entra_Cloud_Kerberos_Risk_Assessment.docx")
#--------------------------------

# Define the folder and filename
folder_path = os.path.expanduser("~/my_projects/Personal/documents")
file_name = "Azure_Entra_Cloud_Kerberos_Risk_Assessment.docx"

# Ensure the folder exists
os.makedirs(folder_path, exist_ok=True)

# Save the document
full_path = os.path.join(folder_path, file_name)
doc.save(full_path)

print(f"Document successfully created: {full_path}")