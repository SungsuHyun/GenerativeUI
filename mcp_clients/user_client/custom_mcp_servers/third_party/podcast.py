#!/usr/bin/env python3
"""
Podcast MCP Server

This MCP server provides podcast functionality.

Generated on: 2025-09-08 at 00:00:00
Generator: MCP Server Generator v2.0.0
Timestamp: 1757289600
"""

import json
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP("Podcast Server")

# 생성 메타데이터
METADATA = {
    "service_name": "podcast",
    "generated_at": "2025-09-08T00:00:00",
    "generated_date": "2025-09-08",
    "generated_time": "00:00:00",
    "timestamp": 1757289600,
    "generator_version": "2.0.0"
}


@mcp.tool()
async def podcast_get_recent_episodes(show_name: str, max_results: int, time: str | None = None) -> str:
    """
    Retrieve the most recent podcast episodes for a given show.
    
    Args:
            show_name: str, The name of the podcast show.
            max_results: int, The maximum number of recent episodes to retrieve.
    
    Returns:
            json
    """

    try:
        import random
        import datetime
        random.seed(31)

        episode_titles = [
            "Deep Dive into AI Ethics",
            "Startup Stories: Zero to One",
            "Health Hacks for Busy People",
            "Design Thinking in Practice",
            "Productivity Myths Debunked",
            "The Future of Work: Remote and Hybrid",
            "Financial Freedom 101",
            "Mindfulness for Everyday Life",
            "Cybersecurity Basics for Everyone",
            "The Art of Storytelling",
            "Data Engineering Weekly Recap",
            "Mobile Dev News Roundup",
            "Design Systems at Scale",
            "K-pop Industry Deep Dive",
            "Korean Startup Ecosystem Overview"
        ]

        base_time = datetime.datetime.fromisoformat(time) if time else datetime.datetime.now()

        episodes = []
        for _ in range(max_results):
            episode = {
                "show": show_name,
                "title": random.choice(episode_titles),
                "timestamp": (base_time - datetime.timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat(),
                "dataType": "text"
            }
            episodes.append(episode)

        result = {
                "data": episodes
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)


@mcp.tool()
async def podcast_search_shows_by_keyword(keyword: str, limit: int) -> str:
    """
    Search for podcast shows by a specific keyword.
    
    Args:
            keyword: str, The keyword to search for.
            limit: int, The maximum number of shows to return.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        shows = [
            {"name": "Tech Trends Today", "category": "Technology"},
            {"name": "Healthy Living Hub", "category": "Health"},
            {"name": "Financial Freedom Fridays", "category": "Finance"},
            {"name": "Design & Life", "category": "Design"},
            {"name": "The Productivity Podcast", "category": "Productivity"},
            {"name": "Korea Tech Weekly", "category": "Technology"},
            {"name": "Deep Learning Diner", "category": "Technology"},
            {"name": "Coffee Chat: Developers", "category": "Technology"},
            {"name": "Mindful Minutes", "category": "Health"}
        ]

        filtered = [show for show in shows if keyword.lower() in show["name"].lower()]
        result = {
                "data": filtered[:max(0, limit)]
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)


@mcp.tool()
async def podcast_get_show_recommendations() -> str:
    """
    Get recommended podcast shows based on listening patterns.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        recommendations = [
            {"name": "AI Explained", "description": "Weekly breakdowns of AI news."},
            {"name": "Founders' Diaries", "description": "Candid stories from startup founders."},
            {"name": "Wellness Weekly", "description": "Science-backed health insights."},
            {"name": "Design Matters", "description": "Conversations with leading designers."},
            {"name": "Money Matters", "description": "Personal finance tips and tricks."},
            {"name": "K-Startup Stories", "description": "Interviews with Korean founders."},
            {"name": "Build in Public", "description": "Makers share progress and lessons."}
        ]

        result = {
                "data": random.sample(recommendations, 3)
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)


@mcp.tool()
async def podcast_get_episode_details(episode_id: str) -> str:
    """
    Retrieve detailed information for a specific podcast episode.
    
    Args:
            episode_id: str, The ID of the episode.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        details = {
            "episode_id": episode_id,
            "title": "The Future of Remote Work",
            "duration": f"{random.randint(20, 65)}:00",
            "host": "Jane Doe",
            "guests": ["John Smith", "Alex Kim"],
            "summary": "Discussion on trends shaping remote and hybrid work.",
            "dataType": "text"
        }

        result = {
                "data": details
        }
    except Exception as e:
        result = {
                "data": {}
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)


@mcp.tool()
async def podcast_get_followed_shows(limit: int) -> str:
    """
    Retrieve a list of shows that the user follows.
    
    Args:
            limit: int, The maximum number of shows to return.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        followed = [
            {"name": "Tech Trends Today", "category": "Technology", "dataType": "contact"},
            {"name": "Wellness Weekly", "category": "Health", "dataType": "contact"},
            {"name": "Design Matters", "category": "Design", "dataType": "contact"},
            {"name": "Money Matters", "category": "Finance", "dataType": "contact"},
            {"name": "The Productivity Podcast", "category": "Productivity", "dataType": "contact"}
        ]

        result = {
                "data": random.sample(followed, min(limit, len(followed)))
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)



if __name__ == "__main__":
    # FastMCP 서버 실행 (stdio transport 사용)
    mcp.run(transport="stdio")


