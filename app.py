from flask import Flask, render_template, session, g
import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import yaml
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key_123')

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

def init_session():
    """Initialize session if needed"""
    if not getattr(g, 'initialized', False):
        session.clear()
        g.initialized = True
        print("Initialized new application session")

@app.before_request
def before_request():
    init_session()

def get_site_context():
    """Get or initialize the site context from session"""
    try:
        # Load current site configuration
        with open('config/site_config.yaml', 'r') as file:
            current_site_config = yaml.safe_load(file)['site']
        
        # Always generate new site context on first request after startup
        if 'app_initialized' not in session:
            session.clear()
            session['app_initialized'] = True
            print("First request - generating fresh site context")
        # Check if site type has changed
        elif 'site_config' in session and session['site_config']['type'] != current_site_config['type']:
            print(f"Site type changed from {session['site_config']['type']} to {current_site_config['type']}")
            session.clear()
            session['app_initialized'] = True
        
        if 'site_context' not in session:
            print("Generating new site context...")
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a {current_site_config['theme']['content_style']}. Design an engaging and user-friendly {current_site_config['type']} structure."
                    },
                    {
                        "role": "user", 
                        "content": f"""
                        Create a new JSON structure for a {current_site_config['type']}.
                        Primary topics to cover: {', '.join(current_site_config['theme']['primary_topics'])}
                        The home page ('/') must be included.
                        
                        For each page, specify:
                        {{
                            "pages": {{
                                "page_name": {{
                                    "path": "/path",
                                    "title": "Page Title",
                                    "description": "Brief description of the page purpose"
                                }}
                            }}
                        }}
                        
                        Be creative but practical. Include pages that would make sense for a {current_site_config['type']}.
                        Keep the total number of pages between 4-6 for good navigation experience.
                        Make sure all paths start with '/'.
                        
                        IMPORTANT: Generate a completely new structure specific to a {current_site_config['type']}.
                        """
                    }
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            print(f"\nChatGPT site context response:\n{content}\n")
            
            session['site_context'] = content
            session['site_config'] = current_site_config
        
        return session['site_context'], session['site_config']
        
    except Exception as e:
        print(f"Error generating site context: {e}")
        return "{}", current_site_config

def get_navigation_history():
    """Get the navigation history from session"""
    if 'nav_history' not in session:
        session['nav_history'] = []
    return session['nav_history']

def update_navigation_history(path, content):
    """Update the navigation history in session"""
    try:
        if not isinstance(path, str):
            path = str(path) if path is not None else '/'
        if not isinstance(content, str):
            content = str(content) if content is not None else ''
            
        nav_history = get_navigation_history()
        nav_history.append({
            'path': path,
            'content': content[:200] + '...' if content else ''
        })
        session['nav_history'] = nav_history[-5:]  # Keep only last 5 entries
        
    except Exception as e:
        print(f"Error in update_navigation_history: {e}")
        print(f"Path type: {type(path)}, Content type: {type(content)}")
        print(f"Path: {path}, Content preview: {str(content)[:50]}")

def get_unsplash_image(query, width, height):
    """Get a random image URL from Unsplash based on query"""
    try:
        # Use Unsplash API directly
        headers = {
            'Authorization': f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"
        }
        response = requests.get(
            f"https://api.unsplash.com/photos/random",
            headers=headers,
            params={
                'query': query,
                'orientation': 'landscape'
            }
        )
        if response.status_code == 200:
            photo_data = response.json()
            return f"{photo_data['urls']['raw']}&w={width}&h={height}&fit=crop"
        else:
            print(f"Error from Unsplash API: {response.status_code}")
            return f"https://via.placeholder.com/{width}x{height}?text={query}"
    except Exception as e:
        print(f"Error getting Unsplash image: {e}")
        return f"https://via.placeholder.com/{width}x{height}?text={query}"

def generate_content(path):
    """Generate page content using ChatGPT"""
    try:
        if not isinstance(path, str):
            path = str(path) if path is not None else '/'
            
        print(f"\ngenerate_content received path: {path} (type: {type(path)})")
        
        nav_history = get_navigation_history()
        site_context, site_config = get_site_context()
        
        if not site_config:
            raise ValueError("Site configuration is missing")

        # Pre-fetch some image URLs for the template
        hero_image = get_unsplash_image(site_config['theme']['image_subjects'][0], 1600, 900)
        featured_image = get_unsplash_image(site_config['type'], 800, 600)
        preview_image = get_unsplash_image(site_config['theme']['primary_topics'][0], 800, 500)
            
        # Create history text only if there is history
        history_context = ""
        if nav_history:
            history_items = []
            for item in nav_history:
                try:
                    history_items.append(f"- {item.get('path', '/')}: {item.get('content', '')[:200]}")
                except Exception as e:
                    print(f"Error processing history item: {e}")
            history_context = "\n\nNavigation history:\n" + "\n".join(history_items)
        
        sections_info = "\n".join([
            f"- {section['name']}: Show {section['count']} {section['type']} items"
            for section in site_config['theme']['sections']
        ])
        
        user_prompt = f"""
        You are managing a {site_config['type']}. The current site structure is:
        {site_context}

        Site description: {site_config['description']}
        Primary topics: {', '.join(site_config['theme']['primary_topics'])}
        Content style: {site_config['theme']['content_style']}

        Current page path: {path}
        {history_context}

        Please generate two parts:
        1. Navigation menu (<nav> element)
        - Include links to all available pages from the site structure
        - Highlight the current page ({path})
        - Keep it clean and semantic
        - Use class="active" for the current page link
        - Always include a home page link ('/')
        - Return raw HTML without any markdown formatting or code blocks
        
        2. Main content
        For the home page ('/'):
        - Start with a featured hero image using: <img src="{hero_image}" alt="Featured Image" class="featured-image">
        - Create an engaging welcome section with a compelling headline
        - Include these sections:
        {sections_info}
        - For each featured item, include a relevant image using: <img src="{featured_image}" alt="[Description]" class="destination-image">
        - For each preview, include a topic-specific image using: <img src="{preview_image}" alt="[Description]" class="article-preview-image">
        - Include a call-to-action to explore more content
        
        For other pages:
        - Use the provided image URLs with appropriate alt text
        - Generate content appropriate for the current path
        - Write in the style of {site_config['theme']['content_style']}
        - Add specific details and examples
        
        Follow these styling guidelines:
        * Use semantic HTML5 elements
        * Start with a single <h1> title
        * Use <h2> for section headings
        * Organize content in clear sections
        * Use <p> tags for paragraphs
        * Use <ul> or <ol> for lists
        * Always wrap images and related content in article tags
        * Keep HTML structure clean and consistent
        
        IMPORTANT:
        - Use the provided image URLs
        - Return raw HTML without any markdown formatting, code blocks, or ```html tags
        - Do not include any backticks (```) in your response
        
        Return both parts separated by <!-- CONTENT_SPLIT -->
        """
        
        print(f"\nSending prompt to ChatGPT:\n{user_prompt}\n")
        
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are managing a {site_config['type']}. Generate consistent and coherent content as a {site_config['theme']['content_style']}."
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        full_response = response.choices[0].message.content
        print(f"\nChatGPT content response:\n{full_response}\n")
        
        try:
            nav_content, main_content = full_response.split('<!-- CONTENT_SPLIT -->')
        except ValueError as e:
            print(f"Error splitting response: {e}")
            print(f"Full response: {full_response}")
            nav_content = "<nav><a href='/'>Home</a></nav>"
            main_content = "<h1>Error processing content</h1><p>The response format was incorrect.</p>"
        
        # Only update history if we successfully generated content
        update_navigation_history(path, main_content)
        
        return nav_content.strip(), main_content.strip()
        
    except Exception as e:
        print(f"Error in generate_content: {e}")
        print(f"Path: {path} (type: {type(path)})")
        return (
            "<nav><a href='/'>Home</a></nav>",
            f"<h1>Error generating content</h1><p>Details: {str(e)}</p>"
        )

@app.route('/')
@app.route('/<path>')
def serve_page(path=None):
    try:
        path = '/' if path is None else f'/{path.strip("/")}'
        print(f"serve_page received path: {path}")
        
        nav_content, main_content = generate_content(path)
        
        # Get current site configuration for the template
        with open('config/site_config.yaml', 'r') as file:
            site_config = yaml.safe_load(file)['site']
        
        return render_template('base.html',
                             site_name=site_config['name'],  # Use name from config
                             nav_content=nav_content,
                             content=main_content)
    except Exception as e:
        print(f"Error in serve_page: {e}")
        return f"Server error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True) 