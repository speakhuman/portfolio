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
let projectsData = []; // Initialize as empty array, will be populated from projects.json
let githubCache = {}; // Cache for GitHub API responses to avoid rate limiting

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

/**
 * Fetch projects data from JSON file using async/await
 */
async function fetchProjects() {
    try {
        const response = await fetch('projects.json');
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        projectsData = data.projects; // Store projects from JSON
        loadProjects(); // Load projects after data is fetched
        setupFilters(); // Set up project filtering
    } catch (error) {
        console.error('Error loading projects:', error);
        // Show error message to user
        const container = document.getElementById('projects-container');
        if (container) {
            container.innerHTML = '<p>Sorry, there was an error loading the projects. Please try again later.</p>';
        }
    }
}

/**
 * Fetch GitHub repository data using the GitHub API
 * @param {string} repoPath - The repository path in format "username/repo"
 * @returns {Promise<Object>} - Promise resolving to repository data
 */
async function fetchGitHubData(repoPath) {
    // Check cache first to avoid hitting rate limits
    if (githubCache[repoPath] && (Date.now() - githubCache[repoPath].timestamp) < 3600000) {
        return githubCache[repoPath].data;
    }
    
    try {
        const response = await fetch(`https://api.github.com/repos/${repoPath}`);
        
        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Cache the response with a timestamp
        githubCache[repoPath] = {
            data: data,
            timestamp: Date.now()
        };
        
        return data;
    } catch (error) {
        console.error('Error fetching GitHub data:', error);
        return null;
    }
}

/**
 * Extract GitHub repository path from a GitHub URL
 * @param {string} url - The GitHub repository URL
 * @returns {string|null} - Repository path in format "username/repo" or null if invalid
 */
function extractRepoPath(url) {
    if (!url || !url.includes('github.com')) {
        return null;
    }
    
    try {
        const urlObj = new URL(url);
        // Remove leading slash and trailing .git if present
        const path = urlObj.pathname.replace(/^\//, '').replace(/\.git$/, '');
        return path;
    } catch (error) {
        console.error('Invalid GitHub URL:', error);
        return null;
    }
}

/**
 * Load and display projects
 * @param {string} filterCategory - Category to filter projects by (default: 'all')
 */
async function loadProjects(filterCategory = 'all') {
    const container = document.getElementById('projects-container');
    if (!container) return;
    
    // Clear container first
    container.innerHTML = '';
    
    // Filter projects if needed
    const filteredProjects = filterCategory === 'all'
        ? projectsData
        : projectsData.filter(project => project.category.includes(filterCategory));
    
    // Create project elements
    for (const project of filteredProjects) {
        const projectCard = document.createElement('div');
        projectCard.className = 'project-card';
        
        // Create thumbnail if available
        let thumbnailHTML = '';
        if (project.thumbnail) {
            thumbnailHTML = `<img src="${sanitizeHTML(project.thumbnail)}" alt="${sanitizeHTML(project.title)}" class="project-thumbnail">`;
        }
        
        // Create technology tags
        let techTagsHTML = '';
        if (project.technologies && project.technologies.length) {
            const tags = project.technologies.map(tech =>
                `<span class="tech-tag">${sanitizeHTML(tech)}</span>`
            ).join('');
            techTagsHTML = `<div class="technology-tags">${tags}</div>`;
        }
        
        // Try to get GitHub stats if source link is a GitHub repository
        let githubStatsHTML = '';
        if (project.links && project.links.source) {
            const repoPath = extractRepoPath(project.links.source);
            if (repoPath) {
                // Add a placeholder for GitHub stats that will be populated asynchronously
                githubStatsHTML = `
                    <div class="github-stats" data-repo="${repoPath}">
                        <div class="github-stats-loading">Loading GitHub stats...</div>
                    </div>
                `;
            }
        }
        
        // Build project card HTML
        projectCard.innerHTML = `
            ${thumbnailHTML}
            <div class="project-info">
                <h3 class="project-title">${sanitizeHTML(project.title)}</h3>
                <p class="project-description">${sanitizeHTML(project.description)}</p>
                ${techTagsHTML}
                ${githubStatsHTML}
                <div class="project-links">
                    <a href="#" class="view-project" data-project-id="${project.id}">View Details</a>
                </div>
            </div>
        `;
        
        container.appendChild(projectCard);
        
        // Fetch GitHub stats if available
        if (project.links && project.links.source) {
            const repoPath = extractRepoPath(project.links.source);
            if (repoPath) {
                loadGitHubStats(repoPath, projectCard);
            }
        }
    }
    
    // Add staggered animation
    setTimeout(() => {
        document.querySelectorAll('.project-card').forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('visible');
            }, index * 100);
        });
    }, 50);
    
    // Add click handlers for project cards
    addProjectDetailHandlers();
}

/**
 * Load GitHub stats for a repository and update the UI
 * @param {string} repoPath - The repository path in format "username/repo"
 * @param {HTMLElement} projectCard - The project card element to update
 */
async function loadGitHubStats(repoPath, projectCard) {
    const statsContainer = projectCard.querySelector(`.github-stats[data-repo="${repoPath}"]`);
    if (!statsContainer) return;
    
    try {
        const data = await fetchGitHubData(repoPath);
        if (!data) {
            statsContainer.innerHTML = '<div class="github-stats-error">GitHub stats unavailable</div>';
            return;
        }
        
        // Format the last update date
        const lastUpdated = new Date(data.updated_at);
        const formattedDate = lastUpdated.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        // Update the stats container with GitHub data
        statsContainer.innerHTML = `
            <div class="github-stats-content">
                <div class="github-stat">
                    <span class="github-stat-value">${data.stargazers_count}</span>
                    <span class="github-stat-label">Stars</span>
                </div>
                <div class="github-stat">
                    <span class="github-stat-value">${data.forks_count}</span>
                    <span class="github-stat-label">Forks</span>
                </div>
                <div class="github-stat">
                    <span class="github-stat-value">${formattedDate}</span>
                    <span class="github-stat-label">Updated</span>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading GitHub stats:', error);
        statsContainer.innerHTML = '<div class="github-stats-error">GitHub stats unavailable</div>';
    }
}

/**
 * Set up project filtering
 */
function setupFilters() {
    // Get all unique categories
    const categories = new Set();
    projectsData.forEach(project => {
        if (project.category && project.category.length) {
            project.category.forEach(cat => categories.add(cat));
        }
    });
    
    // Create filter buttons
    const filterContainer = document.querySelector('.project-filters');
    if (!filterContainer) return;
    
    categories.forEach(category => {
        const button = document.createElement('button');
        button.className = 'filter-btn';
        button.textContent = category;
        button.setAttribute('data-filter', category);
        filterContainer.appendChild(button);
    });
    
    // Add click handlers to filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Mark previously active button with was-active class
            const previousActive = document.querySelector('.filter-btn.active');
            if (previousActive) {
                previousActive.classList.add('was-active');
                // Remove was-active from other buttons
                document.querySelectorAll('.filter-btn').forEach(b => {
                    if (b !== previousActive) {
                        b.classList.remove('was-active');
                    }
                });
            }
            
            // Remove active class from all buttons
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            btn.classList.add('active');
            btn.classList.remove('was-active'); // Remove was-active if it was previously active
            
            // Filter projects
            loadProjects(btn.getAttribute('data-filter'));
        });
    });
}

/**
 * Add event listeners to project detail links
 */
function addProjectDetailHandlers() {
    const projectLinks = document.querySelectorAll('.view-project');
    
    projectLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const projectId = parseInt(link.dataset.projectId);
            openProject(projectId);
        });
    });
}

/**
 * Open project details in modal
 * @param {number} projectId - The ID of the project to open
 */
function openProject(projectId) {
    const project = projectsData.find(p => p.id === projectId);
    if (!project) {
        console.error(`Project with ID ${projectId} not found`);
        return;
    }
    
    // Store current focus for later restoration
    lastFocusedElement = document.activeElement;
    
    const modal = document.getElementById('project-modal');
    if (!modal) {
        console.error('Modal element not found');
        return;
    }
    
    // Update ARIA attributes
    modal.setAttribute('aria-hidden', 'false');
    
    // Create technology tags
    let techTagsHTML = '';
    if (project.technologies && project.technologies.length) {
        const tags = project.technologies.map(tech =>
            `<span class="tech-tag">${sanitizeHTML(tech)}</span>`
        ).join('');
        techTagsHTML = tags;
    }
    
    // Populate modal
    document.getElementById('project-modal-title').textContent = sanitizeHTML(project.title);
    document.getElementById('project-modal-technologies').innerHTML = techTagsHTML;
    document.getElementById('project-modal-content').innerHTML = sanitizeHTMLAllowTags(project.content);
    
    // Set up links
    const liveLink = document.getElementById('project-live-link');
    const sourceLink = document.getElementById('project-source-link');
    
    if (project.links && project.links.live) {
        liveLink.href = project.links.live;
        liveLink.style.display = 'inline-block';
    } else {
        liveLink.style.display = 'none';
    }
    
    if (project.links && project.links.source) {
        sourceLink.href = project.links.source;
        sourceLink.style.display = 'inline-block';
    } else {
        sourceLink.style.display = 'none';
    }
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent scrolling
    
    // Set up focus trapping
    setupModalFocusTrapping(modal);
    
    // Focus the close button
    setTimeout(() => {
        const closeButton = modal.querySelector('.modal-close');
        if (closeButton) {
            closeButton.focus();
        }
    }, 100);
}

/**
 * Very simple theme toggle functionality
 */
function initThemeToggle() {
    console.log('Theme toggle init');
    
    // Get the theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) {
        console.error('Theme toggle button not found!');
        return;
    }
    
    // Apply initial theme
    applyTheme();
    
    // Add click event listener
    themeToggle.addEventListener('click', toggleTheme);
}

/**
 * Apply the current theme based on localStorage or system preference
 */
function applyTheme() {
    const isDark = localStorage.getItem('theme') === 'dark' ||
                  (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        console.log('Applied dark theme');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        console.log('Applied light theme');
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    console.log('Toggle theme clicked');
    
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Update DOM
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Save preference
    localStorage.setItem('theme', newTheme);
    
    console.log(`Theme switched to ${newTheme}`);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');
    
    // Load posts data
    fetchPosts();
    
    // Load projects data
    fetchProjects();
    
    // Initialize theme toggle
    initThemeToggle();
    console.log('Theme toggle initialized');

    // Get all navigation links
    const navLinks = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    // Add specific handler for the logo
    const logo = document.querySelector('.logo');
    console.log('Logo element found:', logo);
    
    if (logo) {
        logo.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Logo clicked!');
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to home nav button
            const homeNavBtn = document.querySelector('.nav-btn[data-target="home"]');
            if (homeNavBtn) {
                homeNavBtn.classList.add('active');
            }
            
            // Show the home section
            const homeSection = document.getElementById('home');
            if (homeSection) {
                homeSection.classList.add('active');
                
                // Update URL hash without scrolling
                history.pushState(null, null, '#home');
                
                // Set focus to the section for accessibility
                homeSection.setAttribute('tabindex', '-1');
                homeSection.focus();
                homeSection.removeAttribute('tabindex');
            }
        });
    }
    
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
    // Post modal close handlers
    // Close button
    document.querySelector('#post-modal .modal-close').addEventListener('click', () => closeModal('post-modal'));
    
    // Click outside to close
    document.getElementById('post-modal').addEventListener('click', (e) => {
        if (e.target.id === 'post-modal') {
            closeModal('post-modal');
        }
    });
    
    // Project modal close handlers
    // Close button
    const projectModalCloseBtn = document.querySelector('#project-modal .modal-close');
    if (projectModalCloseBtn) {
        projectModalCloseBtn.addEventListener('click', () => closeModal('project-modal'));
    }
    
    // Click outside to close
    const projectModal = document.getElementById('project-modal');
    if (projectModal) {
        projectModal.addEventListener('click', (e) => {
            if (e.target.id === 'project-modal') {
                closeModal('project-modal');
            }
        });
    }
    
    // ESC key to close
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Close any open modal
            if (document.querySelector('.modal.active')) {
                const activeModalId = document.querySelector('.modal.active').id;
                closeModal(activeModalId);
            }
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
    const closeButton = modal.querySelector('.modal-close');
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
 * @param {string} modalId - The ID of the modal to close
 */
function closeModal(modalId) {
   const modal = document.getElementById(modalId);
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