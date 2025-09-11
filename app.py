# pip install streamlit groq python-dotenv edge-tts

import os
import time
import streamlit as st
import asyncio
import edge_tts
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ----------------------------
# 🎤 Microsoft Edge TTS
# ----------------------------
async def fast_edge_tts(text, voice="en-US-JessaNeural", file_name="output.wav"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(file_name)
    return file_name

def edge_tts_sync(text, voice="en-US-JessaNeural", file_name="output.wav"):
    asyncio.run(fast_edge_tts(text, voice, file_name))
    return file_name

# ----------------------------
# Streamlit UI Setup
# ----------------------------
st.set_page_config(page_title="Groq's MCP Playground", page_icon="⚡", layout="centered")
st.markdown(
    "<h1><span style='color: #fc4503;'>⚡World's Fastest MCP Studio </span>"
    "<img src='https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/mcp.png' width='40'></h1>",
    unsafe_allow_html=True,
)

st.sidebar.image("https://miro.medium.com/v2/1*b9wiAr_HG6ct7uYtCnf0xA.png", width='stretch')

# Sidebar - Model selection
st.sidebar.header("⚙️ Settings")
model_choice = st.sidebar.selectbox(
    "Choose Model",
    ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "moonshotai/kimi-k2-instruct-0905"],
    index=0
)

# Sidebar - MCP tool selection
st.sidebar.subheader("🔌 MCP Tools")
use_exa = st.sidebar.checkbox("Exa Search", value=True)
use_tavily = st.sidebar.checkbox("Tavily Search", value=False)
use_serper = st.sidebar.checkbox("Serper Search", value=False)
use_linkup = st.sidebar.checkbox("LinkUp Search", value=False)
use_twitter = st.sidebar.checkbox("Twitter", value=False)



# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Avatar images
ASSISTANT_AVATAR = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSxsh0CyhpofrQ95jBcDBlDhWHOQ1ZRLQPwdQ&s"
USER_AVATAR = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/480px-User_icon_2.svg.png"

# Maintain chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm your research assistant — I fetch live web info and can tweet it for you."}
    ]

# Display history
for msg in st.session_state.messages:
    avatar = USER_AVATAR if msg["role"] == "user" else ASSISTANT_AVATAR
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ----------------------------
# 💬 User Input
# ----------------------------
if prompt := st.chat_input("Ask me anything..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # Assistant streaming response
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""

        # Build MCP tools dynamically
        tools = []
        if use_exa:
            tools.append({
                "type": "mcp",
                "server_label": "Exa",
                "server_url": f"https://mcp.exa.ai/mcp?exaApiKey={os.getenv('EXA_API_KEY')}",
                "headers": {}
            })
        if use_tavily:
            tools.append({
                "type": "mcp",
                "server_label": "Tavily",
                "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv('TAVILY_API_KEY')}",
                "headers": {}
            })
        if use_serper:
            tools.append({
                "type": "mcp",
                "server_label": "Serper",
                "server_url": f"https://server.smithery.ai/@marcopesani/mcp-server-serper/mcp?api_key=318135fb-4ad4-4437-b916-9e19a8840f62&profile=yearning-rattlesnake-WM9iJg",
                "headers": {}
            })
        
        if use_linkup:
            tools.append({
                "type": "mcp",
                "server_label": "LinkUp",
                "server_url": f"https://apollo-khnbaduxb-composio.vercel.app/v3/mcp/d6ace0ba-928c-4d90-aeaf-507e0c94e6b9/mcp?include_composio_helper_actions=true",
                "headers": {}
            })
        if use_twitter:
            tools.append({
                "type": "mcp",
                "server_label": "Twitter",
                "server_url": f"https://apollo-khnbaduxb-composio.vercel.app/v3/mcp/9ee40a54-f652-4d93-8807-9ce8da07affa/mcp?include_composio_helper_actions=true",
                "headers": {}
            })
        

        # Build request parameters
        request_params = {
            "model": model_choice,
            "messages": st.session_state.messages,
            "temperature": 0.9,
            "max_completion_tokens": 2048,
            "top_p": 1,
            "stream": True,
            "stop": None,
            "tools": tools
        }

        # Only add reasoning_effort if not using Kimi model
        if model_choice != "moonshotai/kimi-k2-instruct-0905":
            request_params["reasoning_effort"] = "medium"

        # Call Groq with chosen MCP tools
        completion = client.chat.completions.create(**request_params)

        # Stream chunks with Pac-Man cursor 🟡
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(
                    full_response + " <img src='https://media.tenor.com/HiVVJv-skJcAAAAM/pac-man.gif' width='22' style='vertical-align: middle;'/>",
                    unsafe_allow_html=True
                )
                time.sleep(0.00000000000000000000000000000001)

        # Final text
        message_placeholder.markdown(full_response)

        # 🔊 Speak the response with Edge TTS
        wav_file = edge_tts_sync(full_response, voice="en-US-JessaNeural")
        st.audio(wav_file, format="audio/wav")

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": full_response})
