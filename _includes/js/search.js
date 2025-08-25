// Simple Jekyll Search integration
(function() {
  'use strict';
  
  let searchData = [];
  
  // DOM elements
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  
  if (!searchInput || !searchResults) {
    return;
  }
  
  // Debounce function
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }
  
  // Load search data
  function loadSearchData() {
    fetch('/search.json')
      .then(response => response.json())
      .then(data => {
        searchData = data;
        console.log(`Načteno ${searchData.length} článků pro vyhledávání`);
      })
      .catch(error => {
        console.error('Chyba při načítání search.json:', error);
      });
  }
  
  // Search function
  function search(query) {
    query = query.toLowerCase().trim();
    
    if (query.length === 0) {
      hideResults();
      return;
    }
    
    if (query.length < 2) {
      showMessage('Zadej alespoň 2 znaky...');
      return;
    }
    
    // Simple search in title and content
    const results = searchData.filter(item => {
      const titleMatch = item.title.toLowerCase().includes(query);
      const contentMatch = item.content.toLowerCase().includes(query);
      const categoryMatch = item.category.toLowerCase().includes(query);
      const tagsMatch = item.tags.toLowerCase().includes(query);
      
      return titleMatch || contentMatch || categoryMatch || tagsMatch;
    }).slice(0, 8); // Limit results
    
    displayResults(results, query);
  }
  
  // Display search results
  function displayResults(results, query) {
    if (results.length === 0) {
      showMessage('Žádné výsledky nenalezeny');
      return;
    }
    
    const html = results.map(result => {
      const excerpt = getExcerpt(result.content, query, 100);
      const categoryName = getCategoryName(result.category);
      
      return `
        <a href="${result.url}" class="md-search-result">
          <div class="md-search-result__category">${categoryName}</div>
          <div class="md-search-result__title">${highlightQuery(result.title, query)}</div>
          <div class="md-search-result__excerpt">${highlightQuery(excerpt, query)}</div>
        </a>
      `;
    }).join('');
    
    searchResults.innerHTML = html;
    showResults();
  }
  
  // Get excerpt around search query
  function getExcerpt(content, query, maxLength) {
    const queryIndex = content.toLowerCase().indexOf(query.toLowerCase());
    
    if (queryIndex === -1) {
      return content.substring(0, maxLength) + '...';
    }
    
    const start = Math.max(0, queryIndex - maxLength / 2);
    const end = Math.min(content.length, start + maxLength);
    
    let excerpt = content.substring(start, end);
    
    if (start > 0) excerpt = '...' + excerpt;
    if (end < content.length) excerpt = excerpt + '...';
    
    return excerpt;
  }
  
  // Highlight search query in text
  function highlightQuery(text, query) {
    if (!query || query.length === 0) return text;
    
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    return text.replace(regex, '<mark style="background: var(--md-sys-color-tertiary-container); color: var(--md-sys-color-on-tertiary-container); padding: 1px 2px; border-radius: 2px;">$1</mark>');
  }
  
  // Escape regex special characters
  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  // Get human-readable category name
  function getCategoryName(category) {
    const categoryNames = {
      'mistostarosti': 'Místostarosti',
      'strategie': 'Strategie',
      'aktuality': 'Aktuality',
      'CLANKY': 'Články',
      'page': 'Stránka'
    };
    
    return categoryNames[category] || category || 'Článek';
  }
  
  // Show message in results
  function showMessage(message) {
    searchResults.innerHTML = `<div class="md-search-no-results">${message}</div>`;
    showResults();
  }
  
  // Show results container
  function showResults() {
    searchResults.classList.add('md-search-results--visible');
  }
  
  // Hide results container
  function hideResults() {
    searchResults.classList.remove('md-search-results--visible');
  }
  
  // Event listeners
  const debouncedSearch = debounce(search, 200);
  
  searchInput.addEventListener('input', function() {
    debouncedSearch(this.value);
  });
  
  searchInput.addEventListener('focus', function() {
    if (this.value.length > 1) {
      showResults();
    }
  });
  
  // Hide results when clicking outside
  document.addEventListener('click', function(e) {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      hideResults();
    }
  });
  
  // Handle keyboard navigation
  let selectedIndex = -1;
  
  searchInput.addEventListener('keydown', function(e) {
    const resultLinks = searchResults.querySelectorAll('.md-search-result');
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = Math.min(selectedIndex + 1, resultLinks.length - 1);
      updateSelection(resultLinks);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = Math.max(selectedIndex - 1, -1);
      updateSelection(resultLinks);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (selectedIndex >= 0 && resultLinks[selectedIndex]) {
        resultLinks[selectedIndex].click();
      }
    } else if (e.key === 'Escape') {
      hideResults();
      this.blur();
    }
  });
  
  // Update visual selection of results
  function updateSelection(resultLinks) {
    resultLinks.forEach((link, index) => {
      if (index === selectedIndex) {
        link.style.background = 'var(--md-sys-color-secondary-container)';
      } else {
        link.style.background = '';
      }
    });
  }
  
  // Reset selection when mouse is used
  if (searchResults) {
    searchResults.addEventListener('mouseover', function() {
      selectedIndex = -1;
      const resultLinks = this.querySelectorAll('.md-search-result');
      resultLinks.forEach(link => {
        link.style.background = '';
      });
    });
  }
  
  // Initialize
  loadSearchData();
  
})();
