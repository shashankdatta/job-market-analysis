# Import Langchain dependencies
from langchain.agents import AgentExecutor, create_openai_tools_agent, Tool, ConversationalChatAgent
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun

from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate

from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

import streamlit as st
from langchain import hub 
from PIL import Image
import replicate
import os, re, json, requests

# Setup the app UI
jobly_icon, jobly_cover = Image.open('jobly_icon.png'), Image.open('jobly_cover.jpg')

st.set_page_config(page_title='Jobly', layout='wide', page_icon=jobly_icon)

msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)

def clear_chat_history():
    msgs.clear()
    msgs.add_ai_message("Hey, Jobly here! Ask me anything about the job market 📈")
    st.session_state.steps = {}
    # st.session_state.messages = [{"role": "assistant", "content": "Hey, Jobly here! Ask me anything about the job market 📈"}]

def get_available_openai_models(key):
    url = "https://api.openai.com/v1/models"
    headers = {
        "Authorization": f"Bearer {key}"
    }
    response = requests.get(url, headers=headers)

    # Extract the model names from the JSON object
    return [model['id'] for model in response.json()['data'] if model['id'].startswith('gpt')]

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
        temperature = st.slider('temperature', min_value=0.0, max_value=2.0, value=1.0, step=0.01)
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
    "**Matthew So** - Data Analyst"
    "**Rohit Mohanty** - Data Analyst"
    "**Shashank datta Bezgam** - Full Stack And LLM Developer"
    "**Ke Zhang** - Full Stack And LLM Developer"
    "**Jasmine Wu** - Web Scracping Developer"
    "---"
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/shashankdatta/job-market-analysis)"
    st.button('Clear Chat', on_click=clear_chat_history)

# This function Loads a PDF of your chosing
@st.cache_resource
def load_pdf():
    # Update PDF name here to whatever you Like
    pdf_name = ''
    loaders = [PyPDFLoader(pdf_name)]
    
    # Create index - aka vector database - aka chromadb
    index = VectorstoreIndexCreator(
    embedding = HuggingFaceEmbeddings(model_name='all-MiniLM-L12-v2'),
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)).from_loaders(loaders)
    
    # Retun the vector database
    return index

# Load er on up
# index = load_pdf()




st.title('🤖 Ask Jobly')
# st.subheader(" Powered by 🦜LangChain + OpenAI + Streamlit")
st.caption("🚀 A streamlit chatbot powered by OpenAI LLM")

# Set up a session state to store the chat messages variable to hold all the old messages
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [{"role": "assistant", "content": "Hey, Jobly here! Ask me anything about the job market 📈"}]
if len(msgs.messages) == 0:
    msgs.clear()
    msgs.add_ai_message("Hey, Jobly here! Ask me anything about the job market 📈")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}

# Display all the historical messages
# for msg in st.session_state.messages:
#     st.chat_message(msg["role"]).markdown(msg["content"])
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

# Function for generating OpenAI response
def generate_openai_response(prompt):
    optional_params = {
        "top_p": top_p,
        "frequency_penalty": frequency_penalty,
        "presence_penalty": presence_penalty,
    }
    
    llm = ChatOpenAI(model_name=selected_model, temperature=temperature,
                    openai_api_key=OPENAI_API_KEY, model_kwargs=optional_params,
                    streaming=True, verbose=False)
            
    # RGA
    # chain = RetrievalQA.from_chain_type(
    #     Llm=llm,
    #     chain_type='stuff',
    #     retriever=index.vectorstore.as_retriever(),
    #     input_key='question')
    
    # Construct the tools
    search = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper(region="de-de", 
                time="d", max_results=3), name="Search")
    wikidata = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())
    wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
    tools = [
                Tool(
                    name='wikipedia',
                    func= wikipedia.run,
                    description="Useful for when you need to look up information directly from a \
                        Wikipedia article about a topic, country, person, etc."
                ), Tool(
                    name='wikidata',
                    func= wikidata.run,
                    description="Useful for when you need to look up structured data about a \
                        topic, country, person, etc."
                ), Tool(
                    name='DuckDuckGo Search',
                    func= search.run,
                    description="Useful for when you need to do a search on the internet to find information \
                        that another tool can't find. Be specific with your input."
                )
            ]
    # Construct the OpenAI Tools agent
    # from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    # Examples of prompts
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", "You are a helpful assistant"),
    #         MessagesPlaceholder("chat_history", optional=True),
    #         ("human", "{input}"),
    #         MessagesPlaceholder("agent_scratchpad"),
    #     ]
    # )
    # prompt = ChatPromptTemplate.from_messages(
    # [
    #     (
    #         "system",
    #         "You are a helpful assistant. Make sure to use the tavily_search_results_json tool for information.",
    #     ),
    #     ("placeholder", "{chat_history}"),
    #     ("human", "{input}"),
    #     ("placeholder", "{agent_scratchpad}"),
    # ]
    # )

    # prompt_holder = hub.pull("hwchase17/openai-tools-agent")
    # chat_agent = create_openai_tools_agent(llm, tools, prompt_holder)
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm, tools)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
        verbose=False,
        max_iterations=3
    )
    
    # Display the response
    # st.chat_message("assistant").spinner("Thinking...").markdown(msg)
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke(prompt, cfg)

    return response

# Build a prompt input template to display the prompts
# If the user hits enter then
if not OPENAI_API_KEY:
    st.error("❌ Please add your OpenAI API key to continue.")
    st.stop()

if not selected_model:
    st.warning("⚠️ No OpenAI model selected. Please choose a model to continue.")

if prompt := st.chat_input("Ask Jobly something...", disabled=(not (OPENAI_API_KEY and selected_model))):
    # st.session_state.messages.append({"role": "user", "content": prompt})

    # Display the prompt
    st.chat_message("user").markdown(prompt)
    
    # Send the prompt to the OpenAI API
    # client = OpenAI(api_key=OPENAI_API_KEY)
    # response = client.chat.completions.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
    # msg = response.choices[0].message.content
    # st.session_state.messages.append({"role": "assistant", "content": msg})
    
    # OpenAI response to prompt input.
    response = generate_openai_response(prompt)

    st.markdown(response["output"])
    st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]
