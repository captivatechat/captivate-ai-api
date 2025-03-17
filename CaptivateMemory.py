from langchain_openai import AzureChatOpenAI


llm = AzureChatOpenAI(
    api_key="7yHVQZhzlHFw683CRKIDQ29LjYafpG76FwaGLNst71wNpAIKsjchJQQJ99AKACmepeSXJ3w3AAAAACOGxLTN",
    azure_endpoint="https://azureaihub6679550331.openai.azure.com/",
    api_version="2024-08-01-preview",  # Change based on your API version
    model="gpt-4o-mini",
    max_retries=3
).bind(response_format={"type": "json_object"})

prompt = f"""
        You are an Agent tasked to generate a concise title for a conversation based on the user's message. The title should be brief and short, with a maximum of 5 words.  Return the title as a JSON object with the key "title".  For example:

        ```json
        {{"title": "Concise Conversation Title"}}
        Message: Please change my name to Lance?
        """

print(llm.invoke(prompt).content)

