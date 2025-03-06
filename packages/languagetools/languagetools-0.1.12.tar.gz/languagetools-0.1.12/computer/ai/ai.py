from openai import OpenAI
import requests
import base64
import os
from concurrent.futures import ThreadPoolExecutor
import time
import random

class Ai:
    def __init__(self, computer):
        self.computer = computer
        self.openai_client = None

    def upload(self, file_path):
        url = f"{self.computer.api_base}/upload"
        headers = {"Authorization": f"Bearer {self.computer.api_key}"}

        with open(file_path, 'rb') as file:
            file_data = file.read()

        print("Uploading...")

        response = requests.post(url, files={'file': file_data}, headers=headers).json()
        
        if "url" in response:
            print(f"Uploaded `{file_path}`. Please re-use this URL for future computer.ai.cloud operations involving that file:", response["url"])
            return response["url"]
        else:
            # Probably an error :(
            raise Exception(str(response))

    # should we make this more structured for better llm / cli UX?
    def cloud(self, tool, input):

        # tool_map = {
        #     "upscale": "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa"
        # }

        # if tool in tool_map:
        #     tool = tool_map["tool"]

        # import replicate  # pyright: ignore
        # output = replicate.run(
        #     tool,
        #     input,
        # )

        # return output

        url = f"{self.computer.api_base}/tools/"

        data = {
            "tool": tool,
            "input": input
        }
        headers = {"authorization": f"Bearer {self.computer.api_key}"}

        print(f"Running tool: {tool}...")

        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            output = response.json()["output"]
            print(f"Tool finished running. Output: {output}\nPlease reference the output above instead of rerunning the tool with the same inputs.")
            return output
        else:
            # an error :(
            raise Exception(str(response))

    def chat(
        self,
        query,
        system_message="You are a concise AI assistant.",
        image_path=None,
        base64_image=None,
        model_size="tiny",
        display=False,
        messages=None
    ):
        """
        It would be great if we could programatically flip display to True if it's at the end of a cell, jupyter style. And also make it not return its answer tho.
        """

        if self.openai_client == None:
            openai_client = OpenAI(base_url=self.computer.api_base + "/openai", api_key=self.computer.api_key)
            # openai_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key="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")

        if messages == None:
            messages = [
                # {
                #     "role": "system",
                #     "content": system_message,
                # },
                {"role": "user", "content": query},
            ]
            
            if image_path:
                with open(image_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                file_extension = os.path.splitext(image_path)[1].lower()
                mime_type = f"image/{file_extension[1:]}" if file_extension in ['.jpg', '.jpeg', '.png', '.gif'] else "image/jpeg"
                messages[-1]["content"] = [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
                ]
            elif base64_image:
                messages[-1]["content"] = [
                    {"type": "text", "text": query},
                    {"type": "image_url", "image_url": {"url": base64_image}}
                ]

        response = ""

        for _ in range(3):
            try:
                stream = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    stream=True,
                    extra_body={"chat_id": f"langtools_{random.randint(1000000, 9999999)}"}
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        if isinstance(content, str):
                            if display:
                                print(content, end="")
                            response += content
                break  # If successful, exit the retry loop
            except Exception as e:
                if "rate" in str(e).lower():
                    print("Rate limit may have been hit.")
                    sleep_duration = random.uniform(1, 4)
                    print(f"Sleeping for {sleep_duration:.2f} seconds...")
                    time.sleep(sleep_duration)
                else:
                    print("An error occurred:")
                    # traceback.print_exc()
                print("Retrying...")

        return response

    def summarize(self, text):
        query = "You are a highly skilled AI trained in language comprehension and summarization. I would like you to read the previous text and summarize it into a concise abstract paragraph. Aim to retain the most important points, providing a coherent and readable summary that could help a person understand the main points of the discussion without needing to read the entire text. Please avoid unnecessary details or tangential points."
        custom_reduce_query = "You are tasked with taking multiple summarized texts and merging them into one unified and concise summary. Maintain the core essence of the content and provide a clear and comprehensive summary that encapsulates all the main points from the individual summaries."
        return self.query(text, query, custom_reduce_query)

    def query(self, text, query, custom_reduce_query=None, model_size="tiny"):
        """
        text can be a string, a list of strings, or a list of dicts.
        If it's a list of dicts, if the dicts have a "text" parameter, that will be used as the text to split.
        All other parameters will be shoved into the LLM as strings with their key value pairs.
        """
        # If no custom reduce query is provided, use the map query for reduction
        map_query = query
        if custom_reduce_query == None:
            reduce_query = f"Multiple people answered THIS QUERY: {map_query}. Their answers are above. Synthesize the best answer, as though you're answering the query. PAY ATTENTION TO THE QUERY. Say only things that directly answer the query, nothing else."
        else:
            reduce_query = custom_reduce_query

        context_window = 7000 # This should be for the "long" model

        # Define the context window size in characters
        context_window_chars = int(context_window * 2.8)

        # Initialize an empty list to store the chunks of text
        chunks = []
        # Check if the text is a list of dictionaries
        if isinstance(text, list) and all(isinstance(i, dict) for i in text):
            # If so, iterate over each dictionary in the list
            for item in text:
                path = item.get("path")
                item_text = item.get("text")
                # Split the text into chunks based on the context window size
                for i in range(0, len(item_text), context_window_chars):
                    chunks.append(
                        {"path": path, "text": item_text[i : i + context_window_chars]}
                    )
        else:
            # If the text is not a list of dictionaries, split it into chunks based on the context window size
            for i in range(0, len(text), context_window_chars):
                chunks.append(
                    {"path": None, "text": text[i : i + context_window_chars]}
                )

        combined_chunks = []
        temp_chunk = ""

        for chunk in chunks:
            chunk_text = (chunk["path"] + "\n" if chunk["path"] else "") + chunk["text"]
            if len(temp_chunk) + len(chunk_text) <= context_window_chars:
                temp_chunk += "\n\n" + chunk_text
            else:
                combined_chunks.append(temp_chunk)
                temp_chunk = chunk_text

        if temp_chunk:
            combined_chunks.append(temp_chunk)

        chunks = [{"text": chunk.strip()} for chunk in combined_chunks]

        # Use a ThreadPoolExecutor to concurrently process the chunks
        with ThreadPoolExecutor() as executor:
            responses = list(
                executor.map(
                    lambda chunk: self.chat(
                        model_size=model_size,
                        query=f"""Query: {map_query}

Context:
{chunk['text']}

Above is a portion of the full context for the user's query. Use it to answer the following query:

{map_query}

ANSWER THE QUERY. If answering the query is impossible (i.e. a specific thing is being asked for, which is not present) say 'Not enough context, please rephrase or find the information another way.'""",
                        system_message="You are an intelligent AI assistant that can sift through large amounts of data to answer user's questions. You provide exact references and full quotations for your answers when you can."
                    ),
                    chunks
                )
            )

        # Define a function to compress the responses
        def compress_responses(responses, query, context_window_chars):
            # Continue compressing until there is only one response left
            while len(responses) > 1:
                combined_responses = []
                temp_response = ""
                for response in responses:
                    # If the combined response is within the context window size, add the response to it
                    if len(temp_response + response) <= context_window_chars:
                        temp_response += response
                    else:
                        # If the combined response exceeds the context window size, add the temporary response to the combined responses and start a new temporary response
                        combined_responses.append(temp_response)
                        temp_response = response
                if temp_response:
                    combined_responses.append(temp_response)

                # Use a ThreadPoolExecutor to concurrently process the combined responses
                with ThreadPoolExecutor() as executor:
                    responses = list(
                        executor.map(
                            self.chat,
                            [
                                response + "\n\n" + query
                                for response in combined_responses
                            ],
                        )
                    )
            return responses[0]

        # Compress the responses and return the final response
        final_response = compress_responses(
            responses, reduce_query, context_window_chars
        )

        return final_response