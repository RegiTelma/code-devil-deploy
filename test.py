import streamlit as st
import openai
import os
from llama_index import StorageContext, load_index_from_storage
from pathlib import Path
import ipdb
import time


st.set_page_config(page_title="Chat with the LlamaIndex docs, powered by LlamaIndex", page_icon=":japanese_ogre:", layout="centered", initial_sidebar_state="auto", menu_items=None)
  
st.title("Code :red[(D)evil] :japanese_ogre:")

#with st.sidebar:
#    openai_api_key = st.text_input("OpenAI API Key",
#                                   key="chatbot_api_key",
#                                   type='password')

openai.api_key = st.secrets.OPENAI_API_KEY

#use this to check that the api key is correct
#st.write(openai.api_key)
path = Path(os.getcwd())  / 'data'

#st.subheader('Models and parameters')
#selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B', 'Llama2-70B'], key='selected_model')
#if selected_model == 'Llama2-7B':
#    llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
#elif selected_model == 'Llama2-13B':
#    llm = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
#else:
#    llm = 'replicate/llama70b-v2-chat:e951f18578850b652510200860fc4ea62b3b16fac280f83ff32282f87bbd2e48'
    

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about the LlamaIndex library!"}
    ]
    
@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the LlamaIndex docs – hang tight! This should take 1-2 minutes."):
        storage_context = StorageContext.from_defaults(persist_dir=str(path))
        index = load_index_from_storage(storage_context=storage_context)
        return index
        #TODO: figure out difference between ServiceContext and StorageContext and how to create the ServiceContext
        #      from the Github repo data
        #service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, 
        #                                                          system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        #index = VectorStoreIndex.from_documents(docs, service_context=service_context)
       
        #query_engine = index.as_chat_engine()

#temperature = st.sidebar.slider('Temperature', min_value=0., max_value=1., value=0., step=0.01)
 
index = load_data()
chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)#temperature=temperature

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

#chat_history=[]
#with chat_history:
#    st.sidebar.title("Chat History")
#    for history in chat_history:
#        st.write(message['content'])
        
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)



# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = chat_engine.chat(prompt)
            #placeholder = st.empty()
            #placeholder.markdown(response.response)
            #full_response = ''
            st.write(response.response)
            
            sources=[]
            url_to_sources=[]
            filepath=[]
            # Display all sources
            for i, source_node in enumerate(response.source_nodes, start=1):
                source_text = source_node.to_dict()['node']['text']
                source_metadata = source_node.to_dict()['node']['metadata']
                source_filepath = source_metadata['file_path']
                source_filename=source_metadata['file_name']
                if source_filename.endswith('.py'):
                    formatted_source  = f"#### Source #{i}\n```python\n{source_text}```"
                    st.markdown(formatted_source)
                else:
                    st.write(source_text)
                sources.append(formatted_source)
                st.markdown(f"Path within repo: **{source_filepath}**")
                
                url_to_concatenate_to_sources = f'https://github.com/jerryjliu/llama_index/tree/main/{source_filepath}'
                url_to_sources.append(url_to_concatenate_to_sources)
                st.markdown(f"Link to source: {url_to_concatenate_to_sources}")
            ipdb.set_trace()
            message = {"role": "assistant", "content": response.response}
            
            #for item in message:
            #    full_response += item
            #    placeholder.markdown(full_response)
            #    time.sleep(0.08)
            #placeholder.markdown(full_response)
            st.session_state.messages.append(message) # Add response to message history
            

        