#!/usr/bin/env python3
"""
Kakoo_Talk MCP Server

This MCP server provides kakoo_talk functionality.

Generated on: 2025-07-24 at 19:01:57
Generator: MCP Server Generator v2.0.0
Timestamp: 1753351317
"""

import json
from mcp.server.fastmcp import FastMCP

# FastMCP 서버 초기화
mcp = FastMCP("Kakoo_Talk Server")

# 생성 메타데이터
METADATA = {
    "service_name": "kakoo_talk",
    "generated_at": "2025-07-24T19:01:57.253414",
    "generated_date": "2025-07-24",
    "generated_time": "19:01:57",
    "timestamp": 1753351317,
    "generator_version": "2.0.0"
}


@mcp.tool()
async def kakoo_talk_get_recent_messages(chat_id: str, limit: int, time: str | None = None) -> str:
    """
    Retrieve the most recent messages from a specific chat.
    
    Args:
            chat_id: str, The unique identifier for the chat.
            limit: int, The maximum number of recent messages to retrieve.
    
    Returns:
            json
    """

    try:
        import random
        import datetime
        random.seed(31)

        senders = [
            "john_doe", "jane_smith", "alex_jones", "emily_clark", "michael_brown",
            "sarah_lee", "david_wilson", "linda_jones", "robert_miller", "patricia_davis",
            "hyunsoo_kim", "jiyoon_park", "minji_lee", "seojun_choi", "yuna_kang"
        ]
        messages = [
            "Hey, did you see the news today?",
            "I just finished reading that book you recommended.",
            "Let's meet up for coffee this weekend.",
            "Happy Birthday! Hope you have a great day!",
            "Can you send me the report by tomorrow?",
            "I found a great new restaurant we should try.",
            "Did you watch the game last night?",
            "I'm planning a trip to New York next month.",
            "Let's schedule a meeting for next week.",
            "I can't believe it's already September!",
            "오늘 점심 뭐 먹을까?",
            "퇴근하고 헬스장 갈래?",
            "카톡 확인 부탁해!",
            "주말에 드라이브 어때?",
            "회의 자료 업데이트 했어."
        ]

        base_time = datetime.datetime.fromisoformat(time) if time else datetime.datetime.now()
        data = []
        for _ in range(limit):
            offset = datetime.timedelta(days=random.randint(0, 7), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            message = {
                "sender": random.choice(senders),
                "message": random.choice(messages),
                "timestamp": (base_time - offset).isoformat()
            }
            data.append(message)

        result = {
                "data": data
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def kakoo_talk_search_contacts(query: str) -> str:
    """
    Search for contacts by name or other attributes.
    
    Args:
            query: str, The search term to find matching contacts.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        contacts = [
            {"name": "John Doe", "phone": "555-1234", "email": "john.doe@example.com"},
            {"name": "Jane Smith", "phone": "555-5678", "email": "jane.smith@example.com"},
            {"name": "Alex Jones", "phone": "555-8765", "email": "alex.jones@example.com"},
            {"name": "Emily Clark", "phone": "555-4321", "email": "emily.clark@example.com"},
            {"name": "Michael Brown", "phone": "555-6789", "email": "michael.brown@example.com"},
            {"name": "김현수", "phone": "010-1234-5678", "email": "hyunsoo.kim@example.com"},
            {"name": "박지윤", "phone": "010-5555-7777", "email": "jiyoon.park@example.com"}
        ]

        matching_contacts = [contact for contact in contacts if query.lower() in contact["name"].lower()]

        result = {
                "data": matching_contacts
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def kakoo_talk_get_chat_images(chat_id: str, limit: int) -> str:
    """
    Retrieve recent images shared in a specific chat.
    
    Args:
            chat_id: str, The unique identifier for the chat.
            limit: int, The maximum number of images to retrieve.
    
    Returns:
            json
    """

    try:
        import random
        import datetime
        random.seed(31)

        image_urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg",
            "https://example.com/image4.jpg",
            "https://example.com/image5.jpg",
            "https://example.com/image6.png",
            "https://example.com/image7.jpeg",
            "https://example.com/image8.jpg"
        ]

        data = []
        for _ in range(limit):
            image = {
                "url": random.choice(image_urls),
                "timestamp": datetime.datetime(2024, random.randint(1, 9), random.randint(1, 28), random.randint(0, 23), random.randint(0, 59)).isoformat()
            }
            data.append(image)

        result = {
                "data": data
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def kakoo_talk_get_unread_messages_count(chat_id: str) -> str:
    """
    Get the count of unread messages in a specific chat.
    
    Args:
            chat_id: str, The unique identifier for the chat.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        unread_count = random.randint(0, 50)

        result = {
                "data": {"unread_count": unread_count}
        }
    except Exception as e:
        result = {
                "data": {"unread_count": 0}
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def kakoo_talk_get_chat_files(chat_id: str, limit: int) -> str:
    """
    Retrieve recent files shared in a specific chat.
    
    Args:
            chat_id: str, The unique identifier for the chat.
            limit: int, The maximum number of files to retrieve.
    
    Returns:
            json
    """

    try:
        import random
        import datetime
        random.seed(31)

        file_names = [
            "report.pdf",
            "presentation.pptx",
            "notes.txt",
            "budget.xlsx",
            "design.psd",
            "wireframe.fig",
            "summary.docx",
            "invoice_2025-08.pdf"
        ]

        data = []
        for _ in range(limit):
            file = {
                "name": random.choice(file_names),
                "timestamp": datetime.datetime(2024, random.randint(1, 9), random.randint(1, 28), random.randint(0, 23), random.randint(0, 59)).isoformat()
            }
            data.append(file)

        result = {
                "data": data
        }
    except Exception as e:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def kakoo_talk_get_chat_participants(chat_id: str) -> str:
    """
    Retrieve the list of participants in a specific chat.
    
    Args:
            chat_id: str, The unique identifier for the chat.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        participants = [
            {"name": "John Doe", "status": "online"},
            {"name": "Jane Smith", "status": "offline"},
            {"name": "Alex Jones", "status": "online"},
            {"name": "Emily Clark", "status": "offline"},
            {"name": "Michael Brown", "status": "online"}
        ]

        result = {
                "data": participants
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
