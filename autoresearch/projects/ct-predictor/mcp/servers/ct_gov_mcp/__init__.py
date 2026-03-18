"""ClinicalTrials.gov MCP Server - Python API

Provides Python functions for clinical trials database queries.
Data stays in execution environment - only summaries flow to model.

CRITICAL CT.GOV API QUIRKS:
1. Returns MARKDOWN text (not JSON) - parse with regex/string methods
2. Phase format: "PHASE2", "PHASE3" (NOT "Phase 2", "Phase 3") - validated in testing
3. Status values: Use uppercase - "RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING" - validated in testing
4. pageSize: Default 10, max 1000 (different from FDA's 100)
5. Response structure: Plain text with trial summaries, needs parsing
6. NCT ID format: NCT followed by 8 digits (e.g., "NCT04000165")
7. TOKEN USAGE (measured): search() ~140 tokens/study, get_study() ~3,900 tokens/study
8. Pagination: Uses pageToken (not offset) - token provided in each response
"""

from mcp.client import get_client
from typing import Dict, Any, Optional, Union


def search(
    condition: Optional[str] = None,
    intervention: Optional[str] = None,
    phase: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    lead: Optional[str] = None,
    pageSize: int = 100,
    pageToken: Optional[str] = None,
    countTotal: bool = True,
    sort: Optional[str] = None,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    Search ClinicalTrials.gov database

    Args:
        condition: Medical condition (e.g., "obesity", "Diabetes Mellitus Type 2")

        intervention: Treatment/intervention (e.g., "semaglutide", "insulin")

        phase: Trial phase - MUST use uppercase format
               Valid values: "PHASE1", "PHASE2", "PHASE3", "PHASE4", "EARLY_PHASE1", "NA"
               ❌ WRONG: "Phase 2", "Phase 3", "phase 2"
               ✅ CORRECT: "PHASE2", "PHASE3"

        status: Recruitment status - MUST use uppercase underscore format
                Common values:
                - "RECRUITING" - Currently enrolling participants
                - "NOT_YET_RECRUITING" - Not yet open for enrollment
                - "ACTIVE_NOT_RECRUITING" - Ongoing but not enrolling
                - "COMPLETED" - Study has concluded
                - "TERMINATED" - Stopped early
                - "SUSPENDED" - Temporarily halted
                - "WITHDRAWN" - Withdrawn before enrollment
                - "UNKNOWN" - Status not reported

        location: Geographic location (e.g., "United States", "California", "New York")

        lead: Lead sponsor/organization (e.g., "Novo Nordisk", "Pfizer", "Mayo Clinic")

        pageSize: Results per page (1-1000, default: 100)
                 Note: Max is 1000 (different from FDA's 100)

        pageToken: Pagination token from previous response (for fetching next page)

        countTotal: Whether to include total count (default: True)

        sort: Sort order (e.g., "StudyFirstPostDate", "LastUpdatePostDate")

    Returns:
        str or dict: MARKDOWN TEXT by default (not JSON!)
                    Returns string with formatted trial summaries that need parsing

        Response format (markdown text):
        ```
        # Clinical Trials Search Results
        **Results:** 5 of 65 studies found

        ### 1. NCT05930184
        **Title:** Study Title Here
        **Status:** Recruiting
        **Phase:** PHASE3
        ...
        ```

        Use regex or string parsing to extract:
        - Total count: r'(\\d+) of (\\d+) studies found'
        - NCT IDs: r'NCT\\d{8}'
        - Titles, statuses, phases from markdown structure

    Examples:
        # Example 1: Basic search with parsing
        result = search(
            condition="obesity",
            phase="PHASE3",
            status="RECRUITING",
            pageSize=50
        )

        # Parse markdown response (it's a string!)
        import re
        text = result if isinstance(result, str) else result.get('text', '')

        # Extract total trials
        match = re.search(r'(\\d+) of (\\d+) studies found', text)
        total_trials = int(match.group(2)) if match else 0

        # Extract NCT IDs
        nct_ids = re.findall(r'NCT\\d{8}', text)

        print(f"Found {total_trials} total trials")
        print(f"Retrieved {len(nct_ids)} trial IDs")

        # Example 2: Competitive analysis
        result = search(
            intervention="semaglutide",
            phase="PHASE3",
            status="RECRUITING",
            pageSize=100
        )

        # Count mentions of sponsors (parse markdown)
        text = result if isinstance(result, str) else result.get('text', '')
        sponsor_counts = {}
        for line in text.split('\n'):
            if 'Sponsor:' in line:
                sponsor = line.split('Sponsor:')[1].strip()
                sponsor_counts[sponsor] = sponsor_counts.get(sponsor, 0) + 1

        # Example 3: CORRECT phase/status format
        ✅ result = search(phase="PHASE2", status="RECRUITING")

        # Example 4: WRONG phase/status format
        ❌ result = search(phase="Phase 2", status="recruiting")  # Won't work!

        # Example 5: Pagination
        page1 = search(condition="diabetes", pageSize=100)
        # Get nextPageToken from response (if available)
        # page2 = search(condition="diabetes", pageSize=100, pageToken=token)
    """
    client = get_client('ctgov')

    params = {
        'method': 'search',
        'pageSize': pageSize,
        'countTotal': countTotal
    }

    if condition:
        params['condition'] = condition
    if intervention:
        params['intervention'] = intervention
    if phase:
        params['phase'] = phase
    if status:
        params['status'] = status
    if location:
        params['location'] = location
    if lead:
        params['lead'] = lead
    if pageToken:
        params['pageToken'] = pageToken
    if sort:
        params['sort'] = sort

    params.update(kwargs)

    # DEBUG: Log exact parameters being sent to API
    import json
    print(f"🔍 CT.gov API Request:")
    print(f"   Parameters: {json.dumps(params, indent=2)}")

    try:
        result = client.call_tool('ct_gov_studies', params)
        print(f"✅ CT.gov API Success (response length: {len(str(result))} chars)")
        return result
    except Exception as e:
        print(f"❌ CT.gov API Error: {e}")
        print(f"   Failed parameters: {json.dumps(params, indent=2)}")
        raise


def get_study(
    nctId: str,
    format: str = "json",
    markupFormat: str = "markdown"
) -> Dict[str, Any]:
    """
    Get detailed information for a specific clinical trial

    Args:
        nctId: NCT identifier (e.g., "NCT04000165", "NCT05930184")
               Format: NCT followed by 8 digits

        format: Response format - "json", "csv", "fhir.json"
                Default: "json"

        markupFormat: Format for text fields - "markdown" or "legacy"
                     Default: "markdown"

    Returns:
        dict: Detailed study information with full protocol data

        Key fields in response:
        - protocolSection.identificationModule.nctId
        - protocolSection.identificationModule.briefTitle
        - protocolSection.statusModule.overallStatus
        - protocolSection.designModule.phases
        - protocolSection.designModule.enrollmentInfo.count
        - protocolSection.sponsorCollaboratorsModule.leadSponsor.name
        - protocolSection.descriptionModule.briefSummary
        - protocolSection.eligibilityModule.eligibilityCriteria

    Examples:
        # Get detailed study information
        study = get_study(nctId="NCT04000165")

        # Extract key fields
        protocol = study.get('protocolSection', {})
        title = protocol.get('identificationModule', {}).get('briefTitle')
        status = protocol.get('statusModule', {}).get('overallStatus')
        sponsor = protocol.get('sponsorCollaboratorsModule', {}).get('leadSponsor', {}).get('name')

        print(f"Title: {title}")
        print(f"Status: {status}")
        print(f"Sponsor: {sponsor}")

        # Get enrollment count
        design = protocol.get('designModule', {})
        enrollment = design.get('enrollmentInfo', {}).get('count', 0)
        print(f"Enrollment: {enrollment} participants")
    """
    client = get_client('ctgov')

    params = {
        'method': 'get',
        'nctId': nctId,
        'format': format,
        'markupFormat': markupFormat
    }

    return client.call_tool('ct_gov_studies', params)


def suggest(
    dictionary: str,
    input: str
) -> Dict[str, Any]:
    """
    Get term suggestions for search parameters

    Args:
        dictionary: The field to get suggestions for
                   Values: "Condition", "InterventionName", "LeadSponsorName", "LocationFacility"

        input: Text to search for suggestions (minimum 2 characters)

    Returns:
        dict: Suggested terms matching the input

    Examples:
        # Get condition suggestions
        suggestions = suggest(dictionary="Condition", input="diabet")
        # Returns: ["Diabetes Mellitus", "Diabetes Mellitus Type 2", ...]

        # Get intervention suggestions
        suggestions = suggest(dictionary="InterventionName", input="semaglu")
        # Returns: ["Semaglutide", ...]

        # Get sponsor suggestions
        suggestions = suggest(dictionary="LeadSponsorName", input="novo")
        # Returns: ["Novo Nordisk", ...]

        # Get location suggestions
        suggestions = suggest(dictionary="LocationFacility", input="mayo")
        # Returns: ["Mayo Clinic", ...]
    """
    client = get_client('ctgov')

    params = {
        'method': 'suggest',
        'dictionary': dictionary,
        'input': input
    }

    return client.call_tool('ct_gov_studies', params)


__all__ = ['search', 'get_study', 'suggest']
