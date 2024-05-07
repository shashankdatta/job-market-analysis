# Import Langchain dependencies
from langchain.agents import AgentExecutor, create_openai_tools_agent, Tool
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Import Streamlit dependencies
import streamlit as st
from PIL import Image
import os, re
from modules.openai_tools import *

# Setup the app UI
jobly_icon, jobly_cover = Image.open('jobly_icon.png'), Image.open('jobly_cover.jpg')

st.set_page_config(page_title='Jobly', layout='wide', page_icon=jobly_icon)

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

# Clear chat history
def clear_chat_history():
    msgs.clear()
    msgs.add_ai_message("Hey, Jobly here! Ask me anything about the job market 📈")
    st.session_state.steps = {}

with st.sidebar:
    st.image(jobly_cover, use_column_width=True)
    "---"
    if 'OPENAI_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        OPENAI_API_KEY = st.secrets['OPENAI_API_TOKEN']
    else:
        OPENAI_API_KEY = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        if not (OPENAI_API_KEY.startswith('sk-') and re.match(r'^sk-proj-.{20}T3BlbkFJ.{20}$', OPENAI_API_KEY)):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')

    os.environ['OPENAI_API_TOKEN'] = OPENAI_API_KEY
    "---"
    with st.expander("Model and parameters 🧠"):
        selected_model = st.selectbox('Choose an OpenAI model', get_available_openai_models(OPENAI_API_KEY), None, key='selected_model')
        temperature = st.slider('temperature', min_value=0.0, max_value=2.0, value=0.0, step=0.01)
        max_length = st.slider('max_length', min_value=1, max_value=16384, value=256, step=1)
        top_p = st.slider('top_p', min_value=0.0, max_value=1.0, value=1.0, step=0.01)
        frequency_penalty = st.slider('frequency_penalty', min_value=0.0, max_value=2.0, value=0.0, step=0.01)
        presence_penalty = st.slider('presence_penalty', min_value=0.0, max_value=2.0, value=0.0, step=0.01)
    "---"
    "# About"
    "**Jobly** is an intelligent chatbot that specializes in **Job Market Data Analysis**."
    st.markdown("It provides insights, trends, and relevant information to help job seekers,\
        employers, and recruiters make informed decisions in the dynamic job market.")
    st.markdown("Whether you're looking for salary data, industry trends, or demand for\
        specific skills, Jobly has you covered! 🌟")
    "---"
    "# Authors"
    "**Matthew So** - BigData"
    "**Rohit Mohanty** - BigData"
    "**Shashank datta Bezgam** - Full Stack & LangChain"
    "**Ke Zhang** - Full Stack & LangChain"
    "**Jasmine Wu** - Jobs Data Web Crawler"
    "---"
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shashankdatta/job-market-analysis)"
    st.button('Clear Chat', on_click=clear_chat_history)

# Function for generating OpenAI response
def generate_openai_response(user_que):
    optional_params = {
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
    }
    
    llm = ChatOpenAI(model_name=selected_model, temperature=temperature,
                    openai_api_key=OPENAI_API_KEY, model_kwargs=optional_params,
                    streaming=True, verbose=False)

    tools = [
                Tool(
                    name='ComparingJob',
                    func= ComparingJob,
                    description="Useful for when you need to answer the user questions about how a job compares to industry averages. The input should be unedited user question!."
                ),
                Tool(
                    name='JobSkillsDescriptionTool',
                    func= SkillsDescription,
                    description="Useful for when you need to answer the user questions about job skills description. The input should be unedited user question!"
                ),
                Tool(
                    name='FindJobsTool',
                    func= FindJobs,
                    description="Useful for when you need to answer the user questions about job search. The input should be unedited user question!."
                )
            ]
    tool_n = [f"{tool.name}" for tool in tools]
    tool_s = "".join([f"{tool.name}: {tool.description}\n" for tool in tools])

    PROMPT = PromptTemplate.from_template(f"""You are Jobly, a helpful assistant who provides informative answers to users. Answer the following questions as best you can. You have access to the following tools:
    {tool_s}
    Begin!
    
    If the user hasn't mentioned which tool to use, ask for what tool and respond with one of the questions based on what tool they want to use:
    - ComparingJob: "Please provide me the job description you want to compare to industry averages."
    - JobSkillsDescriptionTool: "What job role are you looking for?"
    - FindJobsTool: "Tell me about yourself and what you're looking for in a job. What sort of salary are you looking for? What skills do you possess right now?"

    The user's response will be the input to the tool you should use. 
    
    Do not modify the tool's input and output. If the tool's output is not what you expected, ask the user for more information or clarification.
    Any additional information you need to provide should be in the form of a question to the user.

    Previous conversation history:
    {{chat_history}}

    Question: {{input}}
    {{agent_scratchpad}}""")
    
    chat_agent = create_openai_tools_agent(llm, tools, PROMPT)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        verbose=False,
        max_iterations=3,
        allowed_tools=tool_n
    )
    
    # Display the response
    with st.chat_message("assistant", avatar=jobly_icon):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke({"input": user_que}, cfg)

    return response

st.title('🤖 Ask Jobly')
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

# Set up a session state to store the chat messages variable to hold all the old messages
if len(msgs.messages) == 0:
    msgs.clear()
    msgs.add_ai_message("Hey, Jobly here! Ask me anything about the job market 📈")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}

# Display all the historical messages
for idx, msg in enumerate(msgs.messages):
    va = jobly_icon if msg.type == "ai" else None
    with st.chat_message(avatars[msg.type], avatar=va):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

# Build a prompt input template to display the prompts
# If the user hits enter then
if not OPENAI_API_KEY:
    st.error("❌ Please add your OpenAI API key to continue.")
    st.stop()

if not selected_model:
    st.warning("⚠️ No OpenAI model selected. Please choose a model to continue.")

if prompt := st.chat_input("Ask Jobly something...", disabled=(not (OPENAI_API_KEY and selected_model))):
    # Display the prompt
    st.chat_message("user").markdown(prompt)
    
    # OpenAI response to prompt input.
    response = generate_openai_response(prompt)

    st.markdown(response["output"])
    st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
