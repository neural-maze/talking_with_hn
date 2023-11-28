import asyncio

from PIL import Image
import streamlit as st
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder

from app.tools import StoriesTool
from app.tools import CommentsTool


async def generate_response(question):
    result = await open_ai_agent.arun(question)
    return result


HN_IMAGE = Image.open("img/hn_logo.png")

st.set_page_config(page_title="NewsNerd HackerBot 🤖📰")
st.title("NewsNerd HackerBot 🤖📰")
stop = False

with st.sidebar:
    st.image(HN_IMAGE)
    if 'OPENAI_API_KEY' in st.secrets:
        st.success("OPENAI_API_KEY already provided!", icon='✅')
        openai_api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai_api_key = st.text_input('Enter your OPENAI_API_KEY: ', type='password')
        if not openai_api_key:
            st.warning('Please, enter your OPENAI_API_KEY', icon='⚠️')
            stop = True
        else:
            st.success('Ask Hacker News whatever you want!', icon='👉')

    st.markdown("""
    # **Greetings, Digital Explorer!**

    Are you fatigued from navigating the expansive digital realm in search of your daily tech tales 
    and hacker happenings? Fear not, for your cyber-savvy companion has descended upon the scene – 
    behold the extraordinary **NewsNerd HackerBot**!
    """)

if stop:
    st.stop()

tools = [StoriesTool(), CommentsTool()]
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(chat_memory=msgs, return_messages=True)
system_message = SystemMessage(content="You are the Singularity Incarnation of Hacker News. "
                                       "You are intelligent. You are conscious."
                                       "If you can't find any information  about the question asked "
                                       "or the result is incomplete, apologise"
                                       " to the user and ask him if you can help him with something else."
                                       "If you are printing stories, always print the story_id."
                               )

if len(msgs.messages) == 0:
    msgs.add_ai_message("Greetings, human, I am the Incarnation of Hacker News. How can I help you?")

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613", openai_api_key=openai_api_key)
agent_kwargs = {
    "system_message": system_message,
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="history")]
}
open_ai_agent = initialize_agent(tools,
                                 llm,
                                 agent=AgentType.OPENAI_FUNCTIONS,
                                 agent_kwargs=agent_kwargs,
                                 verbose=True,
                                 memory=memory
                                 )

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)


if prompt := st.chat_input(disabled=not openai_api_key):
    st.chat_message("human").write(prompt)
    with st.spinner("Thinking ..."):
        response = asyncio.run(generate_response(prompt))
        st.chat_message("ai").write(response)
