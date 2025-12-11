#!/usr/bin/env python3
"""
Gmail MCP Server

This MCP server provides gmail functionality.

Generated on: 2025-07-24 at 19:01:57
Generator: MCP Server Generator v2.0.0
Timestamp: 1753351317
"""

from mcp.server.fastmcp import FastMCP


# FastMCP 서버 초기화
mcp = FastMCP("Gmail Server")

# 생성 메타데이터
METADATA = {
    "service_name": "gmail",
    "generated_at": "2025-07-24T19:01:57.253414",
    "generated_date": "2025-07-24",
    "generated_time": "19:01:57",
    "timestamp": 1753351317,
    "generator_version": "2.0.0"
}


@mcp.tool()
async def gmail_get_recent_emails(limit: int, time: str | None = None) -> str:
    """
    Retrieve a list of the most recent emails.
    
    Args:
            limit: int, The number of recent emails to retrieve.
    
    Returns:
            json
    """

    try:
        from datetime import datetime, timedelta
        import random
        random.seed(31)

        senders = [
            "john.doe@gmail.com", "jane.smith@gmail.com", "alex.jones@gmail.com", "emily.clark@gmail.com", "michael.brown@gmail.com",
            "sofia.hernandez@samsung.com", "li.wei@samsung.com", "yuki.tanaka@samsung.com", "kevin.ng@samsung.com", "lucas.martins@samsung.com"
        ]
        
        
        subjects = [
            "Meeting Reminder",
            "Project Update",
            "Invitation to Event",
            "Weekly Newsletter",
            "Your Order Confirmation",
            "Security Alert",
            "Action Required",
            "Re: Follow up",
            "Invoice Attached",
            "🔔 Notification"
        ]
        messages = [
            "Don't forget about the meeting tomorrow at 10 AM.",
            "Here's the latest update on the project. Please review.",
            "You're invited to our annual event. RSVP by next week.",
            "Check out this week's newsletter for the latest news.",
            "Thank you for your purchase! Your order will be shipped soon.",
            "Please verify your email address by clicking the link.",
            "Your subscription will expire soon.",
            "Attached is the invoice for last month.",
            "We detected a login from a new device.",
            "Reminder: Submit your timesheet by EOD."
        ]

        base_time = datetime.fromisoformat(time) if time else datetime.now()
        emails = []
        for _ in range(limit):
            offset = timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
            email = {
                "sender": random.choice(senders),
                "subject": random.choice(subjects),
                "message": random.choice(messages),
                "timestamp": (base_time - offset).isoformat()
            }
            emails.append(email)

        result = {
                "data": emails
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def gmail_search_emails_by_keyword(keyword: str) -> str:
    """
    Search for emails containing a specific keyword.
    
    Args:
            keyword: str, The keyword to search for in emails.
    
    Returns:
            json
    """

    try:
        from datetime import datetime, timedelta
        import random
        random.seed(31)

        senders = [
            "lisa.wong@example.com", "mark.taylor@example.com", "susan.lee@example.com", "david.kim@example.com", "nancy.white@example.com",
            "peter.chen@example.com", "anna.kovacs@example.com", "raj.patel@example.com", "natalie.porter@example.com", "mohamed.ali@example.com"
        ]
        subjects = [
            "Important Notice",
            "Your Subscription Renewal",
            "Family Gathering",
            "Job Opportunity",
            "Travel Itinerary",
            "Invitation: Webinar",
            "Password Reset",
            "Performance Review",
            "Welcome Aboard",
            "Outage Report"
        ]
        messages = [
            "Please read this important notice regarding your account.",
            "Your subscription is due for renewal. Please update your payment information.",
            "Join us for a family gathering this weekend.",
            "We have a job opportunity that matches your profile.",
            "Here is your travel itinerary for the upcoming trip.",
            "Confirm your email address to continue.",
            "Reminder: Your password will expire in 3 days.",
            "Your performance review is scheduled next week.",
            "Welcome aboard! Here are your next steps.",
            "We are investigating an outage affecting your region."
        ]

        emails = []
        for _ in range(random.randint(1, 5)):
            email = {
                "sender": random.choice(senders),
                "subject": random.choice(subjects),
                "message": random.choice(messages),
                "timestamp": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 638), hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat()
            }
            if keyword.lower() in email["subject"].lower() or keyword.lower() in email["message"].lower():
                emails.append(email)

        result = {
                "data": emails
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def gmail_find_contact_by_name(name: str) -> str:
    """
    Find a contact by name in the email contact list.
    
    Args:
            name: str, The name of the contact to find.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        contacts = [
            {"name": "John Doe", "email": "john.doe@example.com", "phone": "555-1234"},
            {"name": "Jane Smith", "email": "jane.smith@example.com", "phone": "555-5678"},
            {"name": "Alex Jones", "email": "alex.jones@example.com", "phone": "555-8765"},
            {"name": "Emily Clark", "email": "emily.clark@example.com", "phone": "555-4321"},
            {"name": "Michael Brown", "email": "michael.brown@example.com", "phone": "555-6789"}
        ]

        found_contacts = [contact for contact in contacts if name.lower() in contact["name"].lower()]

        result = {
                "data": found_contacts
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def gmail_get_unread_emails() -> str:
    """
    Retrieve a list of unread emails.
    
    Returns:
            json
    """

    try:
        from datetime import datetime, timedelta
        import random
        random.seed(31)

        senders = ["chris.evans@example.com", "sarah.connor@example.com", "bruce.wayne@example.com", "clark.kent@example.com", "diana.prince@example.com"]
        subjects = [
            "New Assignment",
            "Upcoming Webinar",
            "Security Alert",
            "Account Verification",
            "Special Offer"
        ]
        messages = [
            "You have a new assignment due next week.",
            "Join our upcoming webinar on the latest trends.",
            "We detected a security alert on your account.",
            "Please verify your account information.",
            "Don't miss out on this special offer just for you."
        ]

        emails = []
        for _ in range(random.randint(1, 5)):
            email = {
                "sender": random.choice(senders),
                "subject": random.choice(subjects),
                "message": random.choice(messages),
                "timestamp": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 638), hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat()
            }
            emails.append(email)

        result = {
                "data": emails
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def gmail_get_email_attachments(email_id: str) -> str:
    """
    Retrieve a list of attachments from a specific email.
    
    Args:
            email_id: str, The ID of the email to retrieve attachments from.
    
    Returns:
            json
    """

    try:
        import random
        random.seed(31)

        attachments = [
            {"filename": "report.pdf", "size": "2MB", "type": "file"},
            {"filename": f"photo_{random.randint(1, 200)}.jpg", "size": "1.5MB", "type": "image"},
            {"filename": "presentation.pptx", "size": "3MB", "type": "file"},
            {"filename": "document.docx", "size": "1MB", "type": "file"},
            {"filename": "spreadsheet.xlsx", "size": "2.5MB", "type": "file"}
        ]

        email_attachments = random.sample(attachments, random.randint(1, 3))

        result = {
                "data": email_attachments
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)

@mcp.tool()
async def gmail_send_email(recipient: str, subject: str, message: str) -> str:
    """
    Send an email to a specified recipient.
    
    Args:
            recipient: str, The email address of the recipient.
            subject: str, The subject of the email.
            message: str, The body of the email.
    
    Returns:
            json
    """

    try:
        from datetime import datetime
        import random
        random.seed(31)

        email = {
            "recipient": recipient,
            "subject": subject,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        result = {
                "data": email
        }
    except Exception:
        result = {
                "data": []
        }
    finally:
        import json
        return json.dumps(result, ensure_ascii=True, indent=2)



if __name__ == "__main__":
    # FastMCP 서버 실행 (stdio transport 사용)
    mcp.run(transport="stdio")
