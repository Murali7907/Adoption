/* =========================================================
   KINDHEART — INTERACTIVE JAVASCRIPT ENGINE
   Theme Toggle • Pet Filtering • Modals • AI Assistant • Contact Form • Ambient Sound
   ========================================================= */

let ambientAudio = null;
let isSoundPlaying = false;

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initScrollEffects();
    initSmoothNavScroll();
    initInfiniteVideoLoop();
    initFindAPetSection();
});

/* ---------------------------------------------------------
   1. 🌗 THEME TOGGLE ENGINE
   --------------------------------------------------------- */
function initTheme() {
    const savedTheme = localStorage.getItem('kindheart_theme') || 'dark';
    if (savedTheme === 'light') {
        document.documentElement.classList.add('light');
        updateThemeToggleIcons(true);
    } else {
        document.documentElement.classList.remove('light');
        updateThemeToggleIcons(false);
    }
}

function toggleTheme() {
    const isLight = document.documentElement.classList.toggle('light');
    localStorage.setItem('kindheart_theme', isLight ? 'light' : 'dark');
    updateThemeToggleIcons(isLight);

    const icon = document.getElementById('theme-toggle-icon');
    if (icon) {
        icon.classList.remove('icon-spin');
        void icon.offsetWidth;
        icon.classList.add('icon-spin');
    }
}

function updateThemeToggleIcons(isLight) {
    const themeBtnIcon = document.getElementById('theme-toggle-icon');
    if (themeBtnIcon) {
        themeBtnIcon.innerHTML = isLight 
            ? `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>`
            : `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>`;
    }
}


/* ---------------------------------------------------------
   AMBIENT NATURE SOUND ENGINE
   --------------------------------------------------------- */
function toggleAmbientSound() {
    if (!ambientAudio) {
        ambientAudio = new Audio('/relaxing_birds.wav');
        ambientAudio.loop = true;
        ambientAudio.volume = 0.35;
    }

    const soundIcon = document.getElementById('sound-icon');
    const soundLabel = document.getElementById('sound-label');
    const soundBtn = document.getElementById('ambient-sound-btn');

    if (isSoundPlaying) {
        ambientAudio.pause();
        isSoundPlaying = false;
        if (soundBtn) soundBtn.classList.remove('is-playing');
        if (soundIcon) {
            soundIcon.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"></path></svg>`;
        }
        if (soundLabel) soundLabel.textContent = 'Sound OFF';
        showToast('Ambient soothing sound muted.');
    } else {
        const playPromise = ambientAudio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                isSoundPlaying = true;
                if (soundBtn) soundBtn.classList.add('is-playing');
                if (soundIcon) {
                    soundIcon.innerHTML = `<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path></svg>`;
                }
                if (soundLabel) soundLabel.textContent = 'Sound ON';
                showToast('Playing ambient soothing sound.');
            }).catch(err => {
                console.warn('Audio playback error:', err);
                showToast('Click to allow audio playback.');
            });
        }
    }
}

/* ---------------------------------------------------------
   📱 iPHONE 14/15 CAMERA MODE SWITCHER TAB ENGINE
   --------------------------------------------------------- */
function setActiveTab(tabElement) {
    if (!tabElement) return;
    const tabs = document.querySelectorAll('.iphone-mode-tab, .nav-link-pill');
    tabs.forEach(t => t.classList.remove('is-active'));
    tabElement.classList.add('is-active');
}

function scrollToTop(tabElement) {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    const tab = tabElement || document.querySelector('.iphone-mode-tab');
    if (tab) setActiveTab(tab);
}

/* ---------------------------------------------------------
   ✨ SILKY SMOOTH NAVIGATION & ROLL BACK TO HOME ENGINE
   --------------------------------------------------------- */
function initSmoothNavScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (!targetId || targetId === '#') return;
            
            // 🏠 Smooth roll back to Home
            if (targetId === '#top' || targetId === '#home') {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                if (window.history && window.history.pushState) {
                    window.history.pushState(null, null, window.location.pathname);
                }
                const homeTabs = document.querySelectorAll('a[href="#top"]');
                homeTabs.forEach(t => setActiveTab(t));
                return;
            }

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                const navHeight = 72;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - navHeight;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                setActiveTab(this);
            }
        });
    });
}

/* ---------------------------------------------------------
   🎬 INFINITE SEAMLESS VIDEO LOOP ENGINE (ABOUT US & SHELTER)
   --------------------------------------------------------- */
function initInfiniteVideoLoop() {
    const setupVideoLoop = () => {
        const videos = document.querySelectorAll('video, .about-shelter-video');
        videos.forEach(video => {
            video.muted = true;
            video.loop = true;
            video.playsInline = true;
            video.setAttribute('playsinline', '');
            video.setAttribute('webkit-playsinline', '');
            video.setAttribute('loop', '');
            video.setAttribute('muted', '');
            video.setAttribute('autoplay', '');

            // Fallback 1: Seamlessly restart on ended event
            video.addEventListener('ended', function() {
                this.currentTime = 0;
                const p = this.play();
                if (p && typeof p.catch === 'function') p.catch(() => {});
            });

            // Fallback 2: Loop safeguard just before the video ends (avoids 1-frame freeze)
            video.addEventListener('timeupdate', function() {
                if (this.duration && this.duration > 0 && this.currentTime >= this.duration - 0.2) {
                    this.currentTime = 0;
                    const p = this.play();
                    if (p && typeof p.catch === 'function') p.catch(() => {});
                }
            });

            // Fallback 3: Resume video when user switches tabs or window regains focus
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden && video.paused) {
                    video.play().catch(() => {});
                }
            });

            // Fallback 4: Resume playback if stalled or waiting
            video.addEventListener('stalled', function() {
                const p = this.play();
                if (p && typeof p.catch === 'function') p.catch(() => {});
            });

            // Trigger immediate playback
            const playPromise = video.play();
            if (playPromise && typeof playPromise.catch === 'function') {
                playPromise.catch(() => {
                    const kickstart = () => {
                        video.play().catch(() => {});
                    };
                    window.addEventListener('click', kickstart, { once: true });
                    window.addEventListener('touchstart', kickstart, { once: true });
                    window.addEventListener('scroll', kickstart, { once: true });
                });
            }
        });
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupVideoLoop);
    } else {
        setupVideoLoop();
    }
}

/* ---------------------------------------------------------
   2. 🔍 PRODUCTION FIND A PET DISCOVERY ENGINE
   --------------------------------------------------------- */
const KINDHEART_PETS = [
  {
    id: 1,
    name: "Bruno",
    type: "Dogs",
    category: "dog",
    breed: "Labrador Retriever",
    age: "2 years",
    location: "Kochi",
    distanceKm: 4,
    image: "/featured_dog.jpg",
    traits: ["Friendly", "Playful", "Family-friendly"],
    chipId: "CHIP-88234",
    vax: "Verified Complete",
    desc: "Gentle and outgoing 2-year-old Labrador Retriever. Highly socialized, excellent with children, and loves daily park adventures."
  },
  {
    id: 2,
    name: "Luna",
    type: "Cats",
    category: "cat",
    breed: "Siamese Mix",
    age: "1 year",
    location: "Kochi",
    distanceKm: 6,
    image: "/luna_siamese.jpg",
    traits: ["Affectionate", "Gentle", "Indoor"],
    chipId: "CHIP-44102",
    vax: "Verified Complete",
    desc: "Sweet and tranquil Siamese mix with bright blue eyes. Enjoys cozy sunlit windowsills and calm indoor companionship."
  },
  {
    id: 3,
    name: "Pip & Sunny",
    type: "Birds",
    category: "bird",
    breed: "Turquoise Parakeet",
    age: "8 months",
    location: "Kochi",
    distanceKm: 8,
    image: "/rescued_bird.jpg",
    traits: ["Vocal", "Curious", "Gentle"],
    chipId: "BAND-1904",
    vax: "Avian Health Screened",
    desc: "Bright and cheerful rescued parakeet pair. Loves whistling melodies, exploring perches, and eating fresh greens."
  },
  {
    id: 4,
    name: "Clover",
    type: "Rabbits",
    category: "rabbit",
    breed: "Holland Lop",
    age: "1.5 years",
    location: "Kochi",
    distanceKm: 5,
    image: "/rescued_rabbit.jpg",
    traits: ["Calm", "Litter-trained", "Docile"],
    chipId: "CHIP-31902",
    vax: "Verified Complete",
    desc: "Incredibly docile Holland Lop bunny with soft floppy ears. Completely litter-trained and loves gentle head scratches."
  },
  {
    id: 5,
    name: "Coco",
    type: "Dogs",
    category: "dog",
    breed: "Beagle Mix",
    age: "2 years",
    location: "Munnar",
    distanceKm: 32,
    image: "/coco_beagle.jpg",
    traits: ["Energetic", "Explorer", "Good with kids"],
    chipId: "CHIP-11094",
    vax: "Verified Complete",
    desc: "Playful and curious Beagle mix rescued from Munnar. High energy, friendly explorer who loves outdoor nature trails."
  },
  {
    id: 6,
    name: "Milo",
    type: "Cats",
    category: "cat",
    breed: "Domestic Shorthair",
    age: "6 months",
    location: "Wayanad",
    distanceKm: 45,
    image: "/cozy_kitten_play.jpg",
    traits: ["Playful", "Curious", "Loving"],
    chipId: "CHIP-66210",
    vax: "Verified Complete",
    desc: "Playful ginger kitten rescued by Wayanad Haven. Loves chasing feather toys and curling up in warm blankets."
  },
  {
    id: 7,
    name: "Oliver",
    type: "Birds",
    category: "bird",
    breed: "Crested Cockatiel",
    age: "2 years",
    location: "Wayanad",
    distanceKm: 42,
    image: "/rescued_cockatiel.jpg",
    traits: ["Whistler", "Social", "Hand-tamed"],
    chipId: "BAND-8812",
    vax: "Avian Health Screened",
    desc: "Hand-tamed cockatiel with an expressive crest. Loves stepping up on friendly fingers and whistling short tunes."
  },
  {
    id: 8,
    name: "Barnaby",
    type: "Rabbits",
    category: "rabbit",
    breed: "Mini Rex",
    age: "1 year",
    location: "Munnar",
    distanceKm: 28,
    image: "/rescued_bunny.jpg",
    traits: ["Quiet", "Velvety", "Lap-friendly"],
    chipId: "CHIP-77401",
    vax: "Verified Complete",
    desc: "Velvety-soft Mini Rex rabbit who enjoys quiet homes. Very gentle demeanor, fond of clean straw and crisp hay."
  },
  {
    id: 9,
    name: "Rocky",
    type: "Dogs",
    category: "dog",
    breed: "German Shepherd Mix",
    age: "1.5 years",
    location: "Wayanad",
    distanceKm: 40,
    image: "/rocky_shepherd.jpg",
    traits: ["Loyal", "Protective", "Trainable"],
    chipId: "CHIP-99120",
    vax: "Verified Complete",
    desc: "Loyal and intelligent German Shepherd mix. Highly receptive to training, loyal guardian, and affectionate companion."
  },
  {
    id: 10,
    name: "Bella",
    type: "Dogs",
    category: "dog",
    breed: "Golden Retriever",
    age: "3 years",
    location: "Trivandrum",
    distanceKm: 48,
    image: "/happy_golden_pup.jpg",
    traits: ["Sweet-tempered", "Patient", "Obedient"],
    chipId: "CHIP-55419",
    vax: "Verified Complete",
    desc: "Sweet-tempered Golden Retriever who loves swimming, fetching tennis balls, and resting calmly at your feet."
  }
];

let activePetCategory = 'All';
const favoritedPetIds = new Set();

function initFindAPetSection() {
    renderPetGrid();
}

function renderPetGrid(petsToRender = null) {
    const grid = document.getElementById('pet-cards-grid');
    if (!grid) return;

    const list = petsToRender || KINDHEART_PETS;

    if (list.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center space-y-3">
                <p class="text-base font-semibold text-white">No matching pets found</p>
                <p class="text-xs text-slate-400">Try adjusting your keyword, location, or distance filters.</p>
                <button onclick="resetPetFilters()" class="mt-3 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-xs font-semibold text-white transition-all cursor-pointer">
                    Clear Filters
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = list.slice(0, 4).map(pet => {
        const safeDesc = (pet.desc || '').replace(/'/g, "\\'");
        return `
            <article class="pet-card-hover-wrapper group" onclick="showPetDetail('${pet.name}', '${pet.breed}', '${pet.location}', '${pet.chipId}', '${pet.vax}', '${pet.image}', '${safeDesc}')">
                <img src="${pet.image}" alt="${pet.name} - ${pet.breed}" class="pet-card-hover-bg" loading="lazy" />
                
                <!-- Static Bottom Title -->
                <div class="pet-card-static-scrim">
                    <h3 class="text-xl font-bold text-white font-heading">${pet.name}</h3>
                    <p class="text-xs text-slate-300 font-medium font-mono">${pet.breed} &bull; ${pet.age}</p>
                </div>

                <!-- Hover Details Overlay (Appears on Hover) -->
                <div class="pet-card-details-overlay">
                    <div>
                        <span class="text-[10px] font-bold font-mono tracking-widest text-[#FF8F1C] uppercase block mb-1">AVAILABLE FOR ADOPTION</span>
                        <h3 class="text-2xl font-bold text-white font-heading leading-tight mb-0.5">${pet.name}</h3>
                        <p class="text-xs font-semibold text-[#FF8F1C] font-mono mb-2">${pet.breed} &bull; ${pet.age}</p>

                        <p class="text-xs text-slate-200 leading-relaxed line-clamp-3 mb-2">
                            ${pet.desc}
                        </p>
                    </div>

                    <button class="pet-adopt-btn" aria-label="Adopt ${pet.name}" onclick="event.stopPropagation(); openAdoptionModal('${pet.name}');">
                        <span>Adopt Me</span>
                        <span>&rarr;</span>
                    </button>
                </div>
            </article>
        `;
    }).join('');
}

function setPetCategory(category, btnElement) {
    activePetCategory = category;

    const categoryButtons = document.querySelectorAll('.pet-category-btn');
    categoryButtons.forEach(btn => {
        btn.classList.remove('is-active');
        btn.setAttribute('aria-selected', 'false');
    });

    if (btnElement) {
        btnElement.classList.add('is-active');
        btnElement.setAttribute('aria-selected', 'true');
    }

    handlePetSearch();
}

function handlePetSearch() {
    const searchInput = document.getElementById('pet-search-input');
    const locationSelect = document.getElementById('pet-location-select');
    const distanceSelect = document.getElementById('pet-distance-select');

    const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
    const loc = locationSelect ? locationSelect.value : 'all';
    const dist = distanceSelect ? distanceSelect.value : 'any';

    const filtered = KINDHEART_PETS.filter(pet => {
        // Category check
        if (activePetCategory !== 'All' && pet.type !== activePetCategory) {
            return false;
        }

        // Query check (name, breed, traits)
        if (query) {
            const matchName = pet.name.toLowerCase().includes(query);
            const matchBreed = pet.breed.toLowerCase().includes(query);
            const matchTrait = pet.traits.some(t => t.toLowerCase().includes(query));
            if (!matchName && !matchBreed && !matchTrait) return false;
        }

        // Location check
        if (loc !== 'all' && pet.location.toLowerCase() !== loc.toLowerCase()) {
            return false;
        }

        // Distance check
        if (dist !== 'any') {
            const maxKm = parseInt(dist, 10);
            if (pet.distanceKm > maxKm) return false;
        }

        return true;
    });

    renderPetGrid(filtered);
}

function resetPetFilters() {
    const searchInput = document.getElementById('pet-search-input');
    const locationSelect = document.getElementById('pet-location-select');
    const distanceSelect = document.getElementById('pet-distance-select');

    if (searchInput) searchInput.value = '';
    if (locationSelect) locationSelect.value = 'all';
    if (distanceSelect) distanceSelect.value = 'any';

    const allBtn = document.querySelector('.pet-category-btn');
    if (allBtn) setPetCategory('All', allBtn);
    else {
        activePetCategory = 'All';
        renderPetGrid(KINDHEART_PETS);
    }
}

function toggleFavorite(petId, btnElement, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }

    if (favoritedPetIds.has(petId)) {
        favoritedPetIds.delete(petId);
        if (btnElement) {
            btnElement.classList.remove('is-favorited');
            const svg = btnElement.querySelector('svg');
            if (svg) svg.setAttribute('fill', 'none');
        }
        showToast('Removed from saved pets');
    } else {
        favoritedPetIds.add(petId);
        if (btnElement) {
            btnElement.classList.add('is-favorited');
            const svg = btnElement.querySelector('svg');
            if (svg) svg.setAttribute('fill', 'currentColor');
        }
        showToast('Saved to your favorites');
    }
}

function filterPets(category, btnElement) {
    // Backwards compatibility hook
    setPetCategory(category === 'all' ? 'All' : category, btnElement);
}

/* ---------------------------------------------------------
   3. 🔑 AUTHENTICATION & LOGIN NAVIGATION ENGINE
   --------------------------------------------------------- */
let isUserLoggedIn = (typeof window !== 'undefined' && window.isUserLoggedIn) ? true : false;
let pendingPetDetail = null;
let pendingAdoptionPet = null;

function openAuthModal(mode = 'login') {
    window.location.href = mode === 'register' ? '/users/register/' : '/users/login/';
}

function switchAuthMode(mode) {
    window.location.href = mode === 'register' ? '/users/register/' : '/users/login/';
}

function closeAuthModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.classList.remove('is-open');
}

function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    const label = document.getElementById('pw-toggle-label');
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        if (label) label.textContent = 'Hide';
    } else {
        input.type = 'password';
        if (label) label.textContent = 'Show';
    }
}

function autofillDemoLogin() {
    const email = document.getElementById('auth-input-email');
    const password = document.getElementById('auth-input-password');
    const name = document.getElementById('auth-input-name');
    if (email) email.value = 'alex.adopter@kindheart.org';
    if (password) password.value = 'RescuePets2026!';
    if (name) name.value = 'Alex Rivera';
    showToast('🐾 Demo Adopter credentials loaded!');
}

function handleAuthSubmit(event) {
    if (event) event.preventDefault();
    isUserLoggedIn = true;
    closeAuthModal();
    const loginBtns = document.querySelectorAll('.auth-btn-login');
    loginBtns.forEach(btn => {
        btn.textContent = 'Account 👤';
    });
    showToast('🔑 Welcome back to KindHeart Shelter!');
}

/* ---------------------------------------------------------
   4. 📋 ADOPTION APPLICATION MODAL ENGINE
   --------------------------------------------------------- */
function openAdoptionModal(petName = 'Bruno') {
    if (!isUserLoggedIn) {
        pendingAdoptionPet = petName;
        openAuthModal('login');
        showToast(`🔒 Please log in to start the adoption application for ${petName}.`);
        return;
    }

    const modal = document.getElementById('adoption-modal');
    if (!modal) return;
    
    const petField = document.getElementById('adopt-pet-name');
    if (petField) petField.value = petName;
    
    modal.classList.add('is-open');
}

function closeAdoptionModal() {
    const modal = document.getElementById('adoption-modal');
    if (modal) modal.classList.remove('is-open');
}

function handleAdoptionSubmit(event) {
    event.preventDefault();
    closeAdoptionModal();
    showToast('🐾 Adoption request submitted successfully! We will contact you soon.');
}

/* ---------------------------------------------------------
   5. 🔍 PET DETAIL PREVIEW MODAL ENGINE (AUTH PROTECTED)
   --------------------------------------------------------- */
const PET_DATA = {
    bruno: {
        name: "Bruno",
        type: "Labrador Retriever · 2 Years",
        image: "/featured_dog.jpg",
        shelter: "Kochi Rescue Shelter",
        status: "Verified Ready",
        chip: "CHIP-88234-99",
        desc: "Bruno is a gentle and outgoing 2-year-old Labrador Retriever. Highly socialized, excellent with children, and loves daily park adventures.",
        vax: "Rabies, DHPP, Bordetella (Complete)"
    },
    luna: {
        name: "Luna",
        type: "Siamese Mix · 1 Year",
        image: "/luna_siamese.jpg",
        shelter: "Animal Haven Reserve",
        status: "Verified Ready",
        chip: "CHIP-44102-12",
        desc: "Luna is a sweet and tranquil Siamese mix with bright blue eyes. Enjoys cozy sunlit windowsills and calm indoor companionship.",
        vax: "FVRCP, FeLV, Rabies (Complete)"
    },
    maya: {
        name: "Maya (Tusked Asian Elephant)",
        type: "Tusked Asian Elephant · Shelter Rescue",
        image: "/kindheart_3d_elephant.jpg",
        shelter: "KindHeart Wildlife Rescue Shelter",
        status: "Protected Shelter",
        chip: "GPS-TAG-88",
        desc: "Maya was rescued from captive hardship and now wanders freely in our 1,200-acre protected bamboo jungle reserve.",
        vax: "Full Shelter Medical Clearance"
    }
};

function openPetPreviewModal(petKey) {
    const data = PET_DATA[petKey] || PET_DATA.bruno;
    showPetDetail(data.name, data.type, data.shelter, data.chip, data.vax, data.image, data.desc);
}

function showPetDetail(name, type, shelter, chip, vax, image, desc) {
    const modal = document.getElementById('fullscreen-preview-modal');
    if (!modal) return;

    if (document.getElementById('modal-pet-name')) document.getElementById('modal-pet-name').textContent = name;
    if (document.getElementById('modal-pet-type')) document.getElementById('modal-pet-type').textContent = type;
    if (document.getElementById('modal-pet-shelter')) document.getElementById('modal-pet-shelter').textContent = shelter;
    if (document.getElementById('modal-pet-chip')) document.getElementById('modal-pet-chip').textContent = chip;
    if (document.getElementById('modal-pet-vax')) document.getElementById('modal-pet-vax').textContent = vax;
    if (document.getElementById('modal-pet-image')) document.getElementById('modal-pet-image').src = image;
    if (document.getElementById('modal-pet-desc')) document.getElementById('modal-pet-desc').textContent = desc;

    modal.classList.add('is-open');
}

function closePetPreviewModal() {
    const modal = document.getElementById('fullscreen-preview-modal');
    if (modal) modal.classList.remove('is-open');
}

function adoptCurrentProfilePet() {
    const petNameEl = document.getElementById('modal-pet-name');
    const petName = petNameEl ? petNameEl.textContent.trim() : 'Bruno';
    closePetPreviewModal();
    setTimeout(() => {
        openAdoptionModal(petName);
    }, 250);
}

window.adoptCurrentProfilePet = adoptCurrentProfilePet;

/* ---------------------------------------------------------
   6. 🤖 AI ASSISTANT CONCIERGE DRAWER
   --------------------------------------------------------- */
function toggleAiAssistant() {
    const drawer = document.getElementById('ai-assistant-drawer');
    if (!drawer) return;
    drawer.classList.toggle('is-open');
}

function sendAiMessage(presetMsg = null) {
    const input = document.getElementById('ai-input');
    const msg = presetMsg || (input ? input.value.trim() : '');
    if (!msg) return;

    const container = document.getElementById('ai-chat-messages');
    if (!container) return;

    const userMsgHtml = `
        <div class="flex justify-end mb-3">
            <div class="bg-emerald-600 text-white text-xs font-semibold px-4 py-2.5 rounded-2xl max-w-[85%] shadow-md">
                ${msg}
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', userMsgHtml);
    if (input) input.value = '';

    container.scrollTop = container.scrollHeight;

    setTimeout(() => {
        let response = "I'm looking through our shelter records to find your perfect rescue match! 🐾";
        if (msg.toLowerCase().includes('dog') || msg.toLowerCase().includes('bruno')) {
            response = "Wonderful! Bruno (Golden Retriever) and Bella (Labrador) are fully vaccinated, microchipped, and available for home visits!";
        } else if (msg.toLowerCase().includes('cat') || msg.toLowerCase().includes('luna')) {
            response = "Luna (Persian Kitten) is super calm, litter-trained, and ready for home adoption in Kochi!";
        } else if (msg.toLowerCase().includes('elephant') || msg.toLowerCase().includes('maya')) {
            response = "Maya the Tusked Asian Elephant is protected in our bamboo jungle reserve. You can sponsor her care directly!";
        }

        const aiMsgHtml = `
            <div class="flex justify-start mb-3">
                <div class="flex items-start gap-2 max-w-[90%]">
                    <div class="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-extrabold text-xs shrink-0 border border-emerald-500/30">💬</div>
                    <div class="liquid-glass text-slate-200 text-xs font-medium px-4 py-2.5 rounded-2xl border border-white/10 shadow-sm">
                        ${response}
                    </div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', aiMsgHtml);
        container.scrollTop = container.scrollHeight;
    }, 600);
}

/* ---------------------------------------------------------
   7. 📬 INTERACTIVE CONTACT FORM SUBMISSION ENGINE
   --------------------------------------------------------- */
function handleContactSubmit(event) {
    event.preventDefault();
    const nameInput = document.getElementById('contact-name');
    const name = nameInput ? nameInput.value.trim() : 'Friend';
    
    // Reset form fields
    event.target.reset();

    // Show Liquid Glass Toast Notification
    showToast(`✨ Thank you, ${name}! Your inquiry has been sent to KindHeart Pet Adoption. We will respond within 2 hours.`);
}

/* ---------------------------------------------------------
   8. 🔔 LIQUID GLASS TOAST NOTIFICATION ENGINE
   --------------------------------------------------------- */
function showToast(message) {
    let toast = document.getElementById('contact-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'contact-toast';
        toast.className = 'liquid-glass px-6 py-3.5 rounded-2xl border border-emerald-500/40 text-xs font-extrabold text-white shadow-2xl backdrop-blur-xl flex items-center gap-3 bg-black/90';
        document.body.appendChild(toast);
    }
    
    toast.innerHTML = `<span class="text-base">📬</span> <span>${message}</span>`;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 4500);
}

/* Scroll FX & Active Nav ScrollSpy Engine */
function initScrollEffects() {
    const handleScroll = () => {
        updateActiveNavOnScroll();
        const scrollTopBtn = document.getElementById('scroll-to-top-btn');
        if (scrollTopBtn) {
            if (window.scrollY > 120) {
                scrollTopBtn.classList.remove('opacity-0', 'pointer-events-none', 'scale-75');
                scrollTopBtn.classList.add('opacity-100', 'scale-100');
            } else {
                scrollTopBtn.classList.add('opacity-0', 'pointer-events-none', 'scale-75');
                scrollTopBtn.classList.remove('opacity-100', 'scale-100');
            }
        }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
}

function initScrollReveal() {
    const reveals = document.querySelectorAll('.scroll-reveal');
    reveals.forEach(el => el.classList.add('is-visible'));
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                }
            });
        }, { threshold: 0.05 });
        reveals.forEach(el => observer.observe(el));
    }
}

function updateActiveNavOnScroll() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.iphone-mode-tab, .nav-link-pill');
    if (!sections.length || !navLinks.length) return;

    let currentSectionId = 'top';

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        if (rect.top <= 220 && rect.bottom >= 100) {
            currentSectionId = section.getAttribute('id');
        }
    });

    if (currentSectionId) {
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === `#${currentSectionId}`) {
                link.classList.add('is-active');
            } else {
                link.classList.remove('is-active');
            }
        });
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initSmoothNavScroll();
    initScrollEffects();
    initScrollReveal();
    initInfiniteVideoLoop();
});

// If DOM is already loaded
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    initSmoothNavScroll();
    initScrollEffects();
    initScrollReveal();
    initInfiniteVideoLoop();
}

// Make functions globally available
window.toggleTheme = toggleTheme;
window.toggleAmbientSound = toggleAmbientSound;
window.toggleMobileMenu = toggleMobileMenu;
window.setActiveTab = setActiveTab;
window.filterPets = filterPets;
window.openAuthModal = openAuthModal;
window.switchAuthMode = switchAuthMode;
window.togglePasswordVisibility = togglePasswordVisibility;
window.autofillDemoLogin = autofillDemoLogin;
window.closeAuthModal = closeAuthModal;
window.handleAuthSubmit = handleAuthSubmit;
window.openAdoptionModal = openAdoptionModal;
window.closeAdoptionModal = closeAdoptionModal;
window.handleAdoptionSubmit = handleAdoptionSubmit;
window.openPetPreviewModal = openPetPreviewModal;
window.showPetDetail = showPetDetail;
window.closePetPreviewModal = closePetPreviewModal;
window.toggleAiAssistant = toggleAiAssistant;
window.sendAiMessage = sendAiMessage;
window.handleContactSubmit = handleContactSubmit;
window.showToast = showToast;
window.scrollToTop = scrollToTop;
window.initSmoothNavScroll = initSmoothNavScroll;
window.initScrollReveal = initScrollReveal;

/* ---------------------------------------------------------
   📱 MOBILE NAVIGATION DRAWER CONTROLLER
   --------------------------------------------------------- */
let _lastMobileMenuToggle = 0;

function toggleMobileMenu(forceState, event) {
    if (event) {
        if (typeof event.preventDefault === 'function') event.preventDefault();
        if (typeof event.stopPropagation === 'function') event.stopPropagation();
    }
    
    const now = Date.now();
    if (now - _lastMobileMenuToggle < 60 && typeof forceState !== 'boolean') {
        return; // Prevent duplicate double-invocation
    }
    _lastMobileMenuToggle = now;

    const drawer = document.getElementById('mobile-nav-drawer');
    const toggleBtn = document.getElementById('mobile-menu-toggle-btn');
    const menuIcon = document.getElementById('mobile-menu-icon');
    if (!drawer) return;

    const willOpen = typeof forceState === 'boolean' 
        ? forceState 
        : !drawer.classList.contains('is-open');

    if (willOpen) {
        drawer.classList.add('is-open');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', 'true');
            toggleBtn.classList.add('is-active');
        }
        if (menuIcon) {
            menuIcon.innerHTML = `
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"></line>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"></line>
            `;
        }
    } else {
        drawer.classList.remove('is-open');
        if (toggleBtn) {
            toggleBtn.setAttribute('aria-expanded', 'false');
            toggleBtn.classList.remove('is-active');
        }
        if (menuIcon) {
            menuIcon.innerHTML = `
                <line x1="4" y1="6" x2="20" y2="6" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"></line>
                <line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"></line>
                <line x1="4" y1="18" x2="20" y2="18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"></line>
            `;
        }
    }
}

window.toggleMobileMenu = toggleMobileMenu;

// Close mobile menu on Escape key and outside click
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        toggleMobileMenu(false);
    }
});

document.addEventListener('click', (e) => {
    const drawer = document.getElementById('mobile-nav-drawer');
    if (drawer && drawer.classList.contains('is-open')) {
        if (!drawer.contains(e.target) && !e.target.closest('#mobile-menu-toggle-btn')) {
            toggleMobileMenu(false);
        }
    }
});