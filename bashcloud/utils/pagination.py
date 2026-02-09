# bashcloud/utils/pagination.py
# ------------------------------
# I handle all pagination logic here in one place. Cloud APIs often return
# large result sets in pages with next-page tokens. This module handles
# the looping, token tracking, and result merging so cloud modules stay clean.

import json
from typing import List, Dict, Any, Optional, Callable, Union

from bashcloud.core.exceptions import PaginationError
from bashcloud.utils.subprocess_helpers import run_cli_command


# I set a safety limit to prevent runaway loops
MAX_PAGES = 100


def resolve_dotted_path(data: Any, path: str) -> List[Any]:
    """
    Resolve a dot-separated path into a nested data structure.
    
    I support numeric array indexes like "ResultsByTime.0.Groups" so callers
    can navigate complex JSON responses. Returns the value at the path
    or an empty list if not found.
    """
    if not path:
        return data if isinstance(data, list) else []
    
    parts = path.split(".")
    current = data
    
    for part in parts:
        if current is None:
            return []
        
        # I check if this part is a numeric index
        if part.isdigit():
            idx = int(part)
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                return []
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return []
    
    # I return the final value as a list
    if isinstance(current, list):
        return current
    elif current is not None:
        return [current]
    return []


def paginate_cli_command(
    build_command: Callable[[Optional[str]], List[str]],
    result_extractor: Union[str, Callable[[Dict[str, Any]], List[Any]]],
    page_token_key: str = "NextPageToken",
    next_token_arg: str = "--next-token",
    max_pages: int = MAX_PAGES,
) -> List[Any]:
    """
    Execute a CLI command with pagination and collect all results.
    
    I loop until there are no more pages, tracking tokens to detect
    infinite loops. The build_command function lets callers construct
    their specific command with the current token.
    
    Args:
        build_command: Function that takes a token (or None) and returns command list
        result_extractor: Either a callable that extracts items from JSON response,
                          or a dot-separated path string like "ResultsByTime.0.Groups"
        page_token_key: JSON key containing the next page token (provider-specific)
        next_token_arg: CLI argument name for the token
        max_pages: Safety limit to prevent runaway loops
        
    Returns:
        Combined list of all extracted items from all pages
        
    Raises:
        PaginationError: If duplicate token detected or max pages exceeded
    """
    all_results: List[Any] = []
    seen_tokens: set = set()
    current_token: Optional[str] = None
    page_count = 0
    
    # I determine the extraction method once
    if callable(result_extractor):
        extract_fn = result_extractor
    else:
        # I use the dotted path resolver
        extract_fn = lambda data: resolve_dotted_path(data, result_extractor)
    
    while True:
        page_count += 1
        
        # I check the page limit to prevent infinite loops
        if page_count > max_pages:
            raise PaginationError(
                f"Exceeded maximum page count ({max_pages}). "
                "Query may be returning too much data."
            )
        
        # I build and run the command
        command = build_command(current_token)
        result = run_cli_command(command, check=True)
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise PaginationError(f"Failed to parse page {page_count} JSON: {e}")
        
        # I extract results from this page using the extractor
        page_results = extract_fn(data)
        all_results.extend(page_results)
        
        # I check for next page token
        next_token = data.get(page_token_key)
        
        if not next_token:
            # No more pages, we are done
            break
        
        # I detect duplicate tokens which indicate infinite loops
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
    I merge ResultsByTime from all pages and return the combined response.
    """
    all_results_by_time: List[Dict[str, Any]] = []
    seen_tokens: set = set()
    current_token: Optional[str] = None
    page_count = 0
    
    # I track the first page metadata to include in final response
    response_metadata: Dict[str, Any] = {}
    
    while True:
        page_count += 1
        
        if page_count > max_pages:
            raise PaginationError(
                f"AWS Cost Explorer exceeded {max_pages} pages."
            )
        
        # I build command with token if we have one
        command = base_command.copy()
        if current_token:
            command.extend(["--next-token", current_token])
        
        result = run_cli_command(command, check=True)
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise PaginationError(f"Failed to parse AWS CE page {page_count}: {e}")
        
        # I store metadata from first page
        if page_count == 1:
            response_metadata = {
                k: v for k, v in data.items()
                if k not in ("ResultsByTime", "NextPageToken")
            }
        
        # I collect results
        all_results_by_time.extend(data.get("ResultsByTime", []))
        
        # I check for more pages
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
    
    # I return combined response in same shape as single-page response
    return {
        **response_metadata,
        "ResultsByTime": all_results_by_time,
    }
