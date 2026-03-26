"""Literature synthesis for drug safety intelligence.

Searches PubMed for safety-related publications and bioRxiv for recent preprints.
Classifies publications by type (case report, meta-analysis, review, etc.).
"""

from typing import Dict, Any, List, Optional
import re
from datetime import datetime, timedelta


# Publication type classification keywords
PUB_TYPE_PATTERNS = {
    'case_report': ['case report', 'case series', 'case-report'],
    'meta_analysis': ['meta-analysis', 'meta analysis', 'systematic review and meta'],
    'systematic_review': ['systematic review', 'systematic literature review'],
    'rct': ['randomized', 'randomised', 'controlled trial', 'phase 3', 'phase 2'],
    'cohort_study': ['cohort', 'longitudinal', 'prospective study', 'retrospective study'],
    'review': ['review', 'narrative review', 'mini-review'],
    'pharmacovigilance': ['pharmacovigilance', 'post-marketing', 'faers', 'signal detection',
                          'disproportionality', 'adverse event report'],
}


def _classify_publication_type(title: str, abstract: str = '') -> str:
    """Classify publication type from title and abstract."""
    text = (title + ' ' + abstract).lower()

    # Check in priority order
    for pub_type, patterns in PUB_TYPE_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                return pub_type

    return 'other'


def _parse_pubmed_results(pubmed_response) -> List[Dict[str, Any]]:
    """Parse PubMed response into structured articles."""
    articles = []

    if isinstance(pubmed_response, str):
        # Parse markdown text
        article_sections = re.split(r'\n### \d+\.', pubmed_response)
        for section in article_sections[1:] if len(article_sections) > 1 else []:
            article = {}

            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', section)
            if title_match:
                article['title'] = title_match.group(1).strip()

            pmid_match = re.search(r'(?:PMID|PubMed ID)[:\s]*(\d+)', section)
            if pmid_match:
                article['pmid'] = pmid_match.group(1)

            authors_match = re.search(r'\*\*Authors?:\*\*\s*(.+?)(?:\n|$)', section)
            if authors_match:
                article['authors'] = authors_match.group(1).strip()

            journal_match = re.search(r'\*\*Journal:\*\*\s*(.+?)(?:\n|$)', section)
            if journal_match:
                article['journal'] = journal_match.group(1).strip()

            year_match = re.search(r'\*\*(?:Year|Date|Published?):\*\*\s*(\d{4})', section)
            if year_match:
                article['year'] = int(year_match.group(1))

            abstract_match = re.search(r'\*\*Abstract:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', section, re.DOTALL)
            if abstract_match:
                article['abstract'] = abstract_match.group(1).strip()[:500]

            if article.get('title'):
                article['pub_type'] = _classify_publication_type(
                    article.get('title', ''),
                    article.get('abstract', '')
                )
                articles.append(article)

    elif isinstance(pubmed_response, (dict, list)):
        # Handle both dict with 'results' key and direct list of articles
        if isinstance(pubmed_response, list):
            results = pubmed_response
        else:
            results = pubmed_response.get('results', pubmed_response.get('articles', []))
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    # Handle authors as list of dicts or string
                    authors = item.get('authors', '')
                    if isinstance(authors, list):
                        author_names = []
                        for a in authors[:5]:
                            if isinstance(a, dict):
                                author_names.append(a.get('name', str(a)))
                            else:
                                author_names.append(str(a))
                        authors = ', '.join(author_names)

                    # Handle publication_date field
                    year = item.get('year', '')
                    if not year:
                        pub_date = item.get('publication_date', item.get('pubdate', ''))
                        if isinstance(pub_date, str) and len(pub_date) >= 4:
                            year = pub_date[:4]

                    article = {
                        'title': item.get('title', ''),
                        'pmid': str(item.get('pmid', item.get('uid', ''))),
                        'authors': authors,
                        'journal': item.get('journal', item.get('source', '')),
                        'year': year,
                        'abstract': (item.get('abstract', '') or '')[:500],
                        'doi': item.get('doi', ''),
                        'url': item.get('url', ''),
                    }
                    article['pub_type'] = _classify_publication_type(
                        article['title'],
                        article.get('abstract', '')
                    )
                    articles.append(article)

    return articles


def _parse_biorxiv_results(biorxiv_response) -> List[Dict[str, Any]]:
    """Parse bioRxiv response into structured preprints."""
    preprints = []

    if isinstance(biorxiv_response, str):
        sections = re.split(r'\n### \d+\.', biorxiv_response)
        for section in sections[1:] if len(sections) > 1 else []:
            preprint = {}

            title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', section)
            if title_match:
                preprint['title'] = title_match.group(1).strip()

            doi_match = re.search(r'\*\*DOI:\*\*\s*(.+?)(?:\n|$)', section)
            if doi_match:
                preprint['doi'] = doi_match.group(1).strip()

            authors_match = re.search(r'\*\*Authors?:\*\*\s*(.+?)(?:\n|$)', section)
            if authors_match:
                preprint['authors'] = authors_match.group(1).strip()

            date_match = re.search(r'\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})', section)
            if date_match:
                preprint['date'] = date_match.group(1)

            category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\n|$)', section)
            if category_match:
                preprint['category'] = category_match.group(1).strip()

            abstract_match = re.search(r'\*\*Abstract:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', section, re.DOTALL)
            if abstract_match:
                preprint['abstract'] = abstract_match.group(1).strip()[:500]

            if preprint.get('title'):
                preprint['source'] = 'bioRxiv/medRxiv'
                preprint['is_preprint'] = True
                preprints.append(preprint)

    elif isinstance(biorxiv_response, dict):
        results = biorxiv_response.get('results', biorxiv_response.get('preprints', []))
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    preprints.append({
                        'title': item.get('title', ''),
                        'doi': item.get('doi', ''),
                        'authors': item.get('authors', ''),
                        'date': item.get('date', ''),
                        'category': item.get('category', ''),
                        'abstract': (item.get('abstract', '') or '')[:500],
                        'source': 'bioRxiv/medRxiv',
                        'is_preprint': True,
                    })

    return preprints


def synthesize_literature(
    pubmed_search_func,
    biorxiv_search_func=None,
    drug_names: List[str] = None,
    target_name: str = None,
    tracker=None,
) -> Dict[str, Any]:
    """
    Search and synthesize safety literature.

    Args:
        pubmed_search_func: PubMed search wrapper
        biorxiv_search_func: bioRxiv search function (optional)
        drug_names: List of drug names
        target_name: Target name
        tracker: ProgressTracker instance

    Returns:
        dict with articles, preprints, pub_type_breakdown, summary
    """
    if tracker:
        tracker.start_step('literature', "Searching safety literature...")

    articles = []
    preprints = []

    # Build PubMed search query
    drug_terms = []
    for drug in (drug_names or [])[:5]:
        drug_terms.append(f'"{drug}"')

    if target_name:
        drug_terms.append(f'"{target_name}"')

    if not drug_terms:
        if tracker:
            tracker.complete_step("No search terms for literature")
        return {
            'articles': [], 'preprints': [], 'pub_type_breakdown': {},
            'summary': {'total_articles': 0, 'total_preprints': 0},
        }

    drug_query = ' OR '.join(drug_terms)
    safety_query = f'({drug_query}) AND (safety OR "adverse event" OR toxicity OR "side effect" OR pharmacovigilance)'

    # PubMed search
    if tracker:
        tracker.update_step(0.2, "Searching PubMed for safety publications...")

    try:
        pubmed_result = pubmed_search_func(
            method='search_keywords',
            keywords=safety_query,
            num_results=20,
        )
        articles = _parse_pubmed_results(pubmed_result)
    except Exception as e:
        print(f"  Warning: PubMed search failed: {e}")

    if tracker:
        tracker.update_step(0.5, f"Found {len(articles)} PubMed articles. Searching bioRxiv...")

    # bioRxiv + medRxiv search (last 2 years)
    if biorxiv_search_func:
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')

        # Try multiple search strategies — bioRxiv client-side filtering is strict
        search_queries = []
        if drug_names:
            # Strategy 1: First drug name (most specific)
            search_queries.append(drug_names[0])
            # Strategy 2: Drug + safety
            search_queries.append(f"{drug_names[0]} safety")
        if target_name:
            # Strategy 3: Target name
            search_queries.append(target_name)

        for query in search_queries:
            if preprints:
                break  # Stop once we find results

            # Try both bioRxiv and medRxiv
            for server in ['medrxiv', 'biorxiv']:
                if preprints:
                    break
                try:
                    biorxiv_result = biorxiv_search_func(
                        query=query,
                        date_from=two_years_ago,
                        date_to=today,
                        server=server,
                        limit=10,
                    )
                    preprints = _parse_biorxiv_results(biorxiv_result)
                except Exception as e:
                    print(f"  Warning: {server} search failed for '{query}': {e}")

    if tracker:
        tracker.update_step(0.8, f"Found {len(preprints)} preprints. Classifying...")

    # Publication type breakdown
    pub_type_counts = {}
    for article in articles:
        pt = article.get('pub_type', 'other')
        pub_type_counts[pt] = pub_type_counts.get(pt, 0) + 1

    if tracker:
        tracker.complete_step(
            f"Literature: {len(articles)} PubMed articles, "
            f"{len(preprints)} preprints"
        )

    return {
        'articles': articles,
        'preprints': preprints,
        'pub_type_breakdown': pub_type_counts,
        'summary': {
            'total_articles': len(articles),
            'total_preprints': len(preprints),
            'case_reports': pub_type_counts.get('case_report', 0),
            'meta_analyses': pub_type_counts.get('meta_analysis', 0),
            'systematic_reviews': pub_type_counts.get('systematic_review', 0),
            'pharmacovigilance': pub_type_counts.get('pharmacovigilance', 0),
        },
    }
