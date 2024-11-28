document.addEventListener('DOMContentLoaded', function() {
    // Initial load
    loadDailyWord();
    
    // Navigation handlers
    document.getElementById('dailyWordLink').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('dailyWordSection');
        loadDailyWord();
    });

    document.getElementById('popularWordsLink').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('popularWordsSection');
        loadPopularWords();
    });

    document.getElementById('grammarLink').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('grammarSection');
        loadGrammarLesson();
    });

    document.getElementById('progressLink').addEventListener('click', function(e) {
        e.preventDefault();
        showSection('progressSection');
        loadProgress();
    });

    // Grammar navigation
    document.getElementById('nextLesson').addEventListener('click', function() {
        currentLesson = (currentLesson + 1) % 6; // We now have 6 lessons
        loadGrammarLesson();
    });

    document.getElementById('prevLesson').addEventListener('click', function() {
        currentLesson = (currentLesson - 1 + 6) % 6; // We now have 6 lessons
        loadGrammarLesson();
    });
});

let currentLesson = 0;

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    // Show the selected section
    document.getElementById(sectionId).style.display = 'block';
}

function loadDailyWord() {
    fetch('/daily-word')
        .then(response => response.json())
        .then(data => {
            document.getElementById('turkishWord').textContent = data.turkish;
            document.getElementById('englishTranslation').textContent = data.english;
            document.getElementById('example').textContent = data.example;
        });
}

function loadGrammarLesson() {
    fetch(`/grammar-lesson?lesson=${currentLesson}`)
        .then(response => response.json())
        .then(data => {
            // Update title and content
            document.getElementById('lessonTitle').textContent = data.title;
            document.getElementById('lessonContent').innerHTML = data.content.replace(/\\n/g, '<br>');
            
            // Update difficulty badge
            const difficultyBadge = document.querySelector('.difficulty-badge');
            difficultyBadge.textContent = data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1);
            difficultyBadge.className = `difficulty-badge badge ${data.difficulty === 'beginner' ? 'bg-success' : 'bg-warning'} mb-3`;
            
            // Update examples
            const examplesList = document.getElementById('examplesList');
            examplesList.innerHTML = '';
            data.examples.forEach(example => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = example;
                examplesList.appendChild(li);
            });
            
            // Update video embed
            const videoFrame = document.getElementById('videoFrame');
            if (data.video_link) {
                // Convert YouTube URL to embed URL
                const videoId = getYouTubeVideoId(data.video_link);
                if (videoId) {
                    videoFrame.src = `https://www.youtube.com/embed/${videoId}`;
                    document.getElementById('videoSection').style.display = 'block';
                } else {
                    document.getElementById('videoSection').style.display = 'none';
                }
            } else {
                document.getElementById('videoSection').style.display = 'none';
            }
        });
}

function getYouTubeVideoId(url) {
    if (!url) return null;
    
    // Handle different YouTube URL formats
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    
    return (match && match[2].length === 11) ? match[2] : null;
}

function loadProgress() {
    fetch('/progress')
        .then(response => response.json())
        .then(data => {
            const progressBar = document.querySelector('.progress-bar');
            progressBar.style.width = `${data.progress}%`;
            progressBar.setAttribute('aria-valuenow', data.progress);
        });
}

function loadPopularWords() {
    fetch('/popular-words')
        .then(response => response.json())
        .then(data => {
            // Create category tabs
            const categoryTabs = document.getElementById('categoryTabs');
            categoryTabs.innerHTML = '';
            
            Object.keys(data).forEach((category, index) => {
                const li = document.createElement('li');
                li.className = 'nav-item';
                li.role = 'presentation';
                
                const button = document.createElement('button');
                button.className = `nav-link ${index === 0 ? 'active' : ''}`;
                button.id = `${category.toLowerCase().replace(/\s+/g, '-')}-tab`;
                button.setAttribute('data-bs-toggle', 'pill');
                button.setAttribute('data-category', category);
                button.type = 'button';
                button.textContent = category;
                
                button.addEventListener('click', () => loadCategoryWords(category));
                
                li.appendChild(button);
                categoryTabs.appendChild(li);
            });
            
            // Load first category
            loadCategoryWords(Object.keys(data)[0]);
        });
}

function loadCategoryWords(category) {
    fetch(`/popular-words/${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(words => {
            const wordCards = document.querySelector('.word-cards');
            wordCards.innerHTML = '';
            
            words.forEach(word => {
                const card = document.createElement('div');
                card.className = 'card mb-3';
                card.innerHTML = `
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h3 class="card-title mb-0">${word.turkish}</h3>
                            <span class="badge ${word.usage_frequency === 'very high' ? 'bg-danger' : 'bg-warning'}">${word.usage_frequency}</span>
                        </div>
                        <h4 class="card-subtitle mb-2 text-muted">${word.english}</h4>
                        <p class="card-text"><em>${word.example}</em></p>
                    </div>
                `;
                wordCards.appendChild(card);
            });
        });
}
