---
name: fhir-developer
description: HL7 FHIR R4 healthcare API development and SMART-on-FHIR authorization specialist. Covers FHIR resource modeling (Patient, Observation, Encounter, Condition, MedicationRequest), CRUD operations, search parameters, Bundle transactions, SMART-on-FHIR OAuth 2.0 scopes and launch flows, OperationOutcome error handling, terminology services, and conformance resources. Use when user mentions FHIR, FHIR API, FHIR server, FHIR resource, SMART-on-FHIR, EHR integration, healthcare API, HL7, Patient resource, Observation, Bundle, FHIR search, FHIR transaction, FHIR OAuth, FHIR scopes, CapabilityStatement, ValueSet, CodeSystem, HAPI FHIR, or healthcare interoperability.
---

# HL7 FHIR R4 Developer

Comprehensive guide for building healthcare APIs using HL7 FHIR R4 (Release 4), the dominant interoperability standard for electronic health records. Covers resource modeling, RESTful CRUD operations, search mechanics, Bundle transactions, SMART-on-FHIR authorization, terminology services, and server implementation patterns.

FHIR (Fast Healthcare Interoperability Resources) uses a RESTful paradigm with JSON or XML serialization. Every clinical concept maps to a Resource type. Resources are identified by `{base}/{ResourceType}/{id}` and versioned via `meta.versionId`.

## Report-First Workflow

1. **Create report file immediately**: `fhir_implementation_report.md` with all section headers
2. **Add placeholders**: Mark each section `[Developing...]`
3. **Populate progressively**: Update sections as API design and code are produced
4. **Never show raw tool output**: Synthesize findings into report sections
5. **Final verification**: Ensure no `[Developing...]` placeholders remain

## When NOT to Use This Skill

- Clinical decision support logic or drug interactions -> use `clinical-decision-support`
- HL7 v2 message parsing (ADT, ORM, ORU) -> handle directly or use integration middleware
- DICOM imaging workflows -> handle directly with DICOM tooling
- General REST API design without healthcare context -> handle directly

---

## FHIR R4 Resource Model

### Core Clinical Resources

| Resource | Purpose | Key Fields | Common Use |
|----------|---------|------------|------------|
| **Patient** | Demographics | identifier, name, birthDate, gender, address, telecom | Master patient index |
| **Observation** | Clinical measurements | code, value[x], status, effectiveDateTime, subject | Lab results, vitals, social history |
| **Encounter** | Visit/admission | class, status, period, participant, reasonCode | ED visits, inpatient stays, telehealth |
| **Condition** | Diagnoses/problems | code, clinicalStatus, verificationStatus, onsetDateTime | Problem list, encounter diagnoses |
| **MedicationRequest** | Prescriptions | medicationCodeableConcept, dosageInstruction, status, intent | Active medications, orders |
| **Medication** | Drug definitions | code, form, ingredient, manufacturer | Formulary entries |
| **AllergyIntolerance** | Allergies/sensitivities | code, type, category, criticality, reaction | Allergy list |
| **Procedure** | Clinical procedures | code, status, performedDateTime, bodySite | Surgical history, interventions |
| **DiagnosticReport** | Report wrapper | code, status, result (Reference[Observation]), presentedForm | Lab panels, radiology reports |

### Administrative Resources

| Resource | Purpose | Key Fields |
|----------|---------|------------|
| **Practitioner** | Clinician | identifier (NPI), name, qualification |
| **Organization** | Healthcare org | identifier, name, type, address |
| **Location** | Physical place | name, address, position, managingOrganization |
| **Coverage** | Insurance | subscriber, beneficiary, payor, class |
| **Claim** | Billing | type, provider, diagnosis, item, total |

### Infrastructure Resources

| Resource | Purpose | Key Fields |
|----------|---------|------------|
| **CapabilityStatement** | Server capabilities | rest.resource, rest.interaction, rest.searchParam |
| **StructureDefinition** | Resource profiles | type, baseDefinition, differential, snapshot |
| **ValueSet** | Allowed code values | compose.include, expansion.contains |
| **CodeSystem** | Code definitions | concept, content (complete/fragment/not-present) |
| **ConceptMap** | Code mappings | group.element.target, equivalence |
| **OperationDefinition** | Custom operations | parameter, resource, system/type/instance |
| **SearchParameter** | Custom search params | base, expression, type |

---

## FHIR Data Types

### Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | UTF-8 text | `"John Doe"` |
| `boolean` | true/false | `true` |
| `integer` | 32-bit signed | `42` |
| `decimal` | Arbitrary precision | `98.6` |
| `date` | Date only (YYYY, YYYY-MM, YYYY-MM-DD) | `"2024-03-15"` |
| `dateTime` | Date + optional time + timezone | `"2024-03-15T10:30:00Z"` |
| `instant` | Precise timestamp with timezone (required) | `"2024-03-15T10:30:00.000+00:00"` |
| `uri` | URI reference | `"http://hl7.org/fhir/sid/icd-10-cm"` |
| `code` | Controlled string from ValueSet | `"active"` |
| `id` | Resource logical ID ([A-Za-z0-9\-\.]{1,64}) | `"abc-123"` |
| `canonical` | Canonical URL for conformance resources | `"http://hl7.org/fhir/ValueSet/observation-codes"` |

### Complex Types

#### Coding vs CodeableConcept

This is the most commonly confused distinction in FHIR. Understanding it is essential.

```
Coding (single code from a single system):
{
  "system": "http://loinc.org",
  "code": "8867-4",
  "display": "Heart rate"
}

CodeableConcept (wrapper for one or more Codings + optional text):
{
  "coding": [
    {
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    },
    {
      "system": "http://snomed.info/sct",
      "code": "364075005",
      "display": "Heart rate"
    }
  ],
  "text": "Heart rate"
}
```

**Rule**: CodeableConcept allows the same concept to be expressed in multiple code systems simultaneously. The `text` field is the human-readable fallback. Always include `text` for clinical safety.

**When to use which**:
- `Coding` appears inside `CodeableConcept` and in `meta.tag`, `meta.security`
- `CodeableConcept` is used for most clinical coded fields (Condition.code, Observation.code, etc.)
- The first Coding in the array is typically the "preferred" representation

#### Reference

```
Internal reference (to a resource on the same server):
{
  "reference": "Patient/123",
  "display": "Jane Smith"
}

Absolute reference (to a resource on another server):
{
  "reference": "https://other-server.example.com/fhir/Patient/456",
  "display": "Jane Smith"
}

Logical reference (by identifier, no server resolution):
{
  "identifier": {
    "system": "http://hospital.example.com/mrn",
    "value": "MRN-12345"
  },
  "display": "Jane Smith"
}
```

**Best practice**: Always include `display` for human readability. Use logical references for cross-system interoperability when the target server is unknown.

#### Identifier

```json
{
  "use": "official",
  "type": {
    "coding": [
      {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
        "code": "MR"
      }
    ]
  },
  "system": "http://hospital.example.com/mrn",
  "value": "MRN-12345",
  "period": {
    "start": "2020-01-01"
  },
  "assigner": {
    "display": "General Hospital"
  }
}
```

**Common identifier systems**:
| System URI | Identifier Type |
|-----------|----------------|
| `http://hl7.org/fhir/sid/us-ssn` | US Social Security Number |
| `http://hl7.org/fhir/sid/us-npi` | National Provider Identifier |
| `urn:oid:2.16.840.1.113883.4.1` | SSN (OID form) |
| `http://terminology.hl7.org/NamingSystem/CMSCertificationNumber` | CMS Certification Number |

#### HumanName

```json
{
  "use": "official",
  "family": "Smith",
  "given": ["Jane", "Marie"],
  "prefix": ["Dr."],
  "suffix": ["MD"],
  "period": {
    "start": "2000-01-01"
  }
}
```

**Rule**: `given` is an array (first name, middle name). `family` is a single string. Use `text` for names that do not decompose cleanly into Western given/family structure.

#### Address

```json
{
  "use": "home",
  "type": "physical",
  "line": ["123 Main St", "Apt 4B"],
  "city": "Springfield",
  "state": "IL",
  "postalCode": "62701",
  "country": "US",
  "period": {
    "start": "2020-01-01"
  }
}
```

#### ContactPoint

```json
{
  "system": "phone",
  "value": "+1-555-555-1234",
  "use": "mobile",
  "rank": 1
}
```

Systems: `phone`, `fax`, `email`, `pager`, `url`, `sms`, `other`.

#### Quantity

```json
{
  "value": 120,
  "unit": "mmHg",
  "system": "http://unitsofmeasure.org",
  "code": "mm[Hg]"
}
```

**Rule**: Always use UCUM (`http://unitsofmeasure.org`) for units. The `code` is the machine-readable UCUM code; `unit` is the human-readable display.

---

## CRUD Operations

### HTTP Semantics

| Operation | HTTP Method | URL Pattern | Request Body | Success Code |
|-----------|------------|-------------|-------------|-------------|
| **Create** | POST | `{base}/{ResourceType}` | Resource (no id) | 201 Created |
| **Read** | GET | `{base}/{ResourceType}/{id}` | None | 200 OK |
| **Update** | PUT | `{base}/{ResourceType}/{id}` | Full resource (with id) | 200 OK |
| **Partial Update** | PATCH | `{base}/{ResourceType}/{id}` | JSON Patch or FHIRPath Patch | 200 OK |
| **Delete** | DELETE | `{base}/{ResourceType}/{id}` | None | 204 No Content |
| **Version Read** | GET | `{base}/{ResourceType}/{id}/_history/{vid}` | None | 200 OK |
| **History** | GET | `{base}/{ResourceType}/{id}/_history` | None | 200 OK (Bundle) |
| **Search** | GET/POST | `{base}/{ResourceType}?params` | None or form-encoded | 200 OK (Bundle) |

### Create

```
POST /fhir/Patient
Content-Type: application/fhir+json

{
  "resourceType": "Patient",
  "name": [{"family": "Smith", "given": ["Jane"]}],
  "gender": "female",
  "birthDate": "1990-05-15"
}

Response: 201 Created
Location: /fhir/Patient/abc-123/_history/1
```

**Conditional Create** (prevent duplicates):
```
POST /fhir/Patient
If-None-Exist: identifier=http://hospital.example.com/mrn|MRN-12345
```
Returns 200 if a match already exists (no new resource created), 201 if created.

### Update

```
PUT /fhir/Patient/abc-123
Content-Type: application/fhir+json
If-Match: W/"1"

{
  "resourceType": "Patient",
  "id": "abc-123",
  "name": [{"family": "Smith", "given": ["Jane", "Marie"]}],
  "gender": "female",
  "birthDate": "1990-05-15"
}

Response: 200 OK
ETag: W/"2"
```

**Critical**: PUT replaces the entire resource. Any fields omitted from the PUT body are deleted. Always read-then-update to avoid data loss.

### Partial Update (PATCH)

```
PATCH /fhir/Patient/abc-123
Content-Type: application/json-patch+json

[
  {"op": "replace", "path": "/birthDate", "value": "1990-05-16"},
  {"op": "add", "path": "/telecom/-", "value": {"system": "email", "value": "jane@example.com"}}
]
```

### Conditional Operations

| Operation | Syntax | Example |
|-----------|--------|---------|
| Conditional Create | `POST` + `If-None-Exist` header | `If-None-Exist: identifier=http://mrn|123` |
| Conditional Update | `PUT {base}/{Type}?search-params` | `PUT /Patient?identifier=http://mrn|123` |
| Conditional Delete | `DELETE {base}/{Type}?search-params` | `DELETE /Patient?identifier=http://mrn|123` |

### HTTP Status Codes

| Code | Meaning | When Returned |
|------|---------|---------------|
| **200 OK** | Successful read, update, or search | GET, PUT, PATCH, POST (search) |
| **201 Created** | Successful create | POST |
| **204 No Content** | Successful delete | DELETE |
| **304 Not Modified** | Conditional read, resource unchanged | GET with If-None-Match |
| **400 Bad Request** | Malformed request | Invalid JSON, bad parameters |
| **401 Unauthorized** | Missing or invalid credentials | No token, expired token |
| **403 Forbidden** | Insufficient scopes/permissions | Token lacks required scope |
| **404 Not Found** | Resource does not exist | GET/PUT/DELETE with unknown id |
| **405 Method Not Allowed** | Operation not supported | DELETE on a read-only server |
| **409 Conflict** | Version conflict | PUT without correct If-Match ETag |
| **410 Gone** | Resource was deleted | GET on a deleted resource |
| **412 Precondition Failed** | ETag mismatch | If-Match header does not match current version |
| **422 Unprocessable Entity** | Validation failure | Resource violates profile constraints |
| **429 Too Many Requests** | Rate limited | Exceeded server rate limit |

### OperationOutcome for Error Responses

Every error response SHOULD include an OperationOutcome resource:

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error",
      "code": "processing",
      "diagnostics": "Patient.birthDate: Value '1990-13-01' is not a valid date",
      "location": ["Patient.birthDate"],
      "expression": ["Patient.birthDate"]
    }
  ]
}
```

**Issue severity levels**: `fatal`, `error`, `warning`, `information`.

**Issue codes** (common): `invalid`, `structure`, `required`, `value`, `processing`, `not-found`, `conflict`, `lock-error`, `exception`, `security`, `login`, `throttled`, `informational`.

---

## Search Parameters

### Common Search Parameters (All Resources)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `_id` | token | Logical ID | `_id=abc-123` |
| `_lastUpdated` | date | Last modification time | `_lastUpdated=gt2024-01-01` |
| `_tag` | token | Resource tag | `_tag=http://example.com|important` |
| `_profile` | reference | Conformance profile | `_profile=http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient` |
| `_security` | token | Security label | `_security=http://terminology.hl7.org/CodeSystem/v3-Confidentiality|R` |
| `_text` | string | Full-text search on narrative | `_text=diabetes` |
| `_content` | string | Full-text search on content | `_content=metformin` |
| `_count` | number | Page size | `_count=50` |
| `_offset` | number | Starting index | `_offset=100` |
| `_sort` | string | Sort field (prefix `-` for descending) | `_sort=-date` |
| `_total` | string | Include total count (`none`, `estimate`, `accurate`) | `_total=accurate` |
| `_elements` | string | Partial resource return | `_elements=name,birthDate` |
| `_summary` | string | Summary mode (`true`, `text`, `data`, `count`) | `_summary=count` |

### Resource-Specific Search Parameters

#### Patient
| Parameter | Type | Example |
|-----------|------|---------|
| `name` | string | `name=Smith` |
| `family` | string | `family=Smith` |
| `given` | string | `given=Jane` |
| `birthdate` | date | `birthdate=1990-05-15` |
| `gender` | token | `gender=female` |
| `identifier` | token | `identifier=http://mrn|12345` |
| `address` | string | `address=Springfield` |
| `phone` | token | `phone=555-1234` |
| `email` | token | `email=jane@example.com` |
| `general-practitioner` | reference | `general-practitioner=Practitioner/doc-1` |

#### Observation
| Parameter | Type | Example |
|-----------|------|---------|
| `code` | token | `code=http://loinc.org|8867-4` |
| `patient` / `subject` | reference | `patient=Patient/123` |
| `date` | date | `date=ge2024-01-01&date=le2024-12-31` |
| `status` | token | `status=final` |
| `category` | token | `category=vital-signs` |
| `value-quantity` | quantity | `value-quantity=gt120|http://unitsofmeasure.org|mm[Hg]` |
| `combo-code` | token | Component code (blood pressure) |
| `combo-value-quantity` | quantity | Component value |

### Search Prefixes (Date and Quantity)

| Prefix | Meaning | Example |
|--------|---------|---------|
| `eq` | Equal (default) | `date=eq2024-01-01` |
| `ne` | Not equal | `date=ne2024-01-01` |
| `gt` | Greater than | `date=gt2024-01-01` |
| `lt` | Less than | `date=lt2024-12-31` |
| `ge` | Greater or equal | `date=ge2024-01-01` |
| `le` | Less or equal | `date=le2024-12-31` |
| `sa` | Starts after | `date=sa2024-01-01` |
| `eb` | Ends before | `date=eb2024-12-31` |
| `ap` | Approximately (+/- 10%) | `value-quantity=ap100|http://unitsofmeasure.org|mg/dL` |

### Search Modifiers

| Modifier | Applies To | Meaning | Example |
|----------|-----------|---------|---------|
| `:exact` | string | Case-sensitive exact match | `name:exact=Smith` |
| `:contains` | string | Substring match | `name:contains=mit` |
| `:not` | token | Negation | `status:not=cancelled` |
| `:text` | token | Search on display text | `code:text=heart rate` |
| `:above` | token | Code or any parent in hierarchy | `code:above=http://snomed.info/sct|73211009` |
| `:below` | token | Code or any child in hierarchy | `code:below=http://snomed.info/sct|73211009` |
| `:missing` | any | Field presence check | `birthdate:missing=true` |
| `:identifier` | reference | Search by target identifier | `subject:identifier=http://mrn|123` |
| `:of-type` | token | Identifier type filtering | `identifier:of-type=http://terminology.hl7.org/CodeSystem/v2-0203|MR|12345` |

### Chained Search

Search by properties of a referenced resource:

```
# Find observations for patients named "Smith"
GET /Observation?patient.name=Smith

# Find observations for patients born after 1990
GET /Observation?patient.birthdate=gt1990-01-01

# Double chain: observations for patients at a specific organization
GET /Observation?patient.organization.name=General%20Hospital
```

### Reverse Chaining (_has)

Search by properties of resources that reference the target:

```
# Find patients who have an Observation with code 8867-4
GET /Patient?_has:Observation:patient:code=http://loinc.org|8867-4

# Find patients with a Condition of diabetes
GET /Patient?_has:Condition:subject:code=http://snomed.info/sct|73211009
```

### Include and Revinclude

Eager-load related resources in a single request:

```
# Include referenced Patients in Observation results
GET /Observation?code=8867-4&_include=Observation:patient

# Include all referenced resources
GET /MedicationRequest?patient=Patient/123&_include=MedicationRequest:*

# Revinclude: get Patient and all their Observations
GET /Patient?_id=123&_revinclude=Observation:patient

# Iterate: follow include chains
GET /MedicationRequest?patient=Patient/123&_include=MedicationRequest:medication&_include:iterate=Medication:manufacturer
```

**Performance warning**: `_include=*` and `_revinclude` can return massive result sets. Always combine with `_count` pagination.

---

## Bundles

### Bundle Types

| Type | Purpose | Processing |
|------|---------|-----------|
| `transaction` | All-or-nothing batch of operations | Atomic: all succeed or all fail, rolled back |
| `batch` | Independent operations in one request | Each entry processed independently, partial success allowed |
| `searchset` | Search results | Returned by server for search operations |
| `document` | Clinical document | Immutable, first entry must be Composition |
| `message` | FHIR messaging | First entry must be MessageHeader |
| `collection` | Arbitrary collection | No processing semantics |
| `history` | Version history | Returned by _history operations |

### Transaction Bundle Structure

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-1",
      "resource": {
        "resourceType": "Patient",
        "name": [{"family": "Smith", "given": ["Jane"]}],
        "gender": "female",
        "birthDate": "1990-05-15"
      },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:observation-1",
      "resource": {
        "resourceType": "Observation",
        "status": "final",
        "code": {
          "coding": [{"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}]
        },
        "subject": {
          "reference": "urn:uuid:patient-1"
        },
        "valueQuantity": {
          "value": 72,
          "unit": "beats/minute",
          "system": "http://unitsofmeasure.org",
          "code": "/min"
        }
      },
      "request": {
        "method": "POST",
        "url": "Observation"
      }
    }
  ]
}
```

### Bundle Processing Order

Regardless of the order entries appear in the Bundle JSON, the server MUST process them in this order:

```
1. DELETE operations
2. POST operations (creates)
3. PUT and PATCH operations (updates)
4. GET operations (reads)
```

This ordering ensures that:
- Deletions clear the way before creates
- Creates generate IDs that updates can reference
- Reads see the final state after all mutations

### Conditional References in Bundles

Within a transaction Bundle, entries can reference each other using:

**Temporary UUIDs** (preferred):
```json
{
  "fullUrl": "urn:uuid:61ebe359-bfdc-4613-8bf2-c5e300945f0a",
  "resource": { "resourceType": "Patient", "..." : "..." },
  "request": { "method": "POST", "url": "Patient" }
}
```
Other entries reference via `"reference": "urn:uuid:61ebe359-bfdc-4613-8bf2-c5e300945f0a"`. The server resolves these to real IDs after processing.

**Conditional references**:
```json
{
  "resource": {
    "resourceType": "Observation",
    "subject": {
      "reference": "Patient?identifier=http://mrn|12345"
    }
  },
  "request": { "method": "POST", "url": "Observation" }
}
```
The server resolves the conditional reference to the matching Patient. If zero or multiple matches, the transaction fails.

### Transaction Response

```json
{
  "resourceType": "Bundle",
  "type": "transaction-response",
  "entry": [
    {
      "response": {
        "status": "201 Created",
        "location": "Patient/abc-123/_history/1",
        "etag": "W/\"1\"",
        "lastModified": "2024-03-15T10:30:00Z"
      }
    },
    {
      "response": {
        "status": "201 Created",
        "location": "Observation/def-456/_history/1",
        "etag": "W/\"1\"",
        "lastModified": "2024-03-15T10:30:00Z"
      }
    }
  ]
}
```

### Pagination

Search results are paginated using Bundle links:

```json
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 342,
  "link": [
    {"relation": "self", "url": "https://server/fhir/Patient?name=Smith&_count=20&_offset=0"},
    {"relation": "next", "url": "https://server/fhir/Patient?name=Smith&_count=20&_offset=20"},
    {"relation": "last", "url": "https://server/fhir/Patient?name=Smith&_count=20&_offset=340"}
  ],
  "entry": [ "..." ]
}
```

**Pagination parameters**:
- `_count`: Number of results per page (server may impose a maximum)
- `_offset`: Starting index (0-based)
- Use `next` link for cursor-based pagination (preferred over manual offset calculation)
- `total` may be omitted or estimated depending on `_total` parameter

---

## SMART-on-FHIR Authorization

### Overview

SMART-on-FHIR is an OAuth 2.0-based authorization framework for healthcare apps. It defines how apps request access to FHIR data with granular scopes.

### SMART v2 Scopes

Format: `{context}/{ResourceType}.{permissions}`

**Context**:
- `patient/` — Access limited to a single patient (patient-facing apps)
- `user/` — Access limited by the user's permissions (clinician-facing apps)
- `system/` — Backend service access (no user context)

**Permissions** (CRUDS):
- `c` — Create
- `r` — Read
- `u` — Update
- `d` — Delete
- `s` — Search

**Examples**:
```
patient/Patient.rs          Read and search the in-context patient
patient/Observation.rs      Read and search the patient's observations
user/Patient.cruds          Full CRUD+search on patients the user can access
user/Encounter.rs           Read and search encounters for the user's patients
system/Patient.rs           Backend service: read and search all patients
system/*.rs                 Backend service: read and search all resource types
```

**Wildcard scopes**:
```
patient/*.rs                Read and search all resource types for the patient
user/*.cruds                Full access for the user across all types
system/*.*                  Full backend service access (use sparingly)
```

**Additional scopes**:
```
openid                      OpenID Connect identity
fhirUser                    Get the FHIR resource URL of the authenticated user
launch                      Receive launch context from EHR
launch/patient              Request patient context in standalone launch
offline_access              Request refresh token for long-lived access
```

### EHR Launch Flow

The EHR initiates the app launch (embedded in EHR UI):

```
Step 1: EHR launches app with launch parameter
  GET https://app.example.com/launch?
    iss=https://ehr.example.com/fhir
    &launch=abc123xyz

Step 2: App discovers authorization endpoints
  GET https://ehr.example.com/fhir/.well-known/smart-configuration
  Response:
  {
    "authorization_endpoint": "https://ehr.example.com/auth/authorize",
    "token_endpoint": "https://ehr.example.com/auth/token",
    "capabilities": ["launch-ehr", "client-public", "client-confidential-symmetric",
                      "context-ehr-patient", "sso-openid-connect", "permission-v2"]
  }

Step 3: App redirects to authorization endpoint
  GET https://ehr.example.com/auth/authorize?
    response_type=code
    &client_id=my-app-id
    &redirect_uri=https://app.example.com/callback
    &scope=launch patient/Patient.rs patient/Observation.rs openid fhirUser
    &state=random-state-value
    &launch=abc123xyz
    &aud=https://ehr.example.com/fhir

Step 4: EHR authenticates user, gets consent, redirects back
  GET https://app.example.com/callback?
    code=auth-code-xyz
    &state=random-state-value

Step 5: App exchanges code for token
  POST https://ehr.example.com/auth/token
  Content-Type: application/x-www-form-urlencoded

  grant_type=authorization_code
  &code=auth-code-xyz
  &redirect_uri=https://app.example.com/callback
  &client_id=my-app-id
  &client_secret=my-secret          (confidential clients only)

Step 6: Token response includes FHIR context
  {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "scope": "launch patient/Patient.rs patient/Observation.rs openid fhirUser",
    "patient": "Patient/abc-123",
    "encounter": "Encounter/enc-456",
    "id_token": "eyJ...",
    "refresh_token": "refresh-xyz"
  }
```

### Standalone Launch Flow

The app launches independently (not from within an EHR):

```
Step 1: App discovers endpoints from well-known configuration
  GET https://ehr.example.com/fhir/.well-known/smart-configuration

Step 2: App redirects to authorization endpoint (no launch parameter)
  GET https://ehr.example.com/auth/authorize?
    response_type=code
    &client_id=my-app-id
    &redirect_uri=https://app.example.com/callback
    &scope=launch/patient patient/Patient.rs patient/Observation.rs openid fhirUser
    &state=random-state-value
    &aud=https://ehr.example.com/fhir

Step 3-6: Same as EHR launch
  (User selects patient during auth if launch/patient scope requested)
```

### Backend Services (System-to-System)

For server-to-server communication with no user interaction:

```
Step 1: Register public key with authorization server (one-time setup)
  Provide JWKS URL or upload public key

Step 2: Create signed JWT assertion
  {
    "iss": "my-backend-client-id",
    "sub": "my-backend-client-id",
    "aud": "https://ehr.example.com/auth/token",
    "exp": 1710500000,
    "jti": "unique-jwt-id-123"
  }
  Sign with RS384 or ES384 private key

Step 3: Exchange JWT for access token
  POST https://ehr.example.com/auth/token
  Content-Type: application/x-www-form-urlencoded

  grant_type=client_credentials
  &scope=system/Patient.rs system/Observation.rs
  &client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer
  &client_assertion=eyJ...signed-jwt...

Step 4: Use access token
  GET https://ehr.example.com/fhir/Patient?_count=100
  Authorization: Bearer eyJ...access-token...
```

---

## Versioning and Concurrency

### ETag / If-Match Headers

FHIR uses ETags for optimistic concurrency control:

```
# Read resource, note the ETag
GET /fhir/Patient/abc-123
Response headers:
  ETag: W/"3"
  Last-Modified: 2024-03-15T10:30:00Z

# Update with If-Match to prevent lost updates
PUT /fhir/Patient/abc-123
If-Match: W/"3"
Content-Type: application/fhir+json

{ "resourceType": "Patient", "id": "abc-123", ... }

# If version matches: 200 OK with new ETag W/"4"
# If version does NOT match: 412 Precondition Failed
```

**When to use If-Match**:
- Always use for PUT operations in multi-user environments
- Critical for resources that multiple systems may update (Patient demographics, medication lists)
- Prevents the "last writer wins" problem

### Version-Specific References

```json
{
  "reference": "Patient/abc-123/_history/3",
  "display": "Jane Smith (as of version 3)"
}
```

Use version-specific references when the exact state of the referenced resource matters (e.g., medication at time of prescribing).

---

## Resource Validation

### Required Fields by Resource

| Resource | Required Fields | Cardinality Notes |
|----------|----------------|-------------------|
| **Patient** | None strictly required in base | US Core requires: identifier, name, gender |
| **Observation** | status, code | value[x] is conditional (required unless dataAbsentReason) |
| **Encounter** | status, class | US Core adds: type, subject |
| **Condition** | code (US Core), subject | clinicalStatus required if verificationStatus != entered-in-error |
| **MedicationRequest** | status, intent, medication[x], subject | dosageInstruction strongly recommended |
| **AllergyIntolerance** | clinicalStatus (if not unconfirmed) | code required by US Core |
| **Procedure** | status, code, subject | performedDateTime or performedPeriod recommended |
| **DiagnosticReport** | status, code | result references to Observations |

### Code System Bindings

| Binding Strength | Meaning | Validation Behavior |
|-----------------|---------|-------------------|
| **required** | MUST use a code from the specified ValueSet | Reject if code not in ValueSet |
| **extensible** | SHOULD use a code from the ValueSet; MAY use other if none fits | Accept other codes with warning |
| **preferred** | RECOMMENDED to use codes from the ValueSet | Accept any valid code |
| **example** | Provided as examples only | No validation constraint |

**Common required bindings**:
- `Observation.status` -> `http://hl7.org/fhir/ValueSet/observation-status` (registered, preliminary, final, amended, corrected, cancelled, entered-in-error, unknown)
- `Patient.gender` -> `http://hl7.org/fhir/ValueSet/administrative-gender` (male, female, other, unknown)
- `Encounter.status` -> `http://hl7.org/fhir/ValueSet/encounter-status`
- `Condition.clinicalStatus` -> `http://terminology.hl7.org/CodeSystem/condition-clinical`
- `Condition.verificationStatus` -> `http://terminology.hl7.org/CodeSystem/condition-ver-status`

---

## Terminology Services

### ValueSet Operations

```
# Expand a ValueSet to see all included codes
GET /fhir/ValueSet/$expand?url=http://hl7.org/fhir/ValueSet/observation-codes&count=20&filter=heart

# Validate a code against a ValueSet
GET /fhir/ValueSet/$validate-code?url=http://hl7.org/fhir/ValueSet/observation-codes
  &system=http://loinc.org&code=8867-4

# Lookup code details
GET /fhir/CodeSystem/$lookup?system=http://loinc.org&code=8867-4
```

### CodeSystem Operations

```
# Look up a code's properties and designations
GET /fhir/CodeSystem/$lookup?system=http://snomed.info/sct&code=73211009

# Subsumption testing (is code A a parent of code B?)
GET /fhir/CodeSystem/$subsumes?system=http://snomed.info/sct&codeA=73211009&codeB=44054006
```

### ConceptMap Translation

```
# Translate a code from one system to another
GET /fhir/ConceptMap/$translate?
  url=http://example.com/ConceptMap/icd10-to-snomed
  &system=http://hl7.org/fhir/sid/icd-10-cm
  &code=E11.9
```

### Common Code Systems

| System URI | Name | Use |
|-----------|------|-----|
| `http://loinc.org` | LOINC | Lab tests, clinical observations |
| `http://snomed.info/sct` | SNOMED CT | Clinical findings, procedures, body sites |
| `http://hl7.org/fhir/sid/icd-10-cm` | ICD-10-CM | Diagnosis codes (US) |
| `http://www.nlm.nih.gov/research/umls/rxnorm` | RxNorm | Medications (US) |
| `http://www.whocc.no/atc` | ATC | Anatomical Therapeutic Chemical classification |
| `http://hl7.org/fhir/sid/cvx` | CVX | Vaccine codes |
| `http://hl7.org/fhir/sid/ndc` | NDC | National Drug Codes |
| `http://unitsofmeasure.org` | UCUM | Units of measure |
| `http://terminology.hl7.org/CodeSystem/v3-ActCode` | HL7 v3 ActCode | Encounter class (AMB, IMP, EMER) |

---

## Conformance

### CapabilityStatement

Every FHIR server exposes its capabilities at `{base}/metadata`:

```
GET /fhir/metadata
Accept: application/fhir+json
```

Key sections to inspect:
```json
{
  "resourceType": "CapabilityStatement",
  "status": "active",
  "fhirVersion": "4.0.1",
  "format": ["json", "xml"],
  "rest": [
    {
      "mode": "server",
      "resource": [
        {
          "type": "Patient",
          "interaction": [
            {"code": "read"},
            {"code": "vread"},
            {"code": "search-type"},
            {"code": "create"},
            {"code": "update"},
            {"code": "patch"},
            {"code": "delete"}
          ],
          "searchParam": [
            {"name": "name", "type": "string"},
            {"name": "birthdate", "type": "date"},
            {"name": "identifier", "type": "token"}
          ],
          "searchInclude": ["Patient:general-practitioner"],
          "searchRevInclude": ["Observation:patient"],
          "versioning": "versioned",
          "conditionalCreate": true,
          "conditionalUpdate": true,
          "conditionalDelete": "single"
        }
      ],
      "security": {
        "service": [
          {
            "coding": [
              {"system": "http://terminology.hl7.org/CodeSystem/restful-security-service", "code": "SMART-on-FHIR"}
            ]
          }
        ],
        "extension": [
          {
            "url": "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris",
            "extension": [
              {"url": "authorize", "valueUri": "https://ehr.example.com/auth/authorize"},
              {"url": "token", "valueUri": "https://ehr.example.com/auth/token"}
            ]
          }
        ]
      }
    }
  ]
}
```

### StructureDefinition (Profiles)

Profiles constrain base resources for specific use cases:

```json
{
  "resourceType": "StructureDefinition",
  "url": "http://example.com/StructureDefinition/my-patient-profile",
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": {
    "element": [
      {
        "id": "Patient.identifier",
        "path": "Patient.identifier",
        "min": 1,
        "mustSupport": true
      },
      {
        "id": "Patient.name",
        "path": "Patient.name",
        "min": 1,
        "mustSupport": true
      },
      {
        "id": "Patient.gender",
        "path": "Patient.gender",
        "min": 1,
        "mustSupport": true
      }
    ]
  }
}
```

### US Core Profiles

US Core is the baseline FHIR implementation guide for the United States. Key profiles:

| Profile | Base Resource | Key Constraints |
|---------|--------------|----------------|
| US Core Patient | Patient | identifier, name, gender required; race/ethnicity extensions |
| US Core Observation (Lab) | Observation | category=laboratory, code from LOINC, value required |
| US Core Vital Signs | Observation | category=vital-signs, specific LOINC codes for BP, HR, etc. |
| US Core Condition | Condition | code from SNOMED/ICD-10, clinicalStatus required |
| US Core MedicationRequest | MedicationRequest | medication from RxNorm |
| US Core Encounter | Encounter | type, class, subject required |
| US Core AllergyIntolerance | AllergyIntolerance | code from SNOMED/RxNorm/NDF-RT |

---

## FastAPI / Pydantic Implementation Patterns

### Resource Models with Pydantic

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, datetime

class Coding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None

class CodeableConcept(BaseModel):
    coding: list[Coding] = []
    text: Optional[str] = None

class Reference(BaseModel):
    reference: Optional[str] = None
    display: Optional[str] = None

class HumanName(BaseModel):
    use: Optional[str] = None
    family: Optional[str] = None
    given: list[str] = []
    prefix: list[str] = []
    suffix: list[str] = []

class Identifier(BaseModel):
    use: Optional[str] = None
    system: Optional[str] = None
    value: Optional[str] = None

class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None

class Patient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: Optional[str] = None
    identifier: list[Identifier] = []
    name: list[HumanName] = []
    gender: Optional[str] = None
    birthDate: Optional[date] = None

class Observation(BaseModel):
    resourceType: Literal["Observation"] = "Observation"
    id: Optional[str] = None
    status: str
    code: CodeableConcept
    subject: Optional[Reference] = None
    effectiveDateTime: Optional[datetime] = None
    valueQuantity: Optional[Quantity] = None
    valueCodeableConcept: Optional[CodeableConcept] = None
    valueString: Optional[str] = None
```

### FastAPI FHIR Server Endpoints

```python
from fastapi import FastAPI, HTTPException, Header, Response, status
from typing import Optional
import uuid

app = FastAPI(title="FHIR R4 Server")

# In-memory store (replace with database)
patients: dict[str, dict] = {}

@app.get("/fhir/metadata")
async def capability_statement():
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [{
            "mode": "server",
            "resource": [{
                "type": "Patient",
                "interaction": [
                    {"code": "read"}, {"code": "create"},
                    {"code": "update"}, {"code": "search-type"}
                ]
            }]
        }]
    }

@app.post("/fhir/Patient", status_code=201)
async def create_patient(patient: Patient, response: Response):
    patient_id = str(uuid.uuid4())
    patient.id = patient_id
    patients[patient_id] = {
        "resource": patient.model_dump(exclude_none=True),
        "version": 1
    }
    response.headers["Location"] = f"/fhir/Patient/{patient_id}/_history/1"
    response.headers["ETag"] = 'W/"1"'
    return patient.model_dump(exclude_none=True)

@app.get("/fhir/Patient/{patient_id}")
async def read_patient(patient_id: str, response: Response):
    if patient_id not in patients:
        raise HTTPException(
            status_code=404,
            detail={
                "resourceType": "OperationOutcome",
                "issue": [{"severity": "error", "code": "not-found",
                           "diagnostics": f"Patient/{patient_id} not found"}]
            }
        )
    record = patients[patient_id]
    response.headers["ETag"] = f'W/"{record["version"]}"'
    return record["resource"]

@app.put("/fhir/Patient/{patient_id}")
async def update_patient(
    patient_id: str, patient: Patient, response: Response,
    if_match: Optional[str] = Header(None)
):
    if patient_id not in patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    record = patients[patient_id]
    if if_match:
        expected = f'W/"{record["version"]}"'
        if if_match != expected:
            raise HTTPException(status_code=412, detail="Version conflict")
    patient.id = patient_id
    new_version = record["version"] + 1
    patients[patient_id] = {
        "resource": patient.model_dump(exclude_none=True),
        "version": new_version
    }
    response.headers["ETag"] = f'W/"{new_version}"'
    return patient.model_dump(exclude_none=True)

@app.get("/fhir/Patient")
async def search_patients(
    name: Optional[str] = None,
    birthdate: Optional[str] = None,
    gender: Optional[str] = None,
    identifier: Optional[str] = None,
    _count: int = 20,
    _offset: int = 0
):
    results = list(patients.values())
    # Apply filters (simplified)
    if name:
        results = [r for r in results
                   if any(name.lower() in n.get("family", "").lower()
                          for n in r["resource"].get("name", []))]
    if gender:
        results = [r for r in results
                   if r["resource"].get("gender") == gender]
    total = len(results)
    page = results[_offset:_offset + _count]
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": total,
        "entry": [{"resource": r["resource"]} for r in page]
    }

@app.delete("/fhir/Patient/{patient_id}", status_code=204)
async def delete_patient(patient_id: str):
    if patient_id not in patients:
        raise HTTPException(status_code=404, detail="Patient not found")
    del patients[patient_id]
    return Response(status_code=204)
```

### Transaction Bundle Processing

```python
@app.post("/fhir")
async def process_bundle(bundle: dict):
    if bundle.get("type") not in ("transaction", "batch"):
        raise HTTPException(status_code=400, detail="Only transaction and batch Bundles supported")

    entries = bundle.get("entry", [])
    is_transaction = bundle["type"] == "transaction"

    # Sort by processing order: DELETE -> POST -> PUT/PATCH -> GET
    method_order = {"DELETE": 0, "POST": 1, "PUT": 2, "PATCH": 2, "GET": 3}
    sorted_entries = sorted(entries, key=lambda e: method_order.get(e["request"]["method"], 4))

    # Resolve urn:uuid references after processing
    uuid_map = {}  # urn:uuid -> actual reference
    response_entries = []

    for entry in sorted_entries:
        method = entry["request"]["method"]
        url = entry["request"]["url"]
        resource = entry.get("resource")
        full_url = entry.get("fullUrl", "")

        # Resolve temporary references in resource
        if resource:
            resource_json = json.dumps(resource)
            for temp_url, real_ref in uuid_map.items():
                resource_json = resource_json.replace(temp_url, real_ref)
            resource = json.loads(resource_json)

        # Process each entry based on method
        # ... (dispatch to create/read/update/delete handlers)
        # Track urn:uuid -> real ID mapping for transaction reference resolution

    return {
        "resourceType": "Bundle",
        "type": f"{bundle['type']}-response",
        "entry": response_entries
    }
```

---

## Common FHIR Servers

| Server | Type | Language | Key Features |
|--------|------|----------|-------------|
| **HAPI FHIR** | Open source | Java | Most widely used, full R4 support, JPA persistence, terminology services |
| **Microsoft FHIR Server** | Open source / Azure | C# | Azure-hosted option, SMART-on-FHIR, Cosmos DB backend |
| **Google Healthcare API** | Managed service | N/A | Cloud-native, BigQuery integration, DICOM+FHIR+HL7v2 |
| **IBM FHIR Server** | Open source | Java | Modular, multi-tenant, conformance-focused |
| **Firely Server** | Commercial | C# | .NET ecosystem, Simplifier integration, profiles |
| **Smile CDR** | Commercial | Java | Built on HAPI, enterprise features, MDM |
| **Aidbox** | Commercial | Clojure | PostgreSQL-native, SQL-on-FHIR, custom operations |

### HAPI FHIR Client Example (Java)

```java
FhirContext ctx = FhirContext.forR4();
IGenericClient client = ctx.newRestfulGenericClient("https://hapi.fhir.org/baseR4");

// Create a patient
Patient patient = new Patient();
patient.addIdentifier().setSystem("http://mrn").setValue("12345");
patient.addName().setFamily("Smith").addGiven("Jane");
patient.setGender(Enumerations.AdministrativeGender.FEMALE);
patient.setBirthDateElement(new DateType("1990-05-15"));

MethodOutcome outcome = client.create().resource(patient).execute();
String id = outcome.getId().getIdPart();

// Search
Bundle results = client.search().forResource(Patient.class)
    .where(Patient.NAME.matches().value("Smith"))
    .returnBundle(Bundle.class)
    .execute();
```

### Python FHIR Client (fhirclient)

```python
from fhirclient import client
from fhirclient.models.patient import Patient

settings = {
    "app_id": "my-app",
    "api_base": "https://r4.smarthealthit.org"
}
smart = client.FHIRClient(settings=settings)

# Search for patients
search = Patient.where(struct={"name": "Smith"})
patients = search.perform_resources(smart.server)

for p in patients:
    print(f"{p.name[0].family}, {p.name[0].given[0]} - {p.birthDate.isostring}")
```

---

## Worked Example: Lab Result Integration

A complete example of creating a patient, posting lab results, and querying them:

```
Step 1: Create Patient
  POST /fhir/Patient
  {
    "resourceType": "Patient",
    "identifier": [{"system": "http://hospital.example.com/mrn", "value": "MRN-12345"}],
    "name": [{"family": "Garcia", "given": ["Maria"]}],
    "gender": "female",
    "birthDate": "1985-07-22"
  }
  -> 201, Patient/p-001

Step 2: Post lab panel as Bundle transaction
  POST /fhir
  {
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "fullUrl": "urn:uuid:report-1",
        "resource": {
          "resourceType": "DiagnosticReport",
          "status": "final",
          "code": {"coding": [{"system": "http://loinc.org", "code": "24323-8", "display": "CMP panel"}]},
          "subject": {"reference": "Patient/p-001"},
          "result": [
            {"reference": "urn:uuid:obs-glucose"},
            {"reference": "urn:uuid:obs-sodium"}
          ]
        },
        "request": {"method": "POST", "url": "DiagnosticReport"}
      },
      {
        "fullUrl": "urn:uuid:obs-glucose",
        "resource": {
          "resourceType": "Observation",
          "status": "final",
          "code": {"coding": [{"system": "http://loinc.org", "code": "2345-7", "display": "Glucose"}]},
          "subject": {"reference": "Patient/p-001"},
          "valueQuantity": {"value": 95, "unit": "mg/dL", "system": "http://unitsofmeasure.org", "code": "mg/dL"},
          "referenceRange": [{"low": {"value": 70, "unit": "mg/dL"}, "high": {"value": 100, "unit": "mg/dL"}}]
        },
        "request": {"method": "POST", "url": "Observation"}
      },
      {
        "fullUrl": "urn:uuid:obs-sodium",
        "resource": {
          "resourceType": "Observation",
          "status": "final",
          "code": {"coding": [{"system": "http://loinc.org", "code": "2951-2", "display": "Sodium"}]},
          "subject": {"reference": "Patient/p-001"},
          "valueQuantity": {"value": 140, "unit": "mmol/L", "system": "http://unitsofmeasure.org", "code": "mmol/L"},
          "referenceRange": [{"low": {"value": 136, "unit": "mmol/L"}, "high": {"value": 145, "unit": "mmol/L"}}]
        },
        "request": {"method": "POST", "url": "Observation"}
      }
    ]
  }

Step 3: Query patient's lab results
  GET /fhir/Observation?patient=Patient/p-001&category=laboratory&_sort=-date&_count=50

Step 4: Get diagnostic report with included observations
  GET /fhir/DiagnosticReport?patient=Patient/p-001&_include=DiagnosticReport:result
```

---

## Common Pitfalls and Solutions

| Pitfall | Why It Happens | Solution |
|---------|---------------|----------|
| PUT deletes fields | PUT replaces entire resource | Always GET before PUT, or use PATCH |
| Missing `text` in CodeableConcept | Developer only provides Coding | Always include `text` for clinical safety |
| Wrong unit system | Using free-text units | Always use UCUM system and codes |
| Ignoring ETag | No concurrency control | Always use If-Match on PUT in production |
| Unbounded _include | `_include=*` returns huge result sets | Be specific about includes, use _count |
| Hardcoded server URLs | References break across environments | Use relative references within a server |
| Ignoring OperationOutcome | Error response body not checked | Always parse OperationOutcome from 4xx/5xx |
| Wrong date precision | Using `date` for timestamps | Use `dateTime` or `instant` for timestamps |
| Token search without system | `identifier=12345` matches any system | Always specify system: `identifier=http://mrn|12345` |
| Missing conditional create | Duplicate resources on retry | Use `If-None-Exist` header with POST |

---

## Completeness Checklist

- [ ] Resource types selected and mapped to clinical data requirements
- [ ] Data types correctly used (CodeableConcept vs Coding, Reference types, Quantity with UCUM)
- [ ] CRUD endpoints implemented with correct HTTP semantics and status codes
- [ ] Search parameters defined with appropriate types, modifiers, and chaining
- [ ] Bundle transactions handle processing order (DELETE->POST->PUT->GET) and reference resolution
- [ ] SMART-on-FHIR scopes defined with correct v2 format and launch flow implemented
- [ ] OperationOutcome returned for all error responses with appropriate severity and codes
- [ ] ETag/If-Match versioning implemented for update operations
- [ ] Terminology bindings validated against required ValueSets
- [ ] CapabilityStatement accurately reflects server capabilities
- [ ] Pagination implemented with _count, _offset, and next/previous links
- [ ] US Core profile constraints met (if US deployment)
