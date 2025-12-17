# n8n Workflows Security Scan Report

**Total files**: 2772
**Successfully scanned**: 2772
**Errors**: 0

## Risk Summary

- **CRITICAL**: 13 workflows
- **HIGH**: 1508 workflows
- **MEDIUM**: 26 workflows
- **LOW**: 1225 workflows

## Critical Issues

### Extract spend details (template)
- File: `1443_Splitout_Extractfromfile_Automation_Triggered.json`
- Nodes: 24
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Extract invoice
  - **HARDCODED_CREDENTIAL** (CRITICAL): Extract payment

### Shopify + Mautic
- File: `1526_Mautic_Webhook_Automation_Webhook.json`
- Nodes: 26
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Crypto

### puq-docker-n8n-deploy
- File: `1825_Code_Webhook_Automation_Webhook.json`
- Nodes: 34
- Issues:
  - **HIGH_RISK_NODE** (HIGH): Code1
  - **HIGH_RISK_NODE** (HIGH): SSH
  - **HARDCODED_CREDENTIAL** (CRITICAL): Change Password

### Extract spend details (template)
- File: `1935_Splitout_Extractfromfile_Automation_Triggered.json`
- Nodes: 24
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Extract invoice
  - **HARDCODED_CREDENTIAL** (CRITICAL): Extract payment

### template-demo-chatgpt-image-1-with-drive-and-sheet copy
- File: `1983_Splitout_Converttofile_Automation_Webhook.json`
- Nodes: 16
- Issues:
  - **HIGH_RISK_NODE** (HIGH): HTTP Request
  - **HARDCODED_CREDENTIAL** (CRITICAL): Google Sheets1

### Unnamed
- File: `1283_Splitout_Webhook_Automation_Webhook.json`
- Nodes: 40
- Issues:
  - **HIGH_RISK_NODE** (HIGH): WooCommerce Get Orders
  - **HIGH_RISK_NODE** (HIGH): Decrypt email
  - **HARDCODED_CREDENTIAL** (CRITICAL): Decrypt email
  - **HIGH_RISK_NODE** (HIGH): Encrypt email
  - **HARDCODED_CREDENTIAL** (CRITICAL): Encrypt email
  - **HIGH_RISK_NODE** (HIGH): Decrypt email address
  - **HARDCODED_CREDENTIAL** (CRITICAL): Decrypt email address

### Unnamed
- File: `0164_Crypto_Webhook_Automate_Webhook.json`
- Nodes: 3
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Crypto

### Create, update, and get a user using the G Suite Admin node
- File: `0455_Manual_Gsuiteadmin_Create_Triggered.json`
- Nodes: 4
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): G Suite Admin

### Unnamed
- File: `0457_Splitout_Webhook_Create_Webhook.json`
- Nodes: 40
- Issues:
  - **HIGH_RISK_NODE** (HIGH): WooCommerce Get Orders
  - **HIGH_RISK_NODE** (HIGH): Decrypt email
  - **HARDCODED_CREDENTIAL** (CRITICAL): Decrypt email
  - **HIGH_RISK_NODE** (HIGH): Encrypt email
  - **HARDCODED_CREDENTIAL** (CRITICAL): Encrypt email
  - **HIGH_RISK_NODE** (HIGH): Decrypt email address
  - **HARDCODED_CREDENTIAL** (CRITICAL): Decrypt email address

### Unnamed
- File: `0615_Webhook_Filemaker_Create_Webhook.json`
- Nodes: 11
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Crypto

### Unnamed
- File: `workflow.json`
- Nodes: 3
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Crypto

### Unnamed
- File: `workflow.json`
- Nodes: 3
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Crypto

### Unnamed
- File: `workflow.json`
- Nodes: 11
- Issues:
  - **HARDCODED_CREDENTIAL** (CRITICAL): Run SQL query


## High Risk Issues

Found 1508 high-risk workflows.

- `video_to_shorts_Automation.json`: video to shorts Automation
- `workflow that watches a Google Drive folder for new PDFs, extracts text with OCR, formats it with GPT.json`: PDF OCR to Airtable Processor
- `1400_Wait_Code_Automation_Webhook.json`: AutoQoutesV2_template
- `1401_Code_Webhook_Automate_Webhook.json`: Workflow stats
- `1402_Code_Manual_Automation_Webhook.json`: LinkedIn Web Scraping with Bright Data MCP Server & Google Gemini
- `1405_Wait_Splitout_Automation_Webhook.json`: Unnamed
- `1407_Splitout_Schedule_Automation_Scheduled.json`: Unnamed
- `1408_Splitout_Code_Monitor_Triggered.json`: Unnamed
- `1412_Splitout_Code_Automation_Scheduled.json`: Scrape Trustpilot Reviews to Google Sheets
- `1415_Webhook_Respondtowebhook_Create_Webhook.json`: Dynamically generate HTML page from user request using OpenAI Structured Output

## Recommendations

1. **CRITICAL/HIGH workflows**: Review manually before use
2. **Hardcoded credentials**: Replace with n8n credentials system
3. **External URLs**: Verify domains are legitimate
4. **Code execution nodes**: Sandbox or disable if not needed
5. **HTTP (non-HTTPS)**: Upgrade to HTTPS where possible
