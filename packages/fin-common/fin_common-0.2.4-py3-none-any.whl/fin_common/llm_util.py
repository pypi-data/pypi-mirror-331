from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.chains import LLMChain

load_dotenv()

llm = AzureChatOpenAI(deployment_name="gpt-4o", temperature=0.9)

def query_llm(question, prompt_template):
    conversation = LLMChain(
        llm=llm,
        prompt=prompt_template,
        verbose=True,
    )
    response = conversation.predict(input=question)
    return response

def query_structured_llm(prompt, class_schema):
    structured_llm = llm.with_structured_output(class_schema)
    return structured_llm.invoke(prompt)
