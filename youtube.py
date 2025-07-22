from secret_key import googleapi_key
from langchain_google_genai import ChatGoogleGenerativeAI
from youtube_transcript_api import YouTubeTranscriptApi
from typing import TypedDict 
from langchain.prompts import PromptTemplate 
from langgraph.graph.state import StateGraph
import requests

import os
os.environ['GOOGLE_API_KEY'] = googleapi_key

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

#graph state schema
class video_summary_state(TypedDict):
    url: str
    transcript: str
    summary: str

def get_transcript(video_url: str) -> str:
    video_id = video_url.split("v=")[-1]
    # print(video_id)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ""
    for entry in transcript_list:
        transcript_text += entry['text'] + " "
    if(transcript_text):
        print("Transcript Fetched")
    else:
        print("Transcript not available for this video.")
    return transcript_text

def summarize_tool(transcript_text: str)-> str: 
  # print(transcript_text)
  print("Generating response...")
  prompt = PromptTemplate(template="You are an expert video summarizer. Summarize the following video transcript in a clear, concise and engaging way. Highlight key points, main ideas, and important takeaways. Keep it under 200 words: {transcript_text}") 

  chain = prompt | llm
  result = chain.invoke({"transcript_text": transcript_text}) 
  return result.text()


#making graph nodes
def input_node(state: dict):
    state["url"] = input("Enter YouTube video URL: ")
    return state

def transcript_node(state):
    video_url = state.get("url")
    state["transcript"] = get_transcript(video_url) 
    return state

def summarize_node(state):
    transcript_text = state.get("transcript")
    state["summary"] = summarize_tool(transcript_text)
    return state


#building graph
graph = StateGraph(state_schema = video_summary_state)

graph.add_node("input", input_node)
graph.add_node("transcript", transcript_node)
graph.add_node("summary", summarize_node)

graph.set_entry_point("input")

graph.add_edge("input","transcript")
graph.add_edge("transcript", "summary")

app = graph.compile()

app = graph.compile()

# # --- Add this part to generate the SVG ---
# try:
#     # Get the graph structure as a pygraphviz AGraph
#     agraph = app.get_graph().draw_pgv()
    
#     # Write the graph to an SVG file
#     agraph.draw("youtube_summary_graph.svg", format="svg", prog="dot")
#     print("\nGraph SVG has been generated: youtube_summary_graph.svg")

# except ImportError:
#     print("\nCould not generate graph SVG. Please install pygraphviz:")
#     print("pip install pygraphviz")
# # --- End of new part ---


# final step for running the model
state = {}
final_state = app.invoke(state)
print("Summary of the video provided: " + final_state.get("summary"))

# # Optional: Save SVG
# graph_code = final_state.get_graph(xray=True).draw_mermaid()
# KROKI_API_URL = "https://kroki.io/mermaid/svg"
# response = requests.post(
#     KROKI_API_URL, json={"diagram_source": graph_code}, timeout=60
# )
# response.raise_for_status()
# with open("execution-graph.svg", "wb") as f:
#     f.write(response.content)
#         # ava_logger.info("Graph saved as execution-graph.svg")
#     # except requests.exceptions.RequestException as e:
#         # ava_logger.info(f"Error: {e}")

# Output result
print("\nSummary of the video provided:\n")
print(final_state.get("summary"))
 
# Optional: Save execution graph as SVG
try:
    graph_code = app.get_graph(xray=True).draw_mermaid()
    KROKI_API_URL = "https://kroki.io/mermaid/svg"
    response = requests.post(
        KROKI_API_URL,
        json={"diagram_source": graph_code},
        timeout=60
    )
    response.raise_for_status()
    with open("execution-graph.svg", "wb") as f:
        f.write(response.content)
    print("\n✅ Execution graph saved as 'execution-graph.svg'")
except requests.exceptions.RequestException as e:
    print(f"\n❌ Error generating execution graph: {e}")