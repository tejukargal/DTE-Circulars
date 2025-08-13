document.addEventListener('DOMContentLoaded', function() {
    loadCirculars();
    
    const refreshBtn = document.getElementById('refreshBtn');
    refreshBtn.addEventListener('click', function() {
        loadCirculars();
    });
    
    // Setup PDF modal
    setupPDFModal();
    
    // Setup dark mode
    setupDarkMode();
});

async function loadCirculars() {
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const circularsGrid = document.getElementById('circularsGrid');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Show loading state
    loadingDiv.style.display = 'flex';
    loadingDiv.innerHTML = `
        <div class="loading-spinner"></div>
        <div>Loading circulars...</div>
    `;
    errorDiv.style.display = 'none';
    circularsGrid.innerHTML = '';
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Loading...';
    
    try {
        const response = await fetch('/api/circulars');
        const data = await response.json();
        
        // Handle both success and fallback scenarios
        if (data.success || data.circulars.length > 0) {
            displayCirculars(data.circulars);
            
            // Show warning if using fallback data
            if (data.debug_info && data.debug_info.fallback_data) {
                showWarning('⚠️ Showing sample data - The DTE website cannot be accessed from this deployment environment');
            }
        } else {
            throw new Error(data.error || 'Failed to fetch circulars');
        }
        
    } catch (error) {
        console.error('Error fetching circulars:', error);
        showError('Failed to load circulars: ' + error.message);
    } finally {
        loadingDiv.style.display = 'none';
        refreshBtn.disabled = false;
        refreshBtn.textContent = 'Refresh';
    }
}

function displayCirculars(circulars) {
    const circularsGrid = document.getElementById('circularsGrid');
    
    if (!circulars || circulars.length === 0) {
        circularsGrid.innerHTML = '<div class="no-circulars">No circulars found</div>';
        return;
    }
    
    // Clear grid first
    circularsGrid.innerHTML = '';
    
    circulars.forEach((circular, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'circular-card';
        cardElement.style.animationDelay = `${index * 0.1}s`;
        
        const safeSubject = escapeHtml(circular.subject);
        const safeOrderNo = escapeHtml(circular.order_no || 'N/A');
        
        cardElement.innerHTML = `
            <div class="card-header">
                <div class="serial-section">
                    <span class="serial">#${circular.serial_no}</span>
                    <div class="date-order">
                        <div class="date">${formatDate(circular.date)}</div>
                        <div class="order">Order: ${safeOrderNo}</div>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <div class="circular-subject">${safeSubject}</div>
                <div class="card-actions">
                    <a href="${circular.pdf_link}" target="_blank" class="open-pdf-btn">
                        <span>🔗</span>
                        Open PDF
                    </a>
                    <button class="share-btn" onclick="shareCircular(${circular.serial_no}, '${formatDate(circular.date)}', '${safeOrderNo}', '${safeSubject.replace(/'/g, "\\'")}', '${circular.pdf_link}')">
                        <span>📤</span>
                        Share
                    </button>
                </div>
            </div>
        `;
        
        circularsGrid.appendChild(cardElement);
    });
}

function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (e) {
        return dateStr;
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function showWarning(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.innerHTML = message;
    errorDiv.style.display = 'block';
    errorDiv.style.backgroundColor = '#ff9800';
    errorDiv.style.color = 'white';
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function setupPDFModal() {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('pdfModal')) {
        const modalHTML = `
            <div id="pdfModal" class="pdf-modal">
                <div class="pdf-modal-content">
                    <div class="pdf-modal-header">
                        <div id="pdfModalTitle" class="pdf-modal-title">PDF Viewer</div>
                        <button class="close-modal" onclick="closePDFModal()">&times;</button>
                    </div>
                    <iframe id="pdfIframe" class="pdf-iframe" src=""></iframe>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    // Close modal when clicking outside
    document.getElementById('pdfModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closePDFModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.getElementById('pdfModal').style.display === 'block') {
            closePDFModal();
        }
    });
}

function openPDFModal(pdfUrl, title) {
    const modal = document.getElementById('pdfModal');
    const iframe = document.getElementById('pdfIframe');
    const modalTitle = document.getElementById('pdfModalTitle');
    
    // Set title
    modalTitle.textContent = title || 'PDF Viewer';
    
    // Set PDF source
    const decodedUrl = decodeURIComponent(pdfUrl);
    iframe.src = decodedUrl;
    
    // Show modal
    modal.style.display = 'block';
    
    // Handle iframe load error
    iframe.onload = function() {
        console.log('PDF loaded successfully');
    };
    
    iframe.onerror = function() {
        console.error('Error loading PDF');
        showError('Failed to load PDF. You can try opening it in a new tab instead.');
    };
}

function closePDFModal() {
    const modal = document.getElementById('pdfModal');
    const iframe = document.getElementById('pdfIframe');
    
    modal.style.display = 'none';
    iframe.src = '';  // Clear the iframe source to stop loading
}

function setupDarkMode() {
    // Check if dark mode is saved in localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    
    // Apply dark mode if it was previously enabled
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        updateDarkModeButton(true);
    }
    
    // Add event listener to dark mode toggle button
    const darkModeBtn = document.getElementById('darkModeBtn');
    if (darkModeBtn) {
        darkModeBtn.addEventListener('click', toggleDarkMode);
    }
}

function toggleDarkMode() {
    const body = document.body;
    const isDarkMode = body.classList.toggle('dark-mode');
    
    // Save preference to localStorage
    localStorage.setItem('darkMode', isDarkMode.toString());
    
    // Update button appearance
    updateDarkModeButton(isDarkMode);
}

function updateDarkModeButton(isDarkMode) {
    const darkModeBtn = document.getElementById('darkModeBtn');
    if (darkModeBtn) {
        darkModeBtn.innerHTML = isDarkMode ? '☀️ Light' : '🌙 Dark';
        darkModeBtn.setAttribute('aria-label', isDarkMode ? 'Switch to light mode' : 'Switch to dark mode');
    }
}

function shareCircular(serialNo, date, orderNo, subject, pdfLink) {
    // Format the share message with proper alignment and bold text
    const shareMessage = `🔔 *DTE Karnataka Circular*

📋 *Serial No:* #${serialNo}
📅 *Date:* ${date}
📄 *Order No:* ${orderNo}

📝 *Subject:*
${subject}

🔗 *PDF Link:* ${pdfLink}

---
Shared from DTE Circulars App`;

    // Check if Web Share API is supported
    if (navigator.share) {
        navigator.share({
            title: `DTE Circular #${serialNo} - ${date}`,
            text: shareMessage,
            url: pdfLink
        }).then(() => {
            console.log('Circular shared successfully');
        }).catch((error) => {
            console.log('Error sharing:', error);
            fallbackShare(shareMessage);
        });
    } else {
        // Fallback for browsers that don't support Web Share API
        fallbackShare(shareMessage);
    }
}

function fallbackShare(message) {
    // Copy to clipboard
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(message).then(() => {
            showShareSuccess('Message copied to clipboard! You can now paste it anywhere.');
        }).catch(() => {
            showShareDialog(message);
        });
    } else {
        // Fallback for older browsers
        showShareDialog(message);
    }
}

function showShareDialog(message) {
    // Create a modal to show the formatted message
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 2000;
        animation: fadeIn 0.3s ease-out;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        padding: 30px;
        border-radius: 12px;
        max-width: 500px;
        width: 90%;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    `;
    
    // Apply dark mode styles if active
    if (document.body.classList.contains('dark-mode')) {
        content.style.background = '#2d3748';
        content.style.color = '#e4e4e4';
    }
    
    content.innerHTML = `
        <h3 style="margin: 0 0 20px 0; color: #3498db;">Share Circular</h3>
        <textarea readonly style="
            width: 100%;
            height: 200px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.9rem;
            line-height: 1.4;
            resize: none;
            background: #f8f9fa;
            color: #333;
        ">${message}</textarea>
        <div style="margin-top: 20px; text-align: center;">
            <button onclick="this.closest('div[style*=fixed]').remove()" style="
                background: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                margin-right: 10px;
            ">Close</button>
            <button onclick="copyToClipboard(this)" style="
                background: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
            ">Copy Text</button>
        </div>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Add copy functionality
    window.copyToClipboard = function(btn) {
        const textarea = btn.closest('div').querySelector('textarea');
        textarea.select();
        document.execCommand('copy');
        btn.textContent = 'Copied!';
        btn.style.background = '#2ecc71';
        setTimeout(() => {
            btn.textContent = 'Copy Text';
            btn.style.background = '#27ae60';
        }, 2000);
    };
}

function showShareSuccess(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #27ae60;
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
        z-index: 2000;
        animation: slideIn 0.5s ease-out;
        font-weight: 600;
    `;
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}