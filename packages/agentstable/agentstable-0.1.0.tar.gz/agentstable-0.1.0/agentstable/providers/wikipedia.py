"""
Wikipedia integration for the agentstable SDK.

This module provides functionality for searching Wikipedia and retrieving article information.
"""

from typing import Dict, List, Optional, Union, Any, Generator, Callable
import importlib.util
import json


class WikipediaProvider:
    """
    Provider for Wikipedia search and article retrieval.
    """
    
    def __init__(self):
        """
        Initialize the Wikipedia provider and check if the wikipedia library is available.
        """
        self.wikipedia_available = importlib.util.find_spec("wikipedia") is not None
        self._wikipedia = None
        
        if self.wikipedia_available:
            try:
                import wikipedia
                self._wikipedia = wikipedia
            except ImportError:
                self.wikipedia_available = False
    
    @property
    def is_available(self) -> bool:
        """
        Check if the Wikipedia library is available.
        
        Returns:
            bool: True if the Wikipedia library is available, False otherwise.
        """
        return self.wikipedia_available and self._wikipedia is not None
    
    def search(self, query: str, language: str = "en", limit: int = 5) -> Dict[str, Any]:
        """
        Perform a Wikipedia search using the wikipedia library.
        
        Args:
            query: The search query
            language: Language code (e.g., en, fr, es)
            limit: Maximum number of results to return
            
        Returns:
            Dict containing search results or error message
        """
        if not self.is_available:
            return {"error": "Wikipedia library not installed. Install with: pip install wikipedia"}
        
        try:
            # Set language if provided
            if language:
                self._wikipedia.set_lang(language)
            
            # Search for articles
            search_results = self._wikipedia.search(query, results=limit)
            
            results = []
            for title in search_results:
                try:
                    # Get page summary
                    page = self._wikipedia.page(title, auto_suggest=False)
                    summary = page.summary
                    url = page.url
                    
                    results.append({
                        "title": title,
                        "summary": summary,
                        "url": url
                    })
                except Exception as e:
                    # Skip pages with errors
                    continue
            
            return {
                "query": query,
                "results": results
            }
        
        except Exception as e:
            return {"error": f"Error performing Wikipedia search: {e}"}
    
    def get_article(self, title: str, auto_suggest: bool = False) -> Dict[str, Any]:
        """
        Get a Wikipedia article by title.
        
        Args:
            title: The title of the article
            auto_suggest: Whether to use auto suggestion for finding the page
            
        Returns:
            Dict containing article information or error message
        """
        if not self.is_available:
            return {"error": "Wikipedia library not installed. Install with: pip install wikipedia"}
        
        try:
            page = self._wikipedia.page(title, auto_suggest=auto_suggest)
            
            return {
                "title": page.title,
                "summary": page.summary,
                "content": page.content,
                "url": page.url,
                "images": page.images,
                "links": page.links,
                "categories": page.categories,
                "references": page.references
            }
        
        except Exception as e:
            return {"error": f"Error retrieving Wikipedia article: {e}"}
    
    def stream_article_content(self, title: str, chunk_size: int = 1000, auto_suggest: bool = False) -> Generator[str, None, None]:
        """
        Stream a Wikipedia article's content in chunks.
        
        Args:
            title: The title of the article
            chunk_size: Size of each content chunk in characters
            auto_suggest: Whether to use auto suggestion for finding the page
            
        Yields:
            Chunks of the article content
        """
        if not self.is_available:
            yield json.dumps({"error": "Wikipedia library not installed. Install with: pip install wikipedia"})
            return
        
        try:
            page = self._wikipedia.page(title, auto_suggest=auto_suggest)
            content = page.content
            
            # Yield the metadata first
            metadata = {
                "title": page.title,
                "url": page.url,
                "total_size": len(content),
                "type": "metadata"
            }
            yield json.dumps(metadata)
            
            # Stream the content in chunks
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i+chunk_size]
                yield chunk
                
        except Exception as e:
            yield json.dumps({"error": f"Error streaming Wikipedia article: {e}"})
    
    def stream_article(self, title: str, auto_suggest: bool = False) -> Generator[Dict[str, Any], None, None]:
        """
        Stream a Wikipedia article with structured data.
        
        Args:
            title: The title of the article
            auto_suggest: Whether to use auto suggestion for finding the page
            
        Yields:
            Dictionary chunks of article data with type indicators
        """
        if not self.is_available:
            yield {"error": "Wikipedia library not installed. Install with: pip install wikipedia"}
            return
        
        try:
            page = self._wikipedia.page(title, auto_suggest=auto_suggest)
            
            # First yield metadata
            yield {
                "type": "metadata",
                "title": page.title,
                "url": page.url
            }
            
            # Then yield summary
            yield {
                "type": "summary",
                "content": page.summary
            }
            
            # Yield main content (split into paragraphs for streaming)
            paragraphs = page.content.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    yield {
                        "type": "content",
                        "part": i+1,
                        "total_parts": len(paragraphs),
                        "content": paragraph
                    }
            
            # Yield references
            yield {
                "type": "references",
                "references": page.references
            }
            
            # Finally yield categories and links
            yield {
                "type": "metadata",
                "categories": page.categories,
                "links": page.links,
                "images": page.images
            }
            
        except Exception as e:
            yield {"error": f"Error streaming Wikipedia article: {e}"}


# Create a singleton instance for easy access
wikipedia_provider = WikipediaProvider()


# Function aliases for simplified use
def search(query: str, language: str = "en", limit: int = 5) -> Dict[str, Any]:
    """
    Perform a Wikipedia search.
    
    Args:
        query: The search query
        language: Language code (e.g., en, fr, es)
        limit: Maximum number of results to return
        
    Returns:
        Dict containing search results or error message
    """
    return wikipedia_provider.search(query, language, limit)


def get_article(title: str, auto_suggest: bool = False) -> Dict[str, Any]:
    """
    Get a Wikipedia article by title.
    
    Args:
        title: The title of the article
        auto_suggest: Whether to use auto suggestion for finding the page
        
    Returns:
        Dict containing article information or error message
    """
    return wikipedia_provider.get_article(title, auto_suggest)


def stream_article_content(title: str, chunk_size: int = 1000, auto_suggest: bool = False) -> Generator[str, None, None]:
    """
    Stream a Wikipedia article's content in chunks.
    
    Args:
        title: The title of the article
        chunk_size: Size of each content chunk in characters
        auto_suggest: Whether to use auto suggestion for finding the page
        
    Yields:
        Chunks of the article content
    """
    return wikipedia_provider.stream_article_content(title, chunk_size, auto_suggest)


def stream_article(title: str, auto_suggest: bool = False) -> Generator[Dict[str, Any], None, None]:
    """
    Stream a Wikipedia article with structured data.
    
    Args:
        title: The title of the article
        auto_suggest: Whether to use auto suggestion for finding the page
        
    Yields:
        Dictionary chunks of article data with type indicators
    """
    return wikipedia_provider.stream_article(title, auto_suggest) 