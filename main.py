import os 
import base64
import random
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# Ensure set_page_config is called only once
if "page_config_set" not in st.session_state:
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    st.session_state["page_config_set"] = True

# Global dictionary to store URL usage count and emails generated
if 'url_usage' not in st.session_state:
    st.session_state['url_usage'] = {}

# Function to add background images
def add_background_images(image_paths):
    """
    Adds multiple background images to the Streamlit app using CSS with an animation loop.
    :param image_paths: List of paths to the local image files.
    """
    b64_images = []
    for image_path in image_paths:
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                b64_images.append(base64.b64encode(img_file.read()).decode())
        else:
            st.error(f"Background image not found at {image_path}")

    animation_css = ""
    for idx, b64_image in enumerate(b64_images):
        animation_css += f"""
        {idx * (100 // len(b64_images))}% {{
            background-image: url("data:image/png;base64,{b64_image}");
        }}
        """
    animation_css += f"""
        100% {{
            background-image: url("data:image/png;base64,{b64_images[0]}");
        }}
    """

    st.markdown(
        f"""
        <style>
        @keyframes background-slideshow {{
            {animation_css}
        }}

        .stApp {{
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            animation: background-slideshow 50s infinite; /* Change every 15 seconds */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


def add_title_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap'); /* Ethnocentric-like font */

        .custom-title {
            font-family: 'Orbitron', sans-serif; /* Ethnocentric-like font */
            font-size: 3rem; /* Adjust the font size */
            color: #4CAF50; /* Green text color */
            text-align: center;
            margin-top: 20px;
            animation: float 3s infinite ease-in-out, glow 3s infinite ; /* Floating and glowing animations */
        }

        /* Floating animation */
        @keyframes float {
            0%, 100% {
                transform: translateY(0); /* Start and end at the same position */
            }
            50% {
                transform: translateY(-10px); /* Move up */
            }
        }
        
        @keyframes glow-animation {
            0% {
                text-shadow: 0 0 10px #4CAF50, 0 0 20px #4CAF50, 0 0 30px #4CAF50;
            }
            100% {
                text-shadow: 0 0 20px #4CAF50, 0 0 40px #4CAF50, 0 0 60px #4CAF50;
            }
        }

        .custom-title:hover {
            color: #00FF00; /* Change text color on hover */
            text-shadow: 0 0 30px #00FF00, 0 0 60px #00FF00, 0 0 90px #00FF00; /* Stronger glow */
            animation: hover-animation 2s infinite alternate; 
        }

        </style>
        """,
        unsafe_allow_html=True,
    )



# Custom CSS for glowing and hover effects
def add_glow_and_hover_styles():
    st.markdown(
        """
        <style>

        /* Glow effect on input box */
        .stTextInput input:hover, .stTextInput input:focus {
            background: linear-gradient(45deg, #ca4adb, #2b4beb, #87ef4a, #35ccea);
            # border: 2px solid #4CAF50;  /* Green border */
            box-shadow: 0 0 45px rgba(154, 233, 57, 0.8);
        }

        /* Hover effect on buttons */
        .stButton button:hover {
            background: linear-gradient(45deg, #2b4beb, #87ef4a);
            color: white; 
            box-shadow: 0 0 55px rgba(154, 233, 57, 0.8);
        }

        /* Glow effect on generated email text */
        .stCodeBlock {
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.6);
        }

        .stCodeBlock:hover {
            border: 2px solid #4CAF50;
            box-shadow: 0 0 15px rgba(76, 175, 80, 0.9);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def calculate_email_price(email_content, usage_count):
    """
    Calculate the price of an email based on its content and usage count.
    :param email_content: The generated email content.
    :param usage_count: How many times the URL has been used.
    :return: Calculated price and a description of the price factors.
    """
    base_price = 10  # Base price in USD
    word_count = len(email_content.split())  # Number of words in the email
    complexity_factor = min(word_count / 100, 2)  # Cap complexity factor at 2 for long emails
    repeat_usage_penalty = 1 + (usage_count * 0.1)  # 10% increase per repeat usage
    price = round(base_price * complexity_factor * repeat_usage_penalty, 2)

    # Create a description of the pricing factors
    description = f"Base price: ${base_price}, word count factor: {complexity_factor:.1f}, repeat usage penalty: {repeat_usage_penalty:.1f}x."
    return price, description

def calculate_email_quality(email_content):
    """
    Calculate the quality metrics for an email (accuracy, excellence).
    :param email_content: The generated email content.
    :return: Accuracy, Excellence.
    """
    # Dummy logic for now; in a real case, this could be a model or more complex analysis
    accuracy = random.uniform(75, 95)  # Random accuracy score between 75% and 95%
    excellence = random.uniform(80, 100)  # Random excellence score between 80% and 100%
    # client_reach = random.uniform(50, 85)  # Random client reach score between 50% and 85%

    return round(accuracy, 2), round(excellence, 2)

def create_streamlit_app(llm, portfolio, clean_text):
    st.markdown('<div class="custom-title">📧 Get AI Emails to Your Most Valued Clients</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    with col1:
        url_input = st.text_input("Enter a URL:", placeholder="Enter the URL of career portal")

    with col2:
        submit_button = st.button("Submit", key="submit_button")
        
        analyze_button = st.button("Analyze", key="analyze_button")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)

                # Track the URL usage count
                if url_input in st.session_state['url_usage']:
                    st.session_state['url_usage'][url_input]["usage_count"] += 1
                else:
                    st.session_state['url_usage'][url_input] = {"usage_count": 1, "generated_emails": []}

                usage_count = st.session_state['url_usage'][url_input]["usage_count"]
                price, description = calculate_email_price(email, usage_count)

                # Calculate the quality metrics
                accuracy, excellence = calculate_email_quality(email)

                # Store generated email and its price
                st.session_state['url_usage'][url_input]["generated_emails"].append({
                    "email": email,
                    "price": price,
                    "description": description,
                    "accuracy": accuracy,
                    "excellence": excellence,
                    # "client_reach": client_reach
                })

                st.success("Email Generated:")
                st.code(email, language='markdown')
                
                # st.write(f"**Client Reach:** {client_reach}%")

        except Exception as e:
            st.error(f"An Error Occurred: {e}")

    if analyze_button:
        st.session_state['page'] = 'analyze'
        st.experimental_rerun()

def display_analysis_page():
    st.title("📊 Email Analysis")
    back_button = st.button('Back to Submit Page')
    if back_button:
        st.session_state['page'] = 'main'
        st.experimental_rerun()

    if not st.session_state.get('url_usage', {}):
        st.warning("No emails generated yet. Please use the Submit button first.")
    else:
        for url, data in st.session_state['url_usage'].items():
            usage_count = data["usage_count"]
            st.write(f"### URL: {url}")
            st.write(f"**Usage Count:** {usage_count}")
            total_price = 0
            for idx, email_data in enumerate(data["generated_emails"]):
                email = email_data["email"]
                price = email_data["price"]
                description = email_data["description"]
                accuracy = email_data["accuracy"]
                excellence = email_data["excellence"]
                # client_reach = email_data["client_reach"]
                total_price += price
                st.write(f"#### Email {idx + 1}:")
                st.code(email, language='markdown')
                st.write(f"**Price:** ${price}")
                st.write(f"**Reason:** {description}")
                st.write(f"**Accuracy:** {accuracy}%")
                st.write(f"**Excellence:** {excellence}%")
                # st.write(f"**Client Reach:** {client_reach}%")
            st.write(f"**Total Price for this URL:** ${total_price}")

# if __name__ == "__main__":
#     chain = Chain()
#     portfolio = Portfolio()

#     if 'page' not in st.session_state:
#         st.session_state['page'] = 'main'

#     if st.session_state['page'] == 'main':
#         create_streamlit_app(chain, portfolio, clean_text)
#     elif st.session_state['page'] == 'analyze':
#         display_analysis_page()

if __name__ == "__main__":

    image_paths = [
        "imgs/1.jpg",  # Replace these with your actual image paths
        "imgs/2.jpg",
        "imgs/3.jpg",
        "imgs/4.jpg",
        "imgs/5.jpg",
        "imgs/6.jpg"
    ]

    # Add the looping background images
    add_background_images(image_paths)

    # Apply custom styles for hover and glow effects
    add_glow_and_hover_styles()

    add_title_styles()

    chain = Chain()
    portfolio = Portfolio()

    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    if st.session_state['page'] == 'main':
        create_streamlit_app(chain, portfolio, clean_text)
    elif st.session_state['page'] == 'analyze':
        display_analysis_page()
