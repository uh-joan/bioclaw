"""
Deep dive narrative analysis for SEC filings.

Extracts and searches narrative sections (Business, Risks, MD&A) from
SEC 10-K and 10-Q HTML filings for specific concepts/keywords and links
findings to business segment financial data.
"""

import time
import urllib.request
import re
from typing import Dict, List
from bs4 import BeautifulSoup
from collections import defaultdict

# SEC EDGAR rate limit: ~6 requests/sec to stay within fair-use policy
SEC_RATE_LIMIT_DELAY = 0.17

# Maximum characters to keep from a single filing section (prevents huge text blocks)
MAX_SECTION_CHARS = 100_000

# Maximum characters to search backwards/forwards when finding sentence boundaries
SENTENCE_BOUNDARY_SEARCH_WINDOW = 1000


def download_filing_html(cik: str, accession_number: str, primary_document: str) -> str:
    """
    Download HTML version of 10-K/10-Q filing from SEC.gov

    Args:
        cik: Company CIK (10 digits with leading zeros)
        accession_number: SEC accession number (e.g., "0001193125-24-012345")
        primary_document: Primary document filename (e.g., "mdt-20251024.htm")

    Returns:
        str: Raw HTML content of the filing

    Raises:
        Exception: If download fails or returns non-200 status
    """
    # Apply same rate limiting as XML downloads (~6 req/sec)
    time.sleep(SEC_RATE_LIMIT_DELAY)

    # Remove dashes from accession number for URL path
    acc_no_dashes = accession_number.replace('-', '')

    # Construct direct filing document URL
    # Format: https://www.sec.gov/Archives/edgar/data/{cik}/{accession-nodashes}/{primary-doc}
    cik_num = int(cik)  # Remove leading zeros
    url = f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{acc_no_dashes}/{primary_document}"

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Company Analysis Tool contact@example.com')

        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status} when downloading {url}")

            # Read and decode HTML content
            content = response.read()

            # Try UTF-8 first, fallback to latin-1 if needed
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                return content.decode('latin-1')

    except Exception as e:
        raise Exception(f"Failed to download filing HTML for {accession_number}: {str(e)}")


def extract_filing_sections(html_content: str) -> dict:
    """
    Extract narrative sections from HTML filing

    Extracts:
    - Item 1: Business Description
    - Item 1A: Risk Factors
    - Item 7: MD&A (10-K) or Item 2: MD&A (10-Q)

    Args:
        html_content: Raw HTML content from SEC filing

    Returns:
        dict: {'business': str, 'risks': str, 'mda': str}
              Empty strings if section not found
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get all text content
    full_text = soup.get_text()

    # Clean up excessive whitespace
    full_text = re.sub(r'\s+', ' ', full_text)

    # Define section patterns (case-insensitive)
    # SEC filings use standardized item headers
    patterns = {
        'business': [
            r'Item\s+1\.\s+Business',
            r'ITEM\s+1\.\s+BUSINESS',
            r'>Item 1\.<.*?>Business',
        ],
        'risks': [
            r'Item\s+1A\.\s+Risk\s+Factors',
            r'ITEM\s+1A\.\s+RISK\s+FACTORS',
            r'>Item 1A\.<.*?>Risk Factors',
        ],
        'mda': [
            r'Item\s+[27]\.\s+Management.?s\s+Discussion\s+and\s+Analysis',
            r'ITEM\s+[27]\.\s+MANAGEMENT.?S\s+DISCUSSION\s+AND\s+ANALYSIS',
            r'>Item [27]\.<.*?>Management',
        ]
    }

    # Next section markers (to find end of current section)
    next_section_patterns = [
        r'Item\s+\d+[A-Z]?\.',
        r'ITEM\s+\d+[A-Z]?\.',
    ]

    sections = {}

    for section_name, section_patterns in patterns.items():
        section_text = ""

        # Try each pattern to find section start
        for pattern in section_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                start_pos = match.end()

                # Find next section header to determine end
                end_pos = len(full_text)
                for next_pattern in next_section_patterns:
                    next_match = re.search(next_pattern, full_text[start_pos:], re.IGNORECASE)
                    if next_match and next_match.start() > 100:  # Ensure we get meaningful content
                        end_pos = start_pos + next_match.start()
                        break

                section_text = full_text[start_pos:end_pos].strip()

                # Limit section length to prevent huge text blocks
                if len(section_text) > MAX_SECTION_CHARS:
                    section_text = section_text[:MAX_SECTION_CHARS] + "... [truncated]"

                break  # Found section, stop trying patterns

        sections[section_name] = section_text

    return sections


def search_concept_in_text(text: str, concept: str, context_window: int = 500) -> list:
    """
    Search for concept mentions in text with surrounding context

    Args:
        text: Section text to search
        concept: Keyword/phrase to find (case-insensitive)
        context_window: Characters before/after match to include (default: 500)

    Returns:
        list of dicts:
        [
            {
                'match': str,           # Matched text
                'context': str,         # Surrounding context
                'position': int,        # Character position
                'sentence': str         # Full sentence containing match
            }
        ]
    """
    if not text or not concept:
        return []

    mentions = []

    # Create case-insensitive regex pattern
    # Escape special regex characters in concept
    concept_escaped = re.escape(concept)
    pattern = re.compile(concept_escaped, re.IGNORECASE)

    # Find all matches
    for match in pattern.finditer(text):
        match_start = match.start()
        match_end = match.end()
        match_text = match.group()

        # Extract context window
        context_start = max(0, match_start - context_window)
        context_end = min(len(text), match_end + context_window)
        context_text = text[context_start:context_end].strip()

        # Add ellipsis if truncated
        if context_start > 0:
            context_text = "..." + context_text
        if context_end < len(text):
            context_text = context_text + "..."

        # Extract full sentence (find sentence boundaries)
        # Look for sentence-ending punctuation: . ! ?
        sentence_start = match_start
        sentence_end = match_end

        # Find sentence start (look backwards for . ! ? or start of text)
        for i in range(match_start - 1, max(0, match_start - SENTENCE_BOUNDARY_SEARCH_WINDOW), -1):
            if text[i] in '.!?' and i < match_start - 1:
                sentence_start = i + 1
                break

        # Find sentence end (look forwards for . ! ?)
        for i in range(match_end, min(len(text), match_end + SENTENCE_BOUNDARY_SEARCH_WINDOW)):
            if text[i] in '.!?':
                sentence_end = i + 1
                break

        sentence_text = text[sentence_start:sentence_end].strip()

        mentions.append({
            'match': match_text,
            'context': context_text,
            'position': match_start,
            'sentence': sentence_text
        })

    return mentions


def link_mentions_to_segments(mentions: list, segment_names: list) -> dict:
    """
    Map text mentions to segment names from financial data

    Args:
        mentions: List of concept mentions with context
        segment_names: List of segment names from XBRL data

    Returns:
        dict mapping segments to relevant mentions:
        {
            'Cardiac Rhythm And Heart Failure': [mention1, mention2],
            'Unknown': [mention3]  # Mentions not linked to specific segment
        }
    """
    if not mentions:
        return {}

    segment_links = defaultdict(list)

    # Create keyword variants for each segment
    segment_keywords = {}
    for segment in segment_names:
        # Split segment name into keywords
        # E.g., "Cardiac Rhythm And Heart Failure" -> ["cardiac", "rhythm", "heart", "failure"]
        keywords = [word.lower() for word in re.findall(r'\b\w+\b', segment)
                   if word.lower() not in ['and', 'or', 'the', 'of', 'in']]
        segment_keywords[segment] = keywords

    # Link each mention to segments
    for mention in mentions:
        # Search in context and sentence for segment keywords
        search_text = (mention['context'] + ' ' + mention['sentence']).lower()

        matched_segment = None
        max_keyword_matches = 0

        # Find segment with most keyword matches
        for segment, keywords in segment_keywords.items():
            # Count how many keywords from this segment appear in the mention context
            matches = sum(1 for kw in keywords if kw in search_text)

            if matches > max_keyword_matches:
                max_keyword_matches = matches
                matched_segment = segment

        # Require at least 2 keyword matches for confident linking
        # (or 1 match if segment name is very specific)
        if max_keyword_matches >= 2 or (max_keyword_matches == 1 and len(segment_keywords.get(matched_segment, [])) <= 2):
            segment_links[matched_segment].append(mention)
        else:
            segment_links['Unknown'].append(mention)

    return dict(segment_links)


def perform_deep_dive(cik: str, quarters: list, concepts: list, segment_names: list) -> dict:
    """
    Main deep dive orchestration - search SEC filings for multiple concept mentions

    For each quarter:
    1. Download HTML filing once (with rate limiting)
    2. Extract narrative sections once
    3. Search ALL concepts in each section (efficient batch search)
    4. Link mentions to segments for each concept

    Args:
        cik: Company CIK
        quarters: List of tuples (accession_number, period_end, form_type, primary_document)
        concepts: List of keywords/phrases to search for
        segment_names: List of segment names from XBRL data

    Returns:
        dict: {
            'concepts': [str],  # List of concepts searched
            'results': {
                'concept1': {
                    'total_mentions': int,
                    'by_quarter': {...},
                    'trends': {...}
                },
                'concept2': {...}
            }
        }
    """
    print(f"\n{'='*80}")
    print(f"DEEP DIVE: Searching for {len(concepts)} concept(s) in SEC filings")
    print(f"Concepts: {', '.join(concepts)}")
    print(f"{'='*80}")

    # Initialize tracking for each concept
    results = {}
    for concept in concepts:
        results[concept] = {
            'by_quarter': {},
            'all_segment_links': defaultdict(list),
            'total_mentions': 0,
            'mention_counts': []
        }

    # Process each quarter ONCE, searching all concepts
    for i, (accession, period_end, form, primary_doc) in enumerate(quarters, 1):
        print(f"\n[{i}/{len(quarters)}] Processing {form} for {period_end}...")

        try:
            # Step 1: Download HTML ONCE
            print(f"  - Downloading filing HTML...")
            html_content = download_filing_html(cik, accession, primary_doc)

            # Step 2: Extract sections ONCE
            print(f"  - Extracting narrative sections...")
            sections = extract_filing_sections(html_content)

            # Step 3: Search ALL concepts in the extracted text
            print(f"  - Searching for {len(concepts)} concepts...")

            # Determine quarter label (e.g., "2024-Q3")
            year = period_end[:4]
            month = period_end[5:7]
            quarter_num = (int(month) - 1) // 3 + 1
            quarter_label = f"{year}-Q{quarter_num}"

            # Search each concept
            for concept in concepts:
                sections_with_mentions = {}
                quarter_total = 0

                for section_name, section_text in sections.items():
                    if section_text:
                        mentions = search_concept_in_text(section_text, concept)
                        sections_with_mentions[section_name] = mentions
                        quarter_total += len(mentions)
                    else:
                        sections_with_mentions[section_name] = []

                # Step 4: Link to segments
                all_mentions_this_quarter = []
                for mentions in sections_with_mentions.values():
                    all_mentions_this_quarter.extend(mentions)

                segment_links = link_mentions_to_segments(all_mentions_this_quarter, segment_names)

                # Track for trends
                for segment, mentions in segment_links.items():
                    results[concept]['all_segment_links'][segment].extend(mentions)

                results[concept]['total_mentions'] += quarter_total
                results[concept]['mention_counts'].append(quarter_total)

                results[concept]['by_quarter'][quarter_label] = {
                    'period_end': period_end,
                    'form': form,
                    'total_mentions': quarter_total,
                    'sections': sections_with_mentions,
                    'segment_links': segment_links
                }

                if quarter_total > 0:
                    print(f"    • '{concept}': {quarter_total} mentions")

        except Exception as e:
            print(f"  ✗ Error processing {period_end}: {str(e)}")
            # Continue with other quarters
            # Add empty data for this quarter for all concepts
            for concept in concepts:
                results[concept]['mention_counts'].append(0)

    # Analyze trends for each concept
    for concept in concepts:
        mention_counts = results[concept]['mention_counts']
        all_segment_links = results[concept]['all_segment_links']

        # Trend analysis
        increasing = False
        if len(mention_counts) >= 2:
            mid = len(mention_counts) // 2
            first_half_avg = sum(mention_counts[:mid]) / mid if mid > 0 else 0
            second_half_avg = sum(mention_counts[mid:]) / (len(mention_counts) - mid)
            increasing = second_half_avg > first_half_avg

        # Find key segments (top 3 by mention count)
        segment_counts = [(seg, len(mentions)) for seg, mentions in all_segment_links.items() if seg != 'Unknown']
        segment_counts.sort(key=lambda x: x[1], reverse=True)
        key_segments = [seg for seg, _ in segment_counts[:3]]

        # Build final result for this concept
        results[concept] = {
            'concept': concept,
            'total_mentions': results[concept]['total_mentions'],
            'by_quarter': results[concept]['by_quarter'],
            'trends': {
                'increasing_mentions': increasing,
                'key_segments': key_segments,
                'mention_counts_by_quarter': mention_counts
            }
        }

    return {
        'concepts': concepts,
        'results': results
    }


def format_deep_dive_summary(deep_dive_data: dict) -> str:
    """
    Format deep dive results as readable summary

    Handles both single concept (legacy) and multi-concept results

    Args:
        deep_dive_data: Deep dive results from perform_deep_dive()
                       New format: {'concepts': [...], 'results': {...}}
                       Legacy format: {'concept': str, 'total_mentions': int, ...}

    Returns:
        str: Formatted summary text
    """
    lines = []

    # Check if this is multi-concept result
    if 'results' in deep_dive_data:
        # Multi-concept format
        concepts = deep_dive_data['concepts']
        results = deep_dive_data['results']

        lines.append("\n" + "="*80)
        lines.append(f"DEEP DIVE SUMMARY: {len(concepts)} Concept(s)")
        lines.append("="*80)

        # Show summary for each concept
        for concept in concepts:
            concept_data = results[concept]

            lines.append(f"\n{'-'*80}")
            lines.append(f"CONCEPT: {concept}")
            lines.append(f"{'-'*80}")

            lines.append(f"\nTotal mentions: {concept_data['total_mentions']} across {len(concept_data['by_quarter'])} quarters")

            # Trends
            trends = concept_data['trends']
            lines.append("\nTrends:")
            if trends['increasing_mentions']:
                lines.append("  • Mentions increasing over time")
            else:
                lines.append("  • Mentions stable or decreasing")

            if trends['key_segments']:
                lines.append("\nKey Segments:")
                for segment in trends['key_segments']:
                    lines.append(f"  • {segment}")

            # Recent quarter highlights (show most recent quarter with mentions)
            by_quarter = concept_data['by_quarter']
            if by_quarter:
                # Sort quarters by period_end (descending)
                sorted_quarters = sorted(by_quarter.items(),
                                        key=lambda x: x[1]['period_end'],
                                        reverse=True)

                # Find most recent quarter with mentions
                for quarter_label, quarter_data in sorted_quarters:
                    if quarter_data['total_mentions'] > 0:
                        lines.append(f"\nRecent Highlights ({quarter_label}):")

                        # Show up to 2 mentions from each section
                        for section_name in ['mda', 'business', 'risks']:
                            mentions = quarter_data['sections'].get(section_name, [])
                            if mentions:
                                lines.append(f"\n  {section_name.upper()}:")
                                for mention in mentions[:2]:
                                    # Truncate long sentences
                                    sentence = mention['sentence']
                                    if len(sentence) > 200:
                                        sentence = sentence[:200] + "..."
                                    lines.append(f"    - {sentence}")

                        break  # Only show most recent quarter

    else:
        # Legacy single-concept format (backwards compatibility)
        lines.append("\n" + "="*80)
        lines.append(f"DEEP DIVE SUMMARY: {deep_dive_data['concept']}")
        lines.append("="*80)

        lines.append(f"\nTotal mentions: {deep_dive_data['total_mentions']} across {len(deep_dive_data['by_quarter'])} quarters")

        # Trends
        trends = deep_dive_data['trends']
        lines.append("\nTrends:")
        if trends['increasing_mentions']:
            lines.append("  • Mentions increasing over time")
        else:
            lines.append("  • Mentions stable or decreasing")

        if trends['key_segments']:
            lines.append("\nKey Segments:")
            for segment in trends['key_segments']:
                lines.append(f"  • {segment}")

        # Recent quarter highlights (show most recent quarter with mentions)
        by_quarter = deep_dive_data['by_quarter']
        if by_quarter:
            # Sort quarters by period_end (descending)
            sorted_quarters = sorted(by_quarter.items(),
                                    key=lambda x: x[1]['period_end'],
                                    reverse=True)

            # Find most recent quarter with mentions
            for quarter_label, quarter_data in sorted_quarters:
                if quarter_data['total_mentions'] > 0:
                    lines.append(f"\nRecent Highlights ({quarter_label}):")

                    # Show up to 2 mentions from each section
                    for section_name in ['mda', 'business', 'risks']:
                        mentions = quarter_data['sections'].get(section_name, [])
                        if mentions:
                            lines.append(f"\n  {section_name.upper()}:")
                            for mention in mentions[:2]:
                                # Truncate long sentences
                                sentence = mention['sentence']
                                if len(sentence) > 200:
                                    sentence = sentence[:200] + "..."
                                lines.append(f"    - {sentence}")

                    break  # Only show most recent quarter

    return "\n".join(lines)
