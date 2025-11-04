# Speak Human - Personal Blog

A minimalist personal blog focused on making technology more human-friendly through elegant, intuitive interfaces.

## Overview

This project is a personal blog for Arif Furqon, a Front-End Engineer. The blog features a clean, minimalist design with a focus on readability and user experience. It includes a home page with personal information and a writing section that displays blog posts loaded dynamically from a JSON file.

## Features

- **Responsive Design**: Adapts seamlessly to different screen sizes
- **Dynamic Content Loading**: Blog posts are loaded from a JSON file
- **Modal Post Viewing**: Full posts open in an accessible modal dialog
- **Accessibility Features**: 
  - Skip link for keyboard navigation
  - Proper heading hierarchy
  - ARIA attributes
  - Focus management
  - Keyboard navigation support
- **Performance Optimizations**:
  - Resource preloading
  - Non-blocking font loading
  - Optimized animations
- **Security**: XSS protection for user-generated content

## Project Structure

- `index.html` - Main HTML structure and content
- `styles.css` - CSS styling and animations
- `main.js` - JavaScript functionality for navigation, post loading, and modal handling
- `posts.json` - Blog post content in JSON format
- `server.js` - Simple Node.js server for local development

## Setup and Installation

1. Make sure you have [Node.js](https://nodejs.org/) installed
2. Clone this repository to your local machine
3. Navigate to the project directory
4. Start the local server:
   ```
   node server.js
   ```
5. Open the URL shown in the console (typically http://localhost:3000)

## Adding Blog Posts

To add a new blog post, edit the `posts.json` file and add a new entry to the `posts` array following this format:

```json
{
  "id": 4,  // Use the next available ID number
  "title": "Your Post Title",
  "date": "YYYY-MM-DD",  // ISO format date
  "excerpt": "A brief summary of your post",
  "content": "<p>Your HTML content here...</p>",  // HTML content is supported
  "readTime": "X min read"  // Estimated reading time
}
```

### Supported HTML Tags

The blog supports the following HTML tags in post content:
- Paragraphs: `<p>`
- Headings: `<h1>` through `<h6>`
- Text formatting: `<b>`, `<i>`, `<strong>`, `<em>`
- Links: `<a href="..." title="..." target="...">`
- Code: `<pre>`, `<code>`
- Lists: `<ul>`, `<ol>`, `<li>`
- Line breaks: `<br>`

## Date Formatting

Dates in the `posts.json` file should be in ISO format (YYYY-MM-DD). The JavaScript code will automatically format these dates for display using `toLocaleDateString()` with the 'en-US' locale, showing them as "MMM D, YYYY" (e.g., "Nov 4, 2025").

## Technologies Used

- HTML5
- CSS3
- Vanilla JavaScript
- Node.js (for local development server)
- Google Fonts (Inter and Roboto Mono)

## License

© speakhuman.dev
