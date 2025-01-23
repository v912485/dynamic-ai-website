# Dynamic GPT Site Generator

A Flask-based web application that generates dynamic websites using GPT-4 and Unsplash. The site content and structure are automatically generated based on the configuration, making it easy to create different types of websites (e.g., travel blogs, cooking sites, tech blogs) without changing the code.

## Features

- Dynamic content generation using GPT-4
- Automatic site structure creation
- Topic-specific image integration using Unsplash API
- Configurable site themes and topics
- Responsive design
- Navigation history tracking
- Clean, semantic HTML output

## Prerequisites

- Python 3.8+
- OpenAI API key
- Unsplash API access key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd website
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your-openai-key
   FLASK_SECRET_KEY=your-secret-key
   UNSPLASH_ACCESS_KEY=your-unsplash-access-key
   ```

## Configuration

The site type and content are configured in `config/site_config.yaml`. Example configurations:

### Cooking Site
```
yaml
   site:
      type: "cooking_site"
      name: "Culinary Adventures"
      description: "Exploring world cuisines and cooking techniques"
      theme:
         primary_topics:
            "recipes"
            "cooking tips"
            "ingredients"
            content_style: "passionate chef sharing culinary knowledge"
            image_subjects:
               "food"
               "cooking"
               "ingredients"
         sections:
            name: "Featured Recipes"
            type: "featured"
            count: 3
            name: "Cooking Tips"
            type: "blog_preview"
            count: 2
yaml
   site:
      type: "travel_blog"
      name: "AI Travel Blog"
      description: "A blog about travel destinations around the world"
      theme:
         primary_topics:
            "destinations"
            "travel tips"
            "adventures"
         content_style: "friendly, informative travel expert"
         image_subjects:
            "travel"
            "landscapes"
            "destinations"
         sections:
            name: "Featured Destinations"
            type: "featured"
            count: 3
            name: "Latest Travel Tips"
            type: "blog_preview"
            count: 2
```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. To change the site type:
   - Edit the `site_config.yaml` file
   - Restart the application
   - The new site will be generated with appropriate content and images

## How It Works

1. **Configuration Loading**
   - Application reads site configuration from `site_config.yaml`
   - Defines site type, structure, and content style

2. **Site Structure Generation**
   - GPT-4 creates a logical site structure based on the configuration
   - Generates appropriate pages and navigation

3. **Content Generation**
   - GPT-4 generates content for each page request
   - Content matches the site type and style
   - Maintains consistency across pages

4. **Image Integration**
   - Unsplash API provides topic-specific images
   - Images are automatically sized and positioned
   - Each image matches the content context

5. **Navigation**
   - Automatically generated based on site structure
   - Tracks user navigation history
   - Highlights current page

## Dependencies

- Flask (3.0.0): Web framework
- OpenAI (≥1.59.7): GPT-4 integration
- Requests (2.31.0): HTTP client for Unsplash API
- PyYAML (6.0.1): YAML configuration parsing
- python-dotenv (1.0.0): Environment variable management

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[MIT License](LICENSE)