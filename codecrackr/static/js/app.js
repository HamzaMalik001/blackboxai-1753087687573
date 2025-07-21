// CodeCrackr Frontend JavaScript

// Initialize Mermaid diagrams
document.addEventListener('DOMContentLoaded', function() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            themeVariables: {
                primaryColor: '#3B82F6',
                primaryTextColor: '#1F2937',
                primaryBorderColor: '#6B7280',
                lineColor: '#6B7280',
                secondaryColor: '#F3F4F6',
                tertiaryColor: '#FFFFFF'
            },
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            }
        });
    }
});

// Utility functions
const Utils = {
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format time
    formatTime: function(seconds) {
        if (seconds < 60) return seconds + 's';
        if (seconds < 3600) return Math.floor(seconds / 60) + 'm';
        return Math.floor(seconds / 3600) + 'h ' + Math.floor((seconds % 3600) / 60) + 'm';
    },

    // Copy to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300 transform translate-x-full`;
        
        const colors = {
            info: 'bg-blue-500 text-white',
            success: 'bg-green-500 text-white',
            warning: 'bg-yellow-500 text-white',
            error: 'bg-red-500 text-white'
        };
        
        toast.className += ' ' + colors[type];
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    },

    // Debounce function
    debounce: function(func, wait) {
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
};

// File tree functionality
class FileTree {
    constructor(container) {
        this.container = container;
        this.init();
    }

    init() {
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('tree-toggle')) {
                this.toggleNode(e.target);
            }
        });
    }

    toggleNode(toggle) {
        const node = toggle.parentElement;
        const children = node.nextElementSibling;
        
        if (children && children.classList.contains('tree-children')) {
            const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
            toggle.setAttribute('aria-expanded', !isExpanded);
            children.style.display = isExpanded ? 'none' : 'block';
            toggle.textContent = isExpanded ? '▶' : '▼';
        }
    }

    renderTree(data, container) {
        const ul = document.createElement('ul');
        ul.className = 'tree-list';
        
        for (const [name, item] of Object.entries(data)) {
            const li = document.createElement('li');
            
            if (item.type === 'directory') {
                li.innerHTML = `
                    <div class="tree-item">
                        <span class="tree-toggle" aria-expanded="false">▶</span>
                        <span class="tree-icon">📁</span>
                        <span class="tree-name">${name}</span>
                    </div>
                `;
                
                if (item.children && Object.keys(item.children).length > 0) {
                    const childUl = this.renderTree(item.children);
                    childUl.className = 'tree-children ml-4 hidden';
                    li.appendChild(childUl);
                }
            } else {
                li.innerHTML = `
                    <div class="tree-item">
                        <span class="tree-icon">📄</span>
                        <span class="tree-name">${name}</span>
                        <span class="tree-size text-sm text-gray-500">${Utils.formatFileSize(item.size)}</span>
                    </div>
                `;
            }
            
            ul.appendChild(li);
        }
        
        return ul;
    }
}

// Progress tracking
class ProgressTracker {
    constructor(taskId, onComplete, onError) {
        this.taskId = taskId;
        this.onComplete = onComplete;
        this.onError = onError;
        this.interval = null;
        this.maxAttempts = 300;
        this.attempts = 0;
    }

    start() {
        this.interval = setInterval(() => {
            this.checkStatus();
        }, 1000);
    }

    async checkStatus() {
        try {
            const response = await fetch(`/status/${this.taskId}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get status');
            }

            this.updateProgress(data);

            if (data.status === 'completed') {
                this.complete(data);
            } else if (data.status === 'failed') {
                this.fail(data.error);
            }

            this.attempts++;
            if (this.attempts >= this.maxAttempts) {
                this.fail('Analysis timed out');
            }

        } catch (error) {
            this.fail(error.message);
        }
    }

    updateProgress(data) {
        const progressBar = document.getElementById('progress-bar');
        const progressPercent = document.getElementById('progress-percent');
        const progressStatus = document.getElementById('progress-status');
        const progressMessage = document.getElementById('progress-message');

        if (progressBar) {
            progressBar.style.width = data.progress + '%';
        }
        if (progressPercent) {
            progressPercent.textContent = data.progress + '%';
        }
        if (progressStatus) {
            progressStatus.textContent = data.status.replace('_', ' ').toUpperCase();
        }
        if (progressMessage) {
            progressMessage.textContent = data.message;
        }
    }

    complete(data) {
        clearInterval(this.interval);
        if (this.onComplete) {
            this.onComplete(data);
        }
    }

    fail(error) {
        clearInterval(this.interval);
        if (this.onError) {
            this.onError(error);
        }
    }

    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
}

// Search functionality
class SearchManager {
    constructor(input, resultsContainer) {
        this.input = input;
        this.resultsContainer = resultsContainer;
        this.init();
    }

    init() {
        this.input.addEventListener('input', Utils.debounce((e) => {
            this.search(e.target.value);
        }, 300));
    }

    async search(query) {
        if (!query.trim()) {
            this.clearResults();
            return;
        }

        // Implement search logic here
        // This would search through files, content, etc.
        console.log('Searching for:', query);
    }

    clearResults() {
        this.resultsContainer.innerHTML = '';
    }

    displayResults(results) {
        this.resultsContainer.innerHTML = results.map(result => `
            <div class="search-result p-3 border-b hover:bg-gray-50">
                <div class="font-medium">${result.title}</div>
                <div class="text-sm text-gray-600">${result.preview}</div>
            </div>
        `).join('');
    }
}

// Export functionality
class ExportManager {
    static async exportMarkdown(tutorial) {
        const markdown = this.generateMarkdown(tutorial);
        this.downloadFile(markdown, 'tutorial.md', 'text/markdown');
    }

    static generateMarkdown(tutorial) {
        let markdown = `# ${tutorial.metadata.repository_name} Tutorial\n\n`;
        markdown += `Generated on: ${new Date(tutorial.metadata.generated_at).toLocaleString()}\n\n`;
        
        // Add overview
        if (tutorial.overview) {
            markdown += `## Overview\n\n${tutorial.overview.overview || 'No overview available'}\n\n`;
        }

        // Add tutorial sections
        tutorial.tutorial_sections.forEach(section => {
            markdown += `## ${section.title}\n\n`;
            markdown += `${section.description}\n\n`;
            markdown += `${section.content}\n\n`;
        });

        return markdown;
    }

    static downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Collapsible sections
class CollapsibleManager {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('collapsible-toggle')) {
                this.toggle(e.target);
            }
        });
    }

    toggle(button) {
        const content = button.nextElementSibling;
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        
        button.setAttribute('aria-expanded', !isExpanded);
        content.classList.toggle('expanded');
        
        // Update icon
        const icon = button.querySelector('.toggle-icon');
        if (icon) {
            icon.textContent = isExpanded ? '▶' : '▼';
        }
    }
}

// Code highlighting (if needed)
class CodeHighlighter {
    static highlight(element) {
        // This would integrate with a syntax highlighter
        // For now, just add line numbers
        const code = element.textContent;
        const lines = code.split('\n');
        const numberedLines = lines.map((line, index) => 
            `<span class="line-number">${index + 1}</span>${line}`
        ).join('\n');
        
        element.innerHTML = numberedLines;
        element.classList.add('highlighted');
    }
}

// Initialize components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize collapsible sections
    new CollapsibleManager();

    // Initialize search if search input exists
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    if (searchInput && searchResults) {
        new SearchManager(searchInput, searchResults);
    }

    // Initialize file tree if container exists
    const fileTreeContainer = document.getElementById('file-tree');
    if (fileTreeContainer) {
        new FileTree(fileTreeContainer);
    }

    // Add copy buttons to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-btn absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 text-white rounded';
        button.textContent = 'Copy';
        button.onclick = () => {
            Utils.copyToClipboard(block.textContent);
        };
        
        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(button);
    });
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    Utils.showToast('An error occurred. Please try again.', 'error');
});

// Handle offline/online status
window.addEventListener('online', () => {
    Utils.showToast('Back online!', 'success');
});

window.addEventListener('offline', () => {
    Utils.showToast('You are offline. Some features may not work.', 'warning');
});

// Export for global use
window.CodeCrackr = {
    Utils,
    ProgressTracker,
    ExportManager,
    SearchManager,
    FileTree,
    CollapsibleManager,
    CodeHighlighter
};
