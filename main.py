from src.captivate_ai_api.Captivate import ActionModel, Captivate, FileCollectionModel,CardCollectionModel,CardMessageModel, FileModel, HtmlMessageModel, TableMessageModel, TextMessageModel,ButtonMessageModel
import asyncio

async def main():
    data_action = {
        "session_id": "lance_catcher_two_602dd1f8-d932-4b13-8c33-162d7dfb929d",
        "endpoint": "action",
        "user_input": "tell me about EU regulations",
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
    asyncio.run(main())
