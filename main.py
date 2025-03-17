from src.captivate_ai_api.Captivate import (
    ActionModel,
    Captivate,
    FileCollectionModel,
    CardCollectionModel,
    CardMessageModel,
    FileModel,
    HtmlMessageModel,
    TableMessageModel,
    TextMessageModel,
    ButtonMessageModel,
)
import asyncio
from langchain_openai import AzureChatOpenAI


llm = AzureChatOpenAI(
    api_key="7yHVQZhzlHFw683CRKIDQ29LjYafpG76FwaGLNst71wNpAIKsjchJQQJ99AKACmepeSXJ3w3AAAAACOGxLTN",
    azure_endpoint="https://azureaihub6679550331.openai.azure.com/",
    api_version="2024-08-01-preview",  # Change based on your API version
    model="gpt-4o-mini",
    max_retries=3,
).bind(response_format={"type": "json_object"})


async def main():
    data_action = {
        "session_id": "C87C3QC-4S44T6E-MHFMJC3-5W916VX - 67c3fd77492d490014351d36 - fixthisaidz",
        "endpoint": "action",
        "user_input": "i am going to paris",
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
                    "course_id": "abc",
                    "channelMetadata": {"channel": "widget", "channelData": {}},
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
        #captivate_instance = Captivate(**data_action)  # for basic stateless

        captivate_instance = await Captivate.create(
          data_dict=data_action,
          memory_enabled=True,
          redis_url="redis://localhost:6379",
          llm=llm,  # optional
          longterm_context=False,  # optional
          generate_conversation_title=True,  # optional
         )

        # await captivate_instance.enable_memory(redis_url="redis://localhost:6379")
        # print(await captivate_instance.get_chat_history())
        # print(captivate_instance.get_conversation_title())
        # print(captivate_instance)
        # print(captivate_instance.get_response())
        # print(captivate_instance.get_conversation_title())
        # print(captivate_instance.get_incoming_action())
        messages = [
            # TextMessageModel(text="Yeohan so pogii"),
            # TextMessageModel(text="I can do this!"),
            # ButtonMessageModel(buttons={"title": "Learn More", "options": [{"label":"Yes","value":"Yes"}]}),
            # TableMessageModel(table="<table><tr><th>Name</th><th>Age</th></tr><tr><td>Alice</td><td>30</td></tr></table>"),
            # CardCollectionModel(cards=[CardMessageModel(
            #    text="Pere Duran",
            #    description="Get 20% off your next purchase.",
            #    image_url="https://uploadcare.mwcglobalprofile.com/a2801e3a-d314-4347-a319-72f52a86893a/",
            #    link="https://www.mwcbarcelona.com/agenda/speakers/13331-pere-duran"
            # )]),
            # HtmlMessageModel(html="<h2>Today's Highlights</h2><ul><li>News Item 1</li><li>News Item 2</li></ul>"),
            # FileCollectionModel(files=[FileModel(type='image',url="https://uploadcare.mwcglobalprofile.com/a2801e3a-d314-4347-a319-72f52a86893a/")] ),
            {
                "type": "files",
                "files": [{"type": "image", "url": "https://uploadcare.mwcglobalprofile.com/a2801e3a-d314-4347-a319-72f52a86893a/"}],
            },
        ]

        # Send messages
        await captivate_instance.set_response(messages)

        # outgoing_actions = [
        #     ActionModel(id="navigate", payload={"url": "https://example.com"}),
        #     ActionModel(id="submit", data={"form_id": "1234"}),
        # ]
        # captivate_instance.set_outgoing_action(outgoing_actions)
        # print(captivate_instance.get_response())
        # await captivate_instance.async_send_message(environment="dev") #dev or prod
        await captivate_instance.async_send_message(environment="dev")  # dev or prod
        # print(captivate_instance.get_response())
        # print("Captivate Model Instance:", captivate_instance.model_dump_json(indent=4))
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
