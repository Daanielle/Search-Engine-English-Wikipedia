# English Wikipedia Search Engine (Dockerized)

A lightweight search engine for **English Wikipedia articles**. This project runs an old Python search engine inside **Docker**.  

## Features

- Search articles by **query**, **body**, **title**, or **anchor text**  
- Supports **PageRank** and **page view** lookup  
- Works with pre-built **index/pickle files**, or returns empty results if missing  

## Quick Start

### Build and Run Docker

```bash
docker build -t wiki-search .
docker run -p 8080:8080 wiki-search
``` 

Access the API

Search:
http://localhost:8080/search?query=hello+world

Body search:
http://localhost:8080/search_body?query=hello+world

Title search:
http://localhost:8080/search_title?query=hello+world

PageRank: POST to http://localhost:8080/get_pagerank with JSON [1,5,8]

Page views: POST to http://localhost:8080/get_pageview with JSON [1,5,8]

Notes

If pickle/index files exist, full search works

Otherwise, endpoints return empty results