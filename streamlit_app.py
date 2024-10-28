# Enhanced Streamlit Script
import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize OpenAI client with flexible secret management
def get_openai_api_key():
    # Try to get API key from Streamlit secrets first
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        # Fall back to environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("No OpenAI API key found. Please set it in .streamlit/secrets.toml or as an environment variable.")
            st.stop()
        return api_key

# Initialize the OpenAI client
client = OpenAI(api_key=get_openai_api_key())

# Initialize OpenAI client with Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Helper function to get embeddings
def get_embedding(input_text, model='text-embedding-3-small'):
    try:
        response = client.embeddings.create(
            input=input_text,
            model=model
        )
        return [x.embedding for x in response.data]
    except Exception as e:
        st.error(f"Error getting embeddings: {str(e)}")
        return None

# Function to generate completion from OpenAI
def get_completion(prompt, model="gpt-4", temperature=0, top_p=1.0, max_tokens=1024, json_output=False):
    try:
        output_json_structure = {"type": "json_object"} if json_output else None
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format=output_json_structure
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting completion: {str(e)}")
        return None

# Alternative method to get completion by messages
def get_completion_by_messages(messages, model="gpt-4", temperature=0, top_p=1.0, max_tokens=1024):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting completion by messages: {str(e)}")
        return None

# Helper function to count tokens in text
def count_tokens(text):
    try:
        encoding = tiktoken.encoding_for_model('gpt-4')
        return len(encoding.encode(text))
    except Exception as e:
        st.error(f"Error counting tokens: {str(e)}")
        return 0

# Count tokens from a list of messages
def count_tokens_from_message(messages):
    try:
        encoding = tiktoken.encoding_for_model('gpt-4')
        value = ' '.join([x.get('content') for x in messages])
        return len(encoding.encode(value))
    except Exception as e:
        st.error(f"Error counting message tokens: {str(e)}")
        return 0

# Define URLs to search for relevant information
websites = [
  "https://www.cpf.gov.sg/member/infohub/cpf-clarifies/policy-faqs/why-do-i-need-to-pay-interest-on-cpf-used-for-housing-after-property-sale",
"https://www.cpf.gov.sg/member/infohub/news/news-releases/cpf-members-to-enjoy-lower-premiums-for-home-protection-insurance",
"https://www.cpf.gov.sg/member/infohub/news/news-releases/cpf-members-to-enjoy-lower-premiums-for-home-protection-insurance-26-june-2018",
"https://www.cpf.gov.sg/member/infohub/news/news-releases/over-760000-cpf-members-to-receive-premium-rebates-under-home-protection-scheme",
"https://www.cpf.gov.sg/member/infohub/news/news-releases/cpf-board-awards-tender-on-sale-of-building-at-79-robinson-road-to-southernwood-property-pte-ltd",
"https://www.cpf.gov.sg/member/infohub/news/news-releases/premium-rebates-for-cpf-members-under-home-protection-scheme",
"https://www.cpf.gov.sg/member/infohub/news/forum-replies/eligibility-for-home-insurance-is-reassessed-in-certain-cases",
"https://www.cpf.gov.sg/member/infohub/news/cpf-related-announcements/more-flexibility-to-buy-a-home-for-life-while-safeguarding-retir",
"https://www.cpf.gov.sg/member/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics",
"https://www.cpf.gov.sg/member/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/cumulative-cpf-savings-withdrawn-for-housing",
"https://www.cpf.gov.sg/member/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/home-protection-scheme-participation",
"https://www.cpf.gov.sg/member/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/home-protection-scheme-claims",
"https://www.cpf.gov.sg/member/infohub/reports-and-statistics/cpf-trends/home-financing",
"https://www.cpf.gov.sg/member/infohub/educational-resources/property-purchase-in-a-pandemic",
"https://www.cpf.gov.sg/member/infohub/educational-resources/financially-savvy-budgeting-tips-for-your-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/hdb-flat-eligibility-letter-what-to-know",
"https://www.cpf.gov.sg/member/infohub/educational-resources/3-benefits-of-the-home-protection-scheme",
"https://www.cpf.gov.sg/member/infohub/educational-resources/3-differences-between-hdb-loan-and-bank-loan",
"https://www.cpf.gov.sg/member/infohub/educational-resources/sales-proceeds-after-selling-your-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/protect-your-home-insurance-for-your-hdb-flat",
"https://www.cpf.gov.sg/member/infohub/educational-resources/make-work-from-home-work-for-you",
"https://www.cpf.gov.sg/member/infohub/educational-resources/keep-your-family-close-when-choosing-your-next-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/roll-smoothly-into-your-hdb-resale-flat-in-4-steps",
"https://www.cpf.gov.sg/member/infohub/educational-resources/how-to-avoid-regret-when-buying-your-dream-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/easy-tips-to-freshen-up-your-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/using-cpf-to-budget-for-house-and-renovations",
"https://www.cpf.gov.sg/member/infohub/educational-resources/a-heart-decision-buying-your-first-home",
"https://www.cpf.gov.sg/member/infohub/educational-resources/hdb-option-fee-and-housing-expenses-you-should-know",
"https://www.cpf.gov.sg/member/infohub/educational-resources/home-improvement-programme-what-to-know",
"https://www.cpf.gov.sg/member/infohub/be-ready/budget-for-my-home",
"https://www.cpf.gov.sg/member/ds/dashboards/home-ownership",
"https://www.cpf.gov.sg/member/home-ownership",
"https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home",
"https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home/considerations-when-using-cpf-to-buy-property",
"https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home/apply-to-use-cpf-for-your-property",
"https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home/cpf-refund-when-selling-or-transferring-property",
"https://www.cpf.gov.sg/member/home-ownership/using-your-cpf-to-buy-a-home/retain-20000-in-your-oa-if-you-are-taking-a-housing-loan",
"https://www.cpf.gov.sg/member/home-ownership/protecting-against-losing-your-home",
"https://www.cpf.gov.sg/member/home-ownership/protecting-against-losing-your-home/claiming-under-the-home-protection-scheme",
"https://www.cpf.gov.sg/member/home-ownership/protecting-against-losing-your-home/single-premium-home-protection-scheme-cover",
"https://www.cpf.gov.sg/member/home-ownership/plan-your-housing-journey",
"https://www.cpf.gov.sg/member/home-ownership/plan-your-housing-journey/upgrading-your-home",
"https://www.cpf.gov.sg/member/home-ownership/plan-your-housing-journey/upgrading-your-home/housing-case-study",
"https://www.cpf.gov.sg/member/tnc/information-for-exemption-from-home-protection-scheme",
"https://www.cpf.gov.sg/member/tnc/important-notes-on-home-protection-scheme",
"https://www.cpf.gov.sg/member/plan-with-cpf/home-ownership-planning",
"https://www.cpf.gov.sg/employer/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics",
"https://www.cpf.gov.sg/employer/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/cumulative-cpf-savings-withdrawn-for-housing",
"https://www.cpf.gov.sg/employer/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/home-protection-scheme-participation",
"https://www.cpf.gov.sg/employer/infohub/reports-and-statistics/cpf-statistics/home-ownership-statistics/home-protection-scheme-claims",
"https://www.cpf.gov.sg/employer/infohub/reports-and-statistics/cpf-trends/home-financing"
]

# Fetch webpage content
def fetch_webpage_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        st.warning(f"Error fetching content from {url}: {str(e)}")
        return ""

# Identify relevant URL based on user message
def identify_relevant_url(user_message):
    return [url for url in websites if user_message.lower() in url.lower()]

# Get relevant content from URLs
def get_relevant_content_from_urls(urls):
    content_list = []
    for url in urls:
        content = fetch_webpage_content(url)
        if content:
            content_list.append({"url": url, "content": content})
    return content_list

# Generate response based on content and append URL for reference
def generate_response_based_on_content(user_message, content_list):
    if not content_list:
        return "I couldn't find relevant information for your query. Please try rephrasing your question."
    
    delimiter = "####"
    system_message = f"""
    Using the relevant information extracted from the websites, \
    answer the customer's question. Follow the query in the format below:

    User Query: {delimiter}{user_message}{delimiter}
    Website Content: {content_list}

    Respond with the information relevant to the user query. Ensure \
    responses are factually accurate and provide details useful for decision-making.
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_message}{delimiter}"}
    ]
    response = get_completion_by_messages(messages)
    
    if response:
        urls_used = [item["url"] for item in content_list]
        urls_text = "\n".join([f"For more detailed information, please visit {url}" for url in urls_used])
        return f"{response}\n\n{urls_text}"
    else:
        return "I apologize, but I encountered an error processing your request. Please try again."

# Main function to process user message
def process_user_message(user_input):
    with st.spinner('Processing your query...'):
        relevant_urls = identify_relevant_url(user_input)
        if not relevant_urls:
            return "I couldn't find any relevant information sources for your query. Please try rephrasing your question."
        
        relevant_content = get_relevant_content_from_urls(relevant_urls)
        return generate_response_based_on_content(user_input, relevant_content)

# Streamlit configuration and UI
st.set_page_config(
    layout="centered",
    page_title="Unified Information Hub",
    page_icon="🌐"
)

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

st.title("CPF Housing Information Hub")

# Information Section
st.sidebar.header("About Us")
st.sidebar.info("This application aggregates data from trusted sources from CPF Website to provide consolidated guidance. It personalizes responses based on the input query, enhancing user experience.")

st.sidebar.header("Methodology")
st.sidebar.write(
    """
    Our approach involves gathering, analyzing, and providing insights by leveraging state-of-the-art language models and embedding techniques. All responses are sourced from reliable public repositories.
    """
)

# Streamlit form for user input
st.write("### Ask Your Question")
st.write("Get tailored guidance by entering your query below:")

# Form for User Input
with st.form(key="query_form"):
    user_prompt = st.text_area(
        "Enter your prompt here:",
        height=100,
        placeholder="e.g., Why do I need to pay interest on CPF used for housing after property sale?"
    )
    submit_button = st.form_submit_button("Submit")

    if submit_button and user_prompt:
        try:
            response = process_user_message(user_prompt)
            
            # Add to conversation history
            st.session_state.conversation_history.append({
                "question": user_prompt,
                "answer": response
            })
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Display conversation history
if st.session_state.conversation_history:
    st.write("### Previous Questions and Answers")
    for item in reversed(st.session_state.conversation_history):
        with st.expander(f"Q: {item['question'][:100]}..."):
            st.write("Question:", item["question"])
            st.write("Answer:", item["answer"])

# Footer
st.write("---")
st.caption("Powered by OpenAI and Streamlit")