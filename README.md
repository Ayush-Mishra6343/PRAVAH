# PRAVAHA

### Turning Multilingual Crisis Reports into Actionable Intelligence.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Ayush-Mishra6343/PRAVAH)

**An AI-powered, multilingual crisis intelligence platform that transforms fragmented emergency reports into structured incidents, connected evidence, and prioritised relief recommendations.**

<p align="center">
  <strong>Listen. Understand. Connect. Respond.</strong>
</p>

<p align="center">
  Built for a world where emergencies don't wait for information to arrive in the right language, format, or place.
</p>

---

## The Problem

When a disaster strikes, information arrives from everywhere.

A resident sends a message in Hindi. A volunteer reports the same situation in Bengali. Someone else submits an English update. Another person reports that a road is blocked, while a later report says it has reopened.

These reports may describe the same evolving emergency, but they rarely arrive as one coherent picture.

Critical information becomes fragmented across languages, messages, locations, and timestamps. Responders must piece together what is happening while the situation continues to evolve.

**The problem isn't a lack of information. It's the inability to turn scattered information into a reliable understanding of the situation.**

## Introducing PRAVAHA

PRAVAHA is designed to bridge the gap between raw emergency reporting and actionable crisis intelligence.

It brings multilingual report intake, AI-powered information extraction, cross-language incident association, evidence inspection, and relief prioritisation into one unified interface.

Instead of treating every incoming message as an isolated record, PRAVAHA aims to build a connected picture of an unfolding incident—preserving the original reports, surfacing uncertainty, and helping people understand what is known, what is reported, and what still needs verification.

### Our vision

A crisis-response system where language is never a barrier to being heard, duplicate reports become useful corroborating signals, contradictions remain visible, and decisions are supported by traceable evidence rather than guesswork.

---

## Core Features

### 1. Multilingual Emergency Intelligence

**Understand the emergency, not just the language.**

Emergency reports can arrive in different Indian languages and in mixed-language speech or text.

PRAVAHA is designed to process these reports and extract information relevant to crisis response, including:

* Incident category, such as flooding or infrastructure damage.
* Reported location and available geographical details.
* People affected and situations requiring attention.
* Reported needs, such as drinking water, food, shelter, or medical assistance.
* Changes in conditions and follow-up information.

The objective is to transform unstructured reports into consistent, machine-readable incident information without discarding the context of the original message.

**Why it matters:** Information should remain useful even when different people describe the same emergency in completely different ways.

### 2. Voice-First Emergency Reporting

**When typing isn't practical, let people speak.**

In an emergency, users may be stressed, moving, or unable to type a detailed report.

PRAVAHA's voice-reporting workflow is designed to turn spoken emergency reports into text that can be reviewed and processed.

The intended workflow is:

1. Record an emergency report.
2. Transcribe the recording using a supported speech-recognition service.
3. Display the transcript for review and correction.
4. Extract structured information from the confirmed report.
5. Submit the report into the incident-intelligence workflow.

The planned speech stack includes Sarvam AI's Saaras speech-to-text capabilities, with support for multilingual reporting subject to the selected API's capabilities.

Voice reporting can make the platform more accessible to people who are uncomfortable typing or communicating in English.

**Design principle:** A transcription is not automatically a verified fact. Original wording and the distinction between reported and verified information must be preserved.

### 3. Cross-Language Incident Fusion

**Three languages. One potential incident. A clearer picture.**

One of PRAVAHA's central goals is to identify when multiple reports may refer to the same real-world event, even when their wording and language differ.

Consider these reports:

* Hindi: Floodwater is rising near a government school, and families are stranded.
* Bengali: Floodwater is rising near the government school, and several families are trapped.
* English: Families are stranded near the school and urgently need drinking water.

A conventional reporting application may store three separate records.

PRAVAHA aims to associate related reports with a common incident when their content and available contextual evidence support the connection.

This enables a more coherent incident view while retaining the individual reports that contributed to it.

The system must also distinguish between reports that merely sound similar and reports that plausibly describe the same event. Shared wording alone is insufficient to establish a match.

**The result:** A path from fragmented messages toward a unified, evidence-backed incident picture.

### 4. Evidence-Centred Incident Inspection

**Every important claim should have a traceable origin.**

AI-generated summaries can be useful, but they become dangerous when users cannot determine where a claim came from.

PRAVAHA is designed around the principle that incident information should remain connected to its supporting reports.

An evidence-inspection workflow can help users examine:

* The original submitted report.
* The recognised or normalised text.
* The information extracted from that report.
* Other reports associated with the incident.
* Conflicting statements or subsequent updates.
* Information that remains uncertain or unverified.

This makes it easier to distinguish the original report from the system's interpretation of it.

For example, a report stating that families are stranded should not silently become a verified count of affected people.

**Evidence before certainty. Context before conclusions.**

### 5. Contradiction and Incident Evolution Tracking

**An emergency is a moving situation, not a static record.**

Information changes as conditions evolve.

A road may initially be reported as blocked and later reported as reopened. Floodwater may continue rising even after a route becomes accessible.

PRAVAHA is designed to preserve these distinctions instead of treating every new message as a complete replacement for previous information.

A follow-up report should be interpreted in context:

* What has changed?
* Which earlier claim does the update concern?
* Does the new report contradict an earlier statement?
* Which aspects of the incident remain unresolved?
* Is further verification necessary?

The goal is to represent the evolution of an incident without erasing its history.

Contradictions should remain visible for review rather than being silently resolved through an unsupported AI assumption.

### 6. Incident Prioritisation

**Help users identify what may require attention first.**

Not every report describes the same level of urgency.

PRAVAHA is designed to organise incident information so that potentially urgent situations and reported needs are easier to identify.

Examples include:

* Reports of stranded families.
* Urgent requests for drinking water.
* Reported road obstructions.
* Infrastructure damage.
* Situations that may require medical assistance.

Prioritisation should be based on explicit incident information and transparent rules, rather than arbitrary scores presented as objective truth.

The platform's recommendations are decision-support outputs. They are not substitutes for trained responders or independently verified field assessments.

### 7. Relief Resource Intelligence

**Connect reported needs with available resources.**

Knowing that people need assistance is only part of the problem. Responders also need to understand which resources may be available and where they might be useful.

PRAVAHA is designed to connect incident needs with resource information and generate recommendations for potential relief priorities.

A resource-oriented workflow can help users consider:

* What has been reported as needed.
* Which resources are listed as available.
* Which incidents may require attention first.
* Which recommendations depend on incomplete information.
* What assumptions underlie a suggested allocation.

Where inventory data is simulated, it must be labelled as demonstration data. Recommendations based on simulated inventory must never be presented as confirmed real-world availability.

**The objective is better-informed prioritisation—not automated dispatch without human oversight.**

### 8. Unified Crisis Intelligence Dashboard

**One interface for understanding the situation.**

PRAVAHA brings the reporting and incident-analysis workflow into a single operational interface.

The intended dashboard experience includes:

| Component          | Purpose                                                                |
| ------------------ | ---------------------------------------------------------------------- |
| Overview Dashboard | Summarise incident activity and surface important information.         |
| Incident Feed      | Browse incoming and associated incident reports.                       |
| Evidence Inspector | Examine original reports and the claims extracted from them.           |
| Resource Centre    | Review available resource information and potential relief priorities. |
| Activity Timeline  | Follow incident updates and understand how reported conditions evolve. |
| Voice Reporting    | Capture spoken emergency reports and process their transcripts.        |

The interface is designed to reduce the cognitive burden of switching between individual messages, separate language translations, and disconnected incident records.

Instead of merely collecting reports, PRAVAHA aims to make their relationships and implications easier to understand.

*The availability of individual dashboard components depends on the current application implementation.*

---

## How PRAVAHA Works

PRAVAHA follows a reporting-to-intelligence workflow.

```text
       EMERGENCY REPORTS
      ┌──────────────────┐
      │  Text Messages   │
      │  Voice Reports   │
      │  Multiple Languages│
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │  Input Processing│
      │ Transcription   │
      │ Language Handling│
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ AI-Powered       │
      │ Information      │
      │ Extraction       │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Incident         │
      │ Association      │
      │ & Evidence Links │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Incident         │
      │ Intelligence     │
      │ & Prioritisation │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Human Review     │
      │ & Relief Support │
      └──────────────────┘
```

The exact services and processing stages depend on the integrations enabled in the deployed application.

### The underlying principle

**Preserve the source. Extract the meaning. Connect the evidence. Make uncertainty visible.**

PRAVAHA should never need to invent missing facts to produce a useful incident summary.

---

## Technology Stack

PRAVAHA is being developed around AI-assisted multilingual crisis reporting.

The intended technology stack includes the following components, subject to the integrations actually enabled in the application.

| Technology                | Intended role                                                     |
| ------------------------- | ----------------------------------------------------------------- |
| Sarvam AI Saaras          | Speech-to-text for voice-based reporting.                         |
| Sarvam AI language models | Extracting structured information from emergency reports.         |
| Sarvam Translate          | Optional translation between supported languages.                 |
| Bulbul TTS                | Optional spoken output for accessibility.                         |
| Sarvam Vision             | Optional processing of images or documents.                       |
| Web application           | Incident dashboard, reporting interface, and evidence inspection. |
| Backend services          | API orchestration, report processing, and application logic.      |

The actual frontend framework, backend framework, storage layer, and deployment architecture should be documented according to the current repository.

**Important:** A listed service is a planned capability unless its integration has been implemented and tested. Do not assume every optional Sarvam service is active.

---

## Example Scenario: One Flood, Multiple Reports

Imagine that flooding develops near a government school.

### Incoming information

**Report 1 — Hindi**

> सरकारी स्कूल के पास बाढ़ का पानी तेजी से बढ़ रहा है। कई परिवार फंसे हुए हैं और पीने के पानी की जरूरत है।

**Report 2 — Bengali**

> সরকারি স্কুলের কাছে বন্যার জল বাড়ছে। অনেক পরিবার আটকে আছে।

**Report 3 — English**

> Families are stranded near the government school due to flooding. Drinking water is urgently needed.

**Report 4 — Subsequent update**

> A local volunteer reports that the road near the school has reopened, but the flooding continues.

### What PRAVAHA should establish

1. The first three reports may describe the same flooding incident.
2. The original reports should remain accessible.
3. Stranded families and drinking-water requirements should be represented as reported information.
4. The later update should affect the road-access assessment.
5. The reopened road must not be interpreted as proof that the flood has ended.
6. A report from a different village should not be automatically merged without sufficient supporting evidence.

This example demonstrates the intended combination of multilingual understanding, incident association, evidence preservation, and evolving situation awareness.

It is a target workflow, not a claim that every scenario has already passed testing.

---

## Responsible AI and Operational Safety

Crisis intelligence requires more than a convincing AI-generated answer.

PRAVAHA is designed around several principles:

* **Source preservation:** Retain original reports rather than replacing them with generated summaries.
* **Traceability:** Make the relationship between claims and source reports inspectable.
* **Explicit uncertainty:** Distinguish reported information from independently verified information.
* **Conservative association:** Avoid merging unrelated incidents solely because they contain similar language.
* **Visible contradictions:** Preserve conflicting reports for review.
* **Human oversight:** Keep consequential relief decisions under appropriate human control.
* **Data honesty:** Clearly label simulated inventory, sample reports, and demonstration-only information.
* **Credential security:** Keep API keys and secrets out of frontend code and public repositories.

PRAVAHA is a decision-support platform, not a substitute for official emergency services or verified field intelligence.

---

## Getting Started

The following steps assume a compatible local development environment. The precise commands depend on the framework and package manager used in this repository.

### 1. Clone the repository

```bash
git clone https://github.com/Ayush-Mishra6343/PRAVAH.git
cd PRAVAH
```

### 2. Install dependencies

Follow the instructions for the project's actual framework and dependency manager.

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file if the application requires one.

For example:

```env
SARVAM_API_KEY=your_api_key_here
```

Use the variable names expected by the actual codebase. This example is illustrative; it must not replace the application's existing configuration.

Never commit `.env` files or real credentials.

### 4. Start the application

Use the startup command documented for the project's framework:

```bash
python run.py
```

The application runs on port 8000:

```text
http://127.0.0.1:8000/
```

### 5. Test the reporting workflow

Verify that you can:

1. Open the dashboard.
2. Submit a text-based emergency report.
3. Record and transcribe a voice report, if supported.
4. Review the resulting incident information.
5. Inspect the original report and extracted claims.
6. Examine how related reports and subsequent updates are handled.

Use demonstration data unless the application is configured for an authorised real-world deployment.

---

## Current Development Status

PRAVAHA is an evolving project.

The product vision encompasses multilingual reporting, speech recognition, structured incident extraction, cross-language incident association, evidence inspection, and relief-support workflows.

The actual status of each feature must be determined by the current codebase and test results.

| Area                          | Status to establish                                     |
| ----------------------------- | ------------------------------------------------------- |
| Dashboard and navigation      | Verify against the running application.                 |
| Text-based incident reporting | Test submission and persistence.                        |
| Multilingual processing       | Verify supported languages and actual model responses.  |
| Speech-to-text                | Confirm a real API integration and test recorded audio. |
| Incident association          | Test related and unrelated reports.                     |
| Evidence inspection           | Verify access to original reports and extracted claims. |
| Contradiction handling        | Test evolving and conflicting reports.                  |
| Resource recommendations      | Verify whether data is simulated or real.               |
| Deployment                    | Confirm the deployed URL and test it independently.     |

A visible interface alone does not establish that its underlying workflow is functional.

---

## Roadmap

Potential development priorities include:

* [ ] Reliable voice reporting and editable transcripts.
* [ ] Broader testing across supported Indian languages.
* [ ] Improved cross-language incident association.
* [ ] Claim-level source attribution.
* [ ] More robust contradiction and update handling.
* [ ] Geographic incident visualisation using verified location data.
* [ ] Resource prioritisation with transparent assumptions.
* [ ] Automated tests for critical reporting workflows.
* [ ] Secure, persistent storage and appropriate data-retention controls.
* [ ] Public deployment with verified backend connectivity.

These items represent development priorities, not guaranteed features of the current release.

---

## Why PRAVAHA?

Many applications collect emergency reports.

PRAVAHA's ambition is to help users understand how those reports fit together.

A message in Hindi, another in Bengali, and a third in English may contain complementary pieces of information about one unfolding situation. A subsequent report may change the accessibility assessment without changing the underlying emergency.

The value lies in preserving those details, connecting the evidence, and making the resulting information easier to interpret.

**From fragmented reports to connected intelligence.**

**From isolated messages to a clearer operational picture.**

**From information overload to better-informed decisions.**

That is the problem PRAVAHA is built to address.

---

## Disclaimer

PRAVAHA is a developing crisis-intelligence and decision-support project. Its outputs may contain errors, omissions, or uncertain interpretations.

AI-generated incident details and recommendations must not be treated as independently verified facts. Demonstration data must not be interpreted as live emergency information or confirmed resource availability.

The platform is not a replacement for official emergency-response systems, trained responders, or emergency services.

---

<p align="center">
  <strong>PRAVAHA</strong><br/>
  Multilingual Crisis Intelligence<br/><br/>
  <em>Every report matters. Every language counts. Every claim deserves context.</em>
</p>
