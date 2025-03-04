SCRAPE_OPTIONS = {
    "type": "object",
    "description": "The options for the scrape",
    "properties": {
        "include_tags": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "An array of HTML tags, classes, or IDs to include in the scraped content. Only elements matching these selectors will be returned.",
        },
        "exclude_tags": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "An array of HTML tags, classes, or IDs to exclude from the scraped content. Elements matching these selectors will be omitted from the response.",
        },
        "only_main_content": {
            "type": "boolean",
            "description": "Whether to only return the main content of the page. If true, only the main content of the page will be returned, excluding any headers, navigation menus,footers, or other non-main content.",
        },
    },
    "required": ["include_tags", "exclude_tags", "only_main_content"],
    "additionalProperties": False,
}

SCRAPE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "The URL of the website to scrape",
        },
        "scrape_options": SCRAPE_OPTIONS,
    },
    "required": ["url", "scrape_options"],
    "additionalProperties": False,
}

CRAWL_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "The URL of the website to crawl",
        },
        "max_pages": {
            "type": "number",
            "description": "The maximum number of pages to crawl",
        },
        "follow_links": {
            "type": "boolean",
            "description": "Whether to follow links on the page",
        },
        "ignore_sitemap": {
            "type": "boolean",
            "description": "Whether to ignore the sitemap",
        },
        "exclude_patterns": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "An array of regular expressions or wildcard patterns specifying which URLs should be excluded from the crawl. Any pages whose URLs' path match one of these patterns will be skipped. Example: ['/admin', '/careers/*']",
        },
        "include_patterns": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "An array of regular expressions or wildcard patterns specifying which URLs should be included in the crawl. Only pages whose URLs' path match one of these path patterns will be visited. Example: ['/admin', '/careers/*']",
        },
        "scrape_options": SCRAPE_OPTIONS,
    },
    "required": [
        "url",
        "max_pages",
        "follow_links",
        "ignore_sitemap",
        "exclude_patterns",
        "include_patterns",
        "scrape_options",
    ],
    "additionalProperties": False,
}
