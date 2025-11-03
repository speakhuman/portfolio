/**
 * @fileoverview Blog functionality including navigation, post loading, and modal handling
 * @version 1.0.0
 * @author Arif Furqon
 * @description This file contains all JavaScript functionality for the blog, including
 * security measures (XSS protection), navigation handling, post loading, and modal interactions.
 * Accessibility features are implemented throughout for keyboard navigation and screen readers.
 */

/**
 * Basic HTML sanitizer to prevent XSS attacks
 * @param {string} html - The HTML string to sanitize
 * @returns {string} Sanitized HTML with all tags removed
 */
function sanitizeHTML(html) {
  // Create a new div element
  const tempDiv = document.createElement('div');
  // Set its content to the HTML we want to sanitize
  tempDiv.textContent = html;
  // Return the sanitized content
  return tempDiv.innerHTML;
}

/**
 * Advanced HTML sanitizer that allows certain safe tags
 * @param {string} html - The HTML string to sanitize
 * @returns {string} Sanitized HTML with only allowed tags and attributes
 */
function sanitizeHTMLAllowTags(html) {
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  
  // Define allowed tags and attributes
  const allowedTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'b', 'i', 'strong', 'em', 'a', 'pre', 'code', 'ul', 'ol', 'li'];
  const allowedAttributes = {
    'a': ['href', 'title', 'target']
  };
  
  /**
   * Helper function to clean a DOM node
   * @param {Node} node - The DOM node to clean
   */
  function cleanNode(node) {
    // If it's not an element node, keep it as is
    if (node.nodeType !== 1) return;
    
    // If it's not an allowed tag, replace it with its text content
    if (!allowedTags.includes(node.tagName.toLowerCase())) {
      const text = document.createTextNode(node.textContent);
      node.parentNode.replaceChild(text, node);
      return;
    }
    
    // Remove all attributes except allowed ones
    const attributes = Array.from(node.attributes);
    attributes.forEach(attr => {
      const tagName = node.tagName.toLowerCase();
      const attrName = attr.name.toLowerCase();
      
      // Check if this attribute is allowed for this tag
      const allowedAttrsForTag = allowedAttributes[tagName] || [];
      if (!allowedAttrsForTag.includes(attrName)) {
        node.removeAttribute(attr.name);
      }
      
      // Special handling for href attributes to prevent javascript: URLs
      if (attrName === 'href') {
        const value = attr.value.toLowerCase().trim();
        if (value.startsWith('javascript:') || value.startsWith('data:')) {
          node.removeAttribute(attr.name);
        }
      }
    });
    
    // Clean all child nodes recursively
    Array.from(node.childNodes).forEach(cleanNode);
  }
  
  // Clean the entire content
  Array.from(tempDiv.childNodes).forEach(cleanNode);
  
  return tempDiv.innerHTML;
}

// Store posts data globally
let postsData = []; // Initialize as empty array, will be populated from posts.json

/**
 * Fetch posts data from JSON file using async/await
 */
async function fetchPosts() {
    try {
        const response = await fetch('posts.json');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        postsData = data.posts; // Store posts from JSON
        loadPosts(); // Load posts after data is fetched
    } catch (error) {
        console.error('Error loading posts:', error);
        // Show error message to user
        const container = document.getElementById('posts-container');
        container.innerHTML = '<p>Sorry, there was an error loading the posts. Please try again later.</p>';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Load posts data
    fetchPosts();

    // Get all navigation links
    const navLinks = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    /**
     * Set up navigation between sections
     * Implements accessible navigation with proper focus management
     */
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault(); // Prevent default anchor behavior
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Show the corresponding section
            const targetId = link.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.classList.add('active');
                
                // Update URL hash without scrolling
                history.pushState(null, null, `#${targetId}`);
                
                // Set focus to the section for accessibility
                targetSection.setAttribute('tabindex', '-1');
                targetSection.focus();
                targetSection.removeAttribute('tabindex');
            }
        });
    });
    
    /**
     * Handle deep linking via URL hash on page load
     * Ensures correct section is shown when page is loaded with a hash
     */
    if (location.hash) {
        const targetId = location.hash.substring(1);
        const targetLink = document.querySelector(`.nav-btn[data-target="${targetId}"]`);
        if (targetLink) {
            targetLink.click();
        }
    }
    
    // Modal close handlers
    // Close button
    document.querySelector('.modal-close').addEventListener('click', closeModal);
    
    // Click outside to close
    document.getElementById('post-modal').addEventListener('click', (e) => {
        if (e.target.id === 'post-modal') {
            closeModal();
        }
    });
    
    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
    
    // We'll set up focus trapping when the modal is opened instead of here
    // This ensures we have the correct focusable elements after content is loaded
});

/**
 * Load and display blog posts from the postsData array
 * Implements progressive enhancement with animations and accessibility features
 */
function loadPosts() {
  const container = document.getElementById('posts-container');
  
  // Add ARIA live region for screen readers to announce content changes
  container.setAttribute('aria-live', 'polite');
  
  // Clear container first
  container.innerHTML = '';
  
  // Create post elements
  postsData.forEach(post => {
    const postDiv = document.createElement('div');
    postDiv.className = 'post-preview';
    
    // Format date
    const date = new Date(post.date);
    const formattedDate = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
    
    // Build post HTML with sanitized content to prevent XSS
    postDiv.innerHTML = `
      <div class="post-header">
        <span class="date">${sanitizeHTML(formattedDate)}</span>
        <h3>${sanitizeHTML(post.title)}</h3>
      </div>
      <p>${sanitizeHTML(post.excerpt)}</p>
      <div class="post-footer">
        <p class="read-time">${sanitizeHTML(post.readTime)}</p>
        <a href="#" class="read-more" data-post-id="${post.id}" aria-label="Read more about ${sanitizeHTML(post.title)}">Read More</a>
      </div>
    `;
    
    container.appendChild(postDiv);
  });
  
  // Add staggered animation after posts are added
  // Animation respects prefers-reduced-motion via CSS
  setTimeout(() => {
    document.querySelectorAll('.post-preview').forEach((post, index) => {
      setTimeout(() => {
        post.style.opacity = '1';
        post.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }, 50);
  
  // Add click handlers for "Read More" links
  addReadMoreHandlers();
}

/**
 * Add event listeners to all "Read More" links
 * Sets up click handlers to open the full post in a modal
 */
function addReadMoreHandlers() {
  const readMoreLinks = document.querySelectorAll('.read-more');
  
  readMoreLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const postId = parseInt(link.dataset.postId);
      openPost(postId);
    });
  });
}

/**
 * Store the element that had focus before opening the modal
 * Used to restore focus when modal is closed (for accessibility)
 * @type {Element|null}
 */
let lastFocusedElement = null;

/**
 * Open a post in the modal dialog
 * @param {number} postId - The ID of the post to open
 */
function openPost(postId) {
  const post = postsData.find(p => p.id === postId);
  if (!post) {
    console.error(`Post with ID ${postId} not found`);
    return;
  }
  
  // Store the current focus for later restoration
  lastFocusedElement = document.activeElement;
  
  const modal = document.getElementById('post-modal');
  if (!modal) {
    console.error('Modal element not found');
    return;
  }
  
  // Update ARIA attributes for accessibility
  modal.setAttribute('aria-hidden', 'false');
  const date = new Date(post.date);
  const formattedDate = date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
  
  // Populate modal
  document.getElementById('modal-date').textContent = formattedDate;
  document.getElementById('modal-title').textContent = sanitizeHTML(post.title);
  document.getElementById('modal-read-time').textContent = sanitizeHTML(post.readTime);
  document.getElementById('modal-content').innerHTML = sanitizeHTMLAllowTags(post.content);
  
  // Show modal
  modal.classList.add('active');
  document.body.style.overflow = 'hidden'; // Prevent scrolling
  
  // Set up focus trapping now that the modal content is populated
  setupModalFocusTrapping(modal);
  
  // Focus the close button for keyboard accessibility
  setTimeout(() => {
    const closeButton = document.querySelector('.modal-close');
    if (closeButton) {
      closeButton.focus();
    }
  }, 100);
}

/**
 * Set up focus trapping for the modal
 * This is called when the modal is opened to ensure we have the correct focusable elements
 * @param {HTMLElement} modal - The modal element
 */
/**
 * Handle tab key navigation within the modal for focus trapping
 * @param {Event} e - The keyboard event
 * @param {Element} firstFocusableElement - The first focusable element in the modal
 * @param {Element} lastFocusableElement - The last focusable element in the modal
 */
function handleTabKey(e, firstFocusableElement, lastFocusableElement) {
  if (e.key === 'Tab') {
    // If shift + tab and focus is on first element, move to last
    if (e.shiftKey && document.activeElement === firstFocusableElement) {
      e.preventDefault();
      lastFocusableElement.focus();
    }
    // If tab and focus is on last element, move to first
    else if (!e.shiftKey && document.activeElement === lastFocusableElement) {
      e.preventDefault();
      firstFocusableElement.focus();
    }
  }
}

function setupModalFocusTrapping(modal) {
  const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
  
  if (focusableElements.length === 0) {
    console.warn('No focusable elements found in modal');
    return;
  }
  
  const firstFocusableElement = focusableElements[0];
  const lastFocusableElement = focusableElements[focusableElements.length - 1];
  
  // Remove any existing keydown event listeners to prevent duplicates
  modal.removeEventListener('keydown', modal._handleTabKey);
  
  // Create a new handler with the current focusable elements
  modal._handleTabKey = (e) => handleTabKey(e, firstFocusableElement, lastFocusableElement);
  
  // Add new event listener
  modal.addEventListener('keydown', modal._handleTabKey);
}

/**
 * Close the modal dialog and restore previous state
 * Implements accessibility best practices for modal dialogs
 */
function closeModal() {
  const modal = document.getElementById('post-modal');
  if (!modal) {
    console.error('Modal element not found when trying to close');
    return;
  }
  
  modal.classList.remove('active');
  document.body.style.overflow = ''; // Restore scrolling
  
  // Update ARIA attributes for accessibility
  modal.setAttribute('aria-hidden', 'true');
  
  // Return focus to the element that had focus before the modal was opened
  if (lastFocusedElement) {
    lastFocusedElement.focus();
  }
}