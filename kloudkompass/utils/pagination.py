# kloudkompass/utils/pagination.py
# ------------------------------
# all pagination logic handling in one place. Cloud APIs often return
# large result sets in pages with next-page tokens. This module handles
# the looping, token tracking, and result merging so cloud modules stay clean.

import json
from typing import List, Dict, Any, Optional, Callable

from kloudkompass.core.exceptions import PaginationError
from kloudkompass.utils.subprocess_helpers import run_cli_command


# Maximum pages to fetch before assuming something is wrong
MAX_PAGES = 100


def paginate_cli_command(
    build_command: Callable[[Optional[str]], List[str]],
    result_key: str,
    token_key: str = "NextPageToken",
    next_token_arg: str = "--next-token",
    max_pages: int = MAX_PAGES,
) -> List[Dict[str, Any]]:
    """
    Execute a CLI command with pagination and collect all results.
    
    Loops until there are no more pages, tracking tokens to detect
    infinite loops. The build_command function lets callers construct
    their specific command with the current token.
    
    Args:
        build_command: Function that takes a token (or None) and returns command list
        result_key: JSON key containing the list of results (e.g. "ResultsByTime")
        token_key: JSON key containing the next page token
        next_token_arg: CLI argument name for the token
        max_pages: Safety limit to prevent runaway loops
        
    Returns:
        Combined list of all results from all pages
        
    Raises:
        PaginationError: If duplicate token detected or max pages exceeded
    """
    all_results = []
    seen_tokens = set()
    current_token = None
    page_count = 0
    
    while True:
        page_count += 1
        
        # Safety check: too many pages
        if page_count > max_pages:
            raise PaginationError(
                f"Exceeded maximum page count ({max_pages}). "
                "Query may be returning too much data."
            )
        
        # Build and run the command
        command = build_command(current_token)
        result = run_cli_command(command, check=True)
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise PaginationError(f"Failed to parse page {page_count} JSON: {e}")
        
        # Extract results from this page
        page_results = data.get(result_key, [])
        all_results.extend(page_results)
        
        # Check for next page
        next_token = data.get(token_key)
        
        if not next_token:
            # No more pages, we are done
            break
        
        # Safety check: duplicate token means infinite loop
        if next_token in seen_tokens:
            raise PaginationError(
                f"Duplicate pagination token detected on page {page_count}. "
                "This may indicate an API issue.",
                token=next_token
            )
        
        seen_tokens.add(next_token)
        current_token = next_token
    
    return all_results


def paginate_aws_cost_explorer(
    base_command: List[str],
    max_pages: int = MAX_PAGES,
) -> Dict[str, Any]:
    """
    Paginate AWS Cost Explorer get-cost-and-usage specifically.
    
    CE uses 'NextPageToken' in response and '--next-token' as argument.
    Merges ResultsByTime from all pages and return the combined response.
    """
    all_results_by_time = []
    seen_tokens = set()
    current_token = None
    page_count = 0
    
    # Tracks the first page's metadata to include in final response
    response_metadata = {}
    
    while True:
        page_count += 1
        
        if page_count > max_pages:
            raise PaginationError(
                f"AWS Cost Explorer exceeded {max_pages} pages."
            )
        
        # Build command with token if we have one
        command = base_command.copy()
        if current_token:
            command.extend(["--next-token", current_token])
        
        result = run_cli_command(command, check=True)
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise PaginationError(f"Failed to parse AWS CE page {page_count}: {e}")
        
        # Store metadata from first page
        if page_count == 1:
            response_metadata = {
                k: v for k, v in data.items()
                if k not in ("ResultsByTime", "NextPageToken")
            }
        
        # Collect results
        all_results_by_time.extend(data.get("ResultsByTime", []))
        
        # Check for more pages
        next_token = data.get("NextPageToken")
        
        if not next_token:
            break
        
        if next_token in seen_tokens:
            raise PaginationError(
                f"Duplicate token in AWS CE on page {page_count}",
                token=next_token
            )
        
        seen_tokens.add(next_token)
        current_token = next_token
    
    # Return combined response in same shape as single-page response
    return {
        **response_metadata,
        "ResultsByTime": all_results_by_time,
    }
