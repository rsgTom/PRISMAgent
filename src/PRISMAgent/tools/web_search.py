"""
PRISMAgent.tools.web_search
--------------------------

This module provides a tool for performing web searches to retrieve information.
"""

from __future__ import annotations

import json
import aiohttp
from typing import Dict, Any, List, Optional, Union

from .factory import tool_factory
from PRISMAgent.config import SEARCH_API_KEY
from PRISMAgent.util import get_logger, with_log_context

# Get a logger for this module
logger = get_logger(__name__)

@tool_factory
@with_log_context(component="web_search_tool")
async def web_search(
    query: str,
    *,
    num_results: int = 5,
    search_type: str = "web",
    filter_domains: Optional[List[str]] = None,
    include_domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Perform a web search and return formatted results.
    
    This tool leverages a search API to perform web searches and 
    gather information from the internet.
    
    Args:
        query: The search query to use
        num_results: Number of results to return (default: 5)
        search_type: Type of search - "web", "news", "images" (default: "web")
        filter_domains: List of domains to exclude from results
        include_domains: List of domains to exclusively include in results
        
    Returns:
        Dictionary containing the search results
    """
    logger.info(
        f"Performing web search: {query}",
        query=query,
        num_results=num_results,
        search_type=search_type
    )
    
    # For demonstration purposes (without actual API integration), 
    # we'll return a simulated response
    # In a production environment, this would make an actual API call
    
    # Simulate the search API call
    simulated_results = await _simulate_search_api(
        query=query,
        num_results=num_results,
        search_type=search_type,
        filter_domains=filter_domains,
        include_domains=include_domains
    )
    
    # Format the results
    formatted_results = {
        "query": query,
        "num_results": len(simulated_results),
        "results": simulated_results
    }
    
    logger.debug(
        f"Web search complete, found {len(simulated_results)} results",
        query=query,
        result_count=len(simulated_results)
    )
    
    return formatted_results

async def _simulate_search_api(
    query: str,
    num_results: int = 5,
    search_type: str = "web",
    filter_domains: Optional[List[str]] = None,
    include_domains: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Simulate a search API call for demonstration purposes.
    
    In a production environment, this would be replaced with an actual API call
    to a search service like Google Custom Search, Bing API, or similar.
    
    Args:
        query: The search query
        num_results: Number of results to return
        search_type: Type of search
        filter_domains: Domains to exclude
        include_domains: Domains to include exclusively
        
    Returns:
        List of search result dictionaries
    """
    # For now, return simulated data
    # In real use, you would integrate with an actual search API here
    
    results = [
        {
            "title": f"Example search result for '{query}' - {i+1}",
            "url": f"https://example.com/result-{i+1}",
            "snippet": f"This is a simulated search result snippet for the query '{query}'. "
                      f"It demonstrates what search results would look like when properly "
                      f"implemented with a real search API. Result #{i+1}.",
            "source": "example.com"
        }
        for i in range(min(num_results, 10))  # Cap at 10 for the simulation
    ]
    
    return results

@tool_factory
@with_log_context(component="fetch_url_tool")
async def fetch_url(
    url: str,
    *,
    include_headers: bool = False,
    timeout: int = 10,
) -> Dict[str, Any]:
    """
    Fetch content from a specific URL.
    
    This tool retrieves content from a given URL, which can be useful
    for accessing specific web pages, documentation, or resources.
    
    Args:
        url: The URL to fetch
        include_headers: Whether to include HTTP headers in the response
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing the fetched content and metadata
    """
    logger.info(
        f"Fetching URL: {url}",
        url=url,
        include_headers=include_headers,
        timeout=timeout
    )
    
    result = {
        "success": False,
        "url": url,
        "content": None,
        "status_code": None,
        "headers": None,
        "error": None
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                result["status_code"] = response.status
                result["success"] = 200 <= response.status < 300
                
                if include_headers:
                    result["headers"] = dict(response.headers)
                
                # Get content based on content type
                content_type = response.headers.get("Content-Type", "")
                
                if "application/json" in content_type:
                    result["content"] = await response.json()
                else:
                    result["content"] = await response.text()
                
                logger.debug(
                    f"Successfully fetched URL: {url}",
                    url=url,
                    status_code=response.status,
                    content_length=len(str(result["content"]))
                )
    
    except aiohttp.ClientError as e:
        result["error"] = f"Request error: {str(e)}"
        logger.warning(
            f"Error fetching URL {url}: {str(e)}",
            url=url,
            error=str(e),
            error_type=type(e).__name__
        )
    
    except json.JSONDecodeError as e:
        result["error"] = f"JSON parsing error: {str(e)}"
        logger.warning(
            f"Error parsing JSON from URL {url}: {str(e)}",
            url=url,
            error=str(e),
            error_type="JSONDecodeError"
        )
    
    except Exception as e:
        result["error"] = f"Unexpected error: {str(e)}"
        logger.error(
            f"Unexpected error fetching URL {url}: {str(e)}",
            url=url,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
    
    return result
