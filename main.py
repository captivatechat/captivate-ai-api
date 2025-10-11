from src.captivate_ai_api.Captivate import ActionModel, Captivate, FileCollectionModel,CardCollectionModel,CardMessageModel, FileModel, HtmlMessageModel, TableMessageModel, TextMessageModel,ButtonMessageModel, CaptivateResponseModel, ChatRequest
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import time
app = FastAPI(title="Captivate AI API", version="1.0.0")

# Original test data
data_action = {
    "session_id": "lance_catcher_two_602dd1f8-d932-4b13-8c33-162d7dfb929d",
    "endpoint": "action",
    "user_input": "tell me about EU regulations",
    "files": [
        {
            "filename": "EU_Regulations_2024.pdf",
            "type": "application/pdf",
            "file": {},
            "textContent": {
                "type": "file_content",
                "text": "EU REGULATIONS 2024\n\nThis document outlines the latest European Union regulations regarding data protection, privacy, and compliance requirements for businesses operating within the EU market. Key areas covered include GDPR updates, new data localization requirements, and enhanced consumer protection measures.\n\nKey Points:\n- Updated data processing consent mechanisms\n- Enhanced breach notification timelines\n- New requirements for AI and automated decision-making\n- Stricter penalties for non-compliance",
                "metadata": {
                    "source": "file_attachment",
                    "originalFileName": "EU_Regulations_2024.pdf",
                    "storageType": "direct"
                }
            },
            "storage": {
                "fileKey": "uploads/1704067200000-abc123-EU_Regulations_2024.pdf",
                "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-abc123-EU_Regulations_2024.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "expiresIn": 1704070800,
                "fileSize": 2048000,
                "processingTime": 25
            }
        },
        {
            "filename": "compliance_notes.txt",
            "type": "text/plain",
            "file": {},
            "textContent": {
                "type": "file_content",
                "text": "COMPLIANCE NOTES\n\nAction Items:\n1. Review GDPR compliance checklist\n2. Update privacy policy by end of month\n3. Schedule compliance training for Q1\n4. Audit data processing activities\n\nNotes:\n- Current compliance score: 85%\n- Next audit scheduled: March 15, 2024\n- Key contact: compliance@company.com",
                "metadata": {
                    "source": "file_attachment",
                    "originalFileName": "compliance_notes.txt",
                    "storageType": "direct"
                }
            },
            "storage": {
                "fileKey": "uploads/1704067200000-def456-compliance_notes.txt",
                "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-def456-compliance_notes.txt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "expiresIn": 1704070800,
                "fileSize": 512000,
                "processingTime": 5
            }
        },
        {
            "filename": "regulation_flowchart.png",
            "type": "image/png",
            "file": {},
            "textContent": {
                "type": "file_content",
                "text": "[Image: Regulation Flowchart]\nThis flowchart shows the decision tree for EU regulation compliance, including key decision points for data processing, consent management, and breach response procedures.",
                "metadata": {
                    "source": "file_attachment",
                    "originalFileName": "regulation_flowchart.png",
                    "storageType": "direct"
                }
            },
            "storage": {
                "fileKey": "uploads/1704067200000-ghi789-regulation_flowchart.png",
                "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-ghi789-regulation_flowchart.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                "expiresIn": 1704070800,
                "fileSize": 1536000,
                "processingTime": 12
            }
        }
    ],
    "incoming_action": [
        {
            "id": "sendEmail",
            "payload": {
                "email": "delvallelance@gmail.com",
                "message": "You are fired",
            },
        }
    ],
    "metadata": {
        "internal": {
            "channelMetadata": {
                "course_id":"abc",
                "channelMetadata": {"channel": "custom-channel", "channelData": {}},
                "user": {
                    "firstName": "Lance",
                    "lastName": "safa",
                    "email": "asdaf@gmail.com",
                },
                "phoneNumber": None,
                "custom": {
                    "mode": "non-dbfred",
                    "title": {
                        "type": "title",
                        "title": '"Latest Updates on EU Regulations"',
                    },
                },
            }
        }
    },
    "hasLivechat": False,
}



@app.post("/chat", response_model=CaptivateResponseModel)
async def chat(request: ChatRequest):
    """
    Chat endpoint for Captivate AI API
    """
    try:
        # Create Captivate instance using factory method
        captivate_instance = Captivate.create(request)
        
        # Alternative approach for backward compatibility:
        # captivate_instance = Captivate(**request.model_dump())     # Direct constructor
        print(request.model_dump())
        print(captivate_instance.get_user_input())
        print(captivate_instance.get_files())
        
        # Process files if any are provided
        file_info = ""
        files = captivate_instance.get_files()
        if files:
            file_info = f"\n\nI received {len(files)} file(s):\n"
            for i, file in enumerate(files, 1):
                filename = file.get('filename', 'Unknown')
                file_type = file.get('type', 'Unknown type')
                file_size = file.get('storage', {}).get('fileSize', 'Unknown size')
                text_content = file.get('textContent', {}).get('text', '')
                
                file_info += f"{i}. {filename} ({file_type}, {file_size} bytes)\n"
                
                # Show preview of text content if available
                if text_content:
                    preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
                    file_info += f"   Content preview: {preview}\n"
        
        # Create a response that includes file information
        messages = [
            TextMessageModel(text=f"This is a text response from lance local{file_info}"),
        ]
        # Set response
        captivate_instance.set_response(messages)
        

        print(captivate_instance.get_response())
        # Return the actual Captivate response
        return captivate_instance.get_response()
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Captivate AI API is running", 
        "version": "1.0.0",
        "endpoints": {
            "/chat": "POST - Main chat endpoint",
            "/health": "GET - Health check",
            "/test-file-handling": "GET - Test file handling functionality",
            "/test-router-mode": "GET - Test router mode functionality with decorator pattern"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

@app.get("/test-file-handling")
async def test_file_handling():
    """
    Test endpoint to demonstrate file handling functionality
    """
    try:
        # Create a test request with sample files using the real-world structure
        test_request = ChatRequest(
            session_id="test_file_session_123",
            user_input="Please analyze these files",
            files=[
                {
                    "filename": "Sample_Document.pdf",
                    "type": "application/pdf",
                    "file": {},
                    "textContent": {
                        "type": "file_content",
                        "text": "SAMPLE DOCUMENT\n\nThis is a sample PDF document containing important business information. It includes financial reports, market analysis, and strategic recommendations for Q1 2024.\n\nKey Findings:\n- Revenue increased by 15% compared to last quarter\n- Market share expanded in European markets\n- New product launch scheduled for March",
                        "metadata": {
                            "source": "file_attachment",
                            "originalFileName": "Sample_Document.pdf",
                            "storageType": "direct"
                        }
                    },
                    "storage": {
                        "fileKey": "uploads/1704067200000-test123-Sample_Document.pdf",
                        "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-test123-Sample_Document.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                        "expiresIn": 1704070800,
                        "fileSize": 1536000,
                        "processingTime": 18
                    }
                },
                {
                    "filename": "sales_data.csv",
                    "type": "text/csv",
                    "file": {},
                    "textContent": {
                        "type": "file_content",
                        "text": "Date,Product,Revenue,Units Sold\n2024-01-01,Product A,15000,100\n2024-01-02,Product B,22000,150\n2024-01-03,Product C,18000,120\n2024-01-04,Product A,16000,110\n2024-01-05,Product B,25000,170",
                        "metadata": {
                            "source": "file_attachment",
                            "originalFileName": "sales_data.csv",
                            "storageType": "direct"
                        }
                    },
                    "storage": {
                        "fileKey": "uploads/1704067200000-test456-sales_data.csv",
                        "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-test456-sales_data.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                        "expiresIn": 1704070800,
                        "fileSize": 256000,
                        "processingTime": 3
                    }
                },
                {
                    "filename": "quarterly_chart.jpg",
                    "type": "image/jpeg",
                    "file": {},
                    "textContent": {
                        "type": "file_content",
                        "text": "[Image: Quarterly Performance Chart]\nThis chart shows quarterly revenue trends, customer acquisition metrics, and market penetration data for the past 12 months.",
                        "metadata": {
                            "source": "file_attachment",
                            "originalFileName": "quarterly_chart.jpg",
                            "storageType": "direct"
                        }
                    },
                    "storage": {
                        "fileKey": "uploads/1704067200000-test789-quarterly_chart.jpg",
                        "presignedUrl": "https://s3.amazonaws.com/bucket/uploads/1704067200000-test789-quarterly_chart.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=...",
                        "expiresIn": 1704070800,
                        "fileSize": 1024000,
                        "processingTime": 8
                    }
                }
            ],
            metadata={
                "internal": {
                    "channelMetadata": {
                        "user": {"firstName": "Test", "lastName": "User", "email": "test@example.com"},
                        "channelMetadata": {"channel": "test"},
                        "custom": {},
                        "private": {}
                    }
                }
            },
            hasLivechat=False
        )
        
        # Create Captivate instance
        captivate_instance = Captivate.create(test_request)
        
        # Get file information
        files = captivate_instance.get_files()
        
        # Create response with comprehensive file details
        file_details = []
        for file in files:
            storage_info = file.get('storage', {})
            text_content = file.get('textContent', {})
            
            file_details.append({
                "filename": file.get('filename', 'Unknown'),
                "type": file.get('type', 'Unknown'),
                "fileSize": storage_info.get('fileSize', 'Unknown'),
                "processingTime": storage_info.get('processingTime', 'Unknown'),
                "fileKey": storage_info.get('fileKey', 'No file key'),
                "hasTextContent": bool(text_content.get('text')),
                "textPreview": text_content.get('text', '')[:100] + "..." if text_content.get('text') and len(text_content.get('text', '')) > 100 else text_content.get('text', ''),
                "metadata": text_content.get('metadata', {})
            })
        
        return {
            "message": "File handling test completed successfully",
            "total_files": len(files),
            "files": file_details,
            "user_input": captivate_instance.get_user_input(),
            "session_id": captivate_instance.session_id
        }
        
    except Exception as e:
        return {
            "error": "File handling test failed",
            "message": str(e)
        }

@app.get("/test-router-mode")
async def test_router_mode():
    """
    Test endpoint to demonstrate router mode functionality
    """
    test_results = []
    
    try:
        # Create a test instance
        test_data = {
            "session_id": "test_session_123",
            "metadata": {
                "internal": {
                    "channelMetadata": {
                        "user": {"firstName": "Test", "lastName": "User", "email": "test@example.com"},
                        "channelMetadata": {"channel": "test"},
                        "custom": {},
                        "private": {},
                        "conversationCreatedAt": "2024-01-15T10:30:00Z",
                        "conversationUpdatedAt": "2024-01-15T10:35:00Z"
                    }
                }
            },
            "hasLivechat": False
        }
        
        captivate_instance = Captivate(**test_data)
        
        # Test 1: Router mode disabled by default
        test_results.append({
            "test": "Router mode disabled by default",
            "expected": False,
            "actual": captivate_instance.is_router_mode(),
            "passed": captivate_instance.is_router_mode() == False
        })
        
        # Test 2: Protected methods should fail when router mode is disabled
        try:
            captivate_instance.set_agents(["agent_001", "agent_002"])
            test_results.append({
                "test": "set_agents should fail when router mode disabled",
                "expected": "ValueError",
                "actual": "No error raised",
                "passed": False
            })
        except ValueError as e:
            test_results.append({
                "test": "set_agents should fail when router mode disabled",
                "expected": "ValueError",
                "actual": str(e),
                "passed": "set_agents is only available when router mode is enabled." in str(e)
            })
        
        try:
            captivate_instance.get_outgoing_action()
            test_results.append({
                "test": "get_outgoing_action should fail when router mode disabled",
                "expected": "ValueError",
                "actual": "No error raised",
                "passed": False
            })
        except ValueError as e:
            test_results.append({
                "test": "get_outgoing_action should fail when router mode disabled",
                "expected": "ValueError",
                "actual": str(e),
                "passed": "get_outgoing_action is only available when router mode is enabled." in str(e)
            })
        
        try:
            captivate_instance.is_escalating_to_agent_router()
            test_results.append({
                "test": "is_escalating_to_agent_router should fail when router mode disabled",
                "expected": "ValueError",
                "actual": "No error raised",
                "passed": False
            })
        except ValueError as e:
            test_results.append({
                "test": "is_escalating_to_agent_router should fail when router mode disabled",
                "expected": "ValueError",
                "actual": str(e),
                "passed": "is_escalating_to_agent_router is only available when router mode is enabled." in str(e)
            })
        
        # Test 3: Enable router mode
        captivate_instance.enable_router_mode()
        test_results.append({
            "test": "Router mode enabled",
            "expected": True,
            "actual": captivate_instance.is_router_mode(),
            "passed": captivate_instance.is_router_mode() == True
        })
        
        # Test 4: Protected methods should work when router mode is enabled
        try:
            captivate_instance.set_agents(["agent_001", "agent_002", "agent_003"])
            test_results.append({
                "test": "set_agents should work when router mode enabled",
                "expected": "Success",
                "actual": "Success",
                "passed": True
            })
        except Exception as e:
            test_results.append({
                "test": "set_agents should work when router mode enabled",
                "expected": "Success",
                "actual": str(e),
                "passed": False
            })
        
        # Test 5: Get agents list
        agents = captivate_instance.get_agents()
        test_results.append({
            "test": "get_agents should return the set agents list",
            "expected": ["agent_001", "agent_002", "agent_003"],
            "actual": agents,
            "passed": agents == ["agent_001", "agent_002", "agent_003"]
        })
        
        # Test 6: Set outgoing action and test get_outgoing_action
        test_action = ActionModel(id="test_action", payload={"test": "data"})
        captivate_instance.set_outgoing_action([test_action])
        
        try:
            outgoing_actions = captivate_instance.get_outgoing_action()
            test_results.append({
                "test": "get_outgoing_action should work when router mode enabled",
                "expected": "Success",
                "actual": "Success",
                "passed": True
            })
        except Exception as e:
            test_results.append({
                "test": "get_outgoing_action should work when router mode enabled",
                "expected": "Success",
                "actual": str(e),
                "passed": False
            })
        
        # Test 7: Test escalation detection
        captivate_instance.escalate_to_agent_router(
            reason="Test escalation",
            intent="test_intent",
            recommended_agents=["agent_001", "agent_002"]
        )
        
        try:
            escalation_payload = captivate_instance.is_escalating_to_agent_router()
            test_results.append({
                "test": "is_escalating_to_agent_router should work when router mode enabled",
                "expected": "Success",
                "actual": "Success",
                "passed": True
            })
        except Exception as e:
            test_results.append({
                "test": "is_escalating_to_agent_router should work when router mode enabled",
                "expected": "Success",
                "actual": str(e),
                "passed": False
            })
        
        # Test 8: Disable router mode and verify protected methods fail again
        captivate_instance.disable_router_mode()
        test_results.append({
            "test": "Router mode disabled",
            "expected": False,
            "actual": captivate_instance.is_router_mode(),
            "passed": captivate_instance.is_router_mode() == False
        })
        
        try:
            captivate_instance.set_agents(["agent_004"])
            test_results.append({
                "test": "set_agents should fail again when router mode disabled",
                "expected": "ValueError",
                "actual": "No error raised",
                "passed": False
            })
        except ValueError as e:
            test_results.append({
                "test": "set_agents should fail again when router mode disabled",
                "expected": "ValueError",
                "actual": str(e),
                "passed": "set_agents is only available when router mode is enabled." in str(e)
            })
        
        # Test 9: Test that agents_list can only be set once
        captivate_instance.enable_router_mode()
        try:
            captivate_instance.set_agents(["agent_005"])  # This should fail because agents_list was already set
            test_results.append({
                "test": "set_agents should fail when agents_list already set",
                "expected": "ValueError",
                "actual": "No error raised",
                "passed": False
            })
        except ValueError as e:
            test_results.append({
                "test": "set_agents should fail when agents_list already set",
                "expected": "ValueError",
                "actual": str(e),
                "passed": "agents_list can only be set once" in str(e)
            })
        
        # Calculate overall test results
        passed_tests = sum(1 for result in test_results if result["passed"] is True)
        total_tests = len(test_results)
        
        return {
            "message": "Router Mode Decorator Tests",
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%"
            },
            "test_results": test_results
        }
        
    except Exception as e:
        return {
            "error": "Test execution failed",
            "message": str(e),
            "test_results": test_results
        }

async def main():
    """
    Original test function - can be called separately
    """
    try:
        captivate_instance = Captivate(**data_action)
        print('Captivate instance created successfully')
        captivate_instance.set_conversation_title('Lord of the rings')
        print('Conversation title set successfully')
        # Test set_private_metadata and get_metadata
        captivate_instance.set_private_metadata('my_secret', 123)
        print('private my_secret:', captivate_instance.get_metadata('my_secret'))
        # Test reserved key protection
        print("Testing 'private' key...")
        try:
            captivate_instance.set_metadata('private', 'should fail')
        except Exception as e:
            print('Expected error for reserved key:', e)

        print("Testing 'title' key...")
        try:
            captivate_instance.set_metadata('title', 'should fail')
        except Exception as e:
            print('Expected error for reserved key:', e)

        print("Testing 'conversation_title' key...")
        try:
            captivate_instance.set_metadata('conversation_title', 'should fail')
        except Exception as e:
            print('Expected error for reserved key:', e)
        #print(captivate_instance.get_conversation_title())
        #print(captivate_instance.get_incoming_action())
        messages = [
            TextMessageModel(text="Lets party!"),
            #TextMessageModel(text="I can do this!"),
            #ButtonMessageModel(buttons={"title": "Learn More", "options": [{"label":"Yes","value":"Yes"}]}),
            #TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            #CardCollectionModel(cards=[CardMessageModel(
            #    text="Special Offer",
            #    description="Get 20% off your next purchase.",
            #    image_url="https://example.com/offer.png",
            #    link="https://example.com/deals"
            #)]),
            #HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
            #FileCollectionModel(files=[FileModel(type='application/pdf',url="https://example.com/manual.pdf", filename="UserManual.pdf")] ),
            {"type": "policy_assesment_id","id":"12345"}
            ]

        # Send messages
        captivate_instance.set_response(messages)


        outgoing_actions = [
            ActionModel(id="navigate", payload={"url": "https://example.com"}),
            ActionModel(id="submit", data={"form_id": "1234"})
        ]
        #captivate_instance.set_outgoing_action(outgoing_actions)
        print(captivate_instance.get_response())
        #await captivate_instance.async_send_message(environment="dev") #dev or prod
        await captivate_instance.async_send_message(environment="dev") #dev or prod
        #print(captivate_instance.get_response())
        #print("Captivate Model Instance:", captivate_instance.model_dump_json(indent=4))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
