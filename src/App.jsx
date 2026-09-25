import React, { useEffect } from 'react';

export default function App() {
  useEffect(() => {
    // Dynamically load Vanilla JS Engine
    const script = document.createElement('script');
    script.src = '/script.js';
    script.async = true;
    document.body.appendChild(script);
    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  return (
    <div className="antialiased selection:bg-emerald-500/30 selection:text-white min-h-screen text-slate-100 bg-[#0A0A0B]">

      {/* 🎬 FIXED FULLSCREEN CINEMATIC VIDEO BACKGROUND */}
      <div id="bg-video-container">
        <video id="bg-video-element" autoPlay muted loop playsInline preload="auto">
          <source src="/hero.mp4" type="video/mp4" />
          <img src="/kindheart_real_hero.jpg" alt="Background Wildlife Loop" className="w-full h-full object-cover" />
        </video>
      </div>
      <div className="dark-video-scrim"></div>

      {/* 🌫️ ULTRA-CLEAN APPLE LIQUID GLASS STICKY HEADER NAVBAR */}
      <header className="nav-kindheart-fixed fixed top-0 left-0 right-0 z-50 flex items-center justify-between w-full">
        {/* FAR LEFT CORNER: Logo & Brand Name */}
        <a href="#top" className="flex items-center gap-2.5 font-extrabold tracking-tight text-white font-heading shrink-0" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}>
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#FF8F1C] to-[#E06000] flex items-center justify-center text-sm text-white shadow-sm">❤️</div>
          <span className="font-heading font-extrabold text-base sm:text-lg tracking-tight text-white">Kind<span className="text-[#FF8F1C]">Heart</span></span>
        </a>

        {/* CENTER: Main Header Tabs (Desktop Only) */}
        <nav className="iphone-camera-switcher hidden lg:flex items-center justify-center mx-auto" aria-label="Primary Navigation">
          <div className="iphone-mode-track flex items-center gap-1">
            <a href="#top" className="iphone-mode-tab is-active" onClick={(e) => { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); if (window.setActiveTab) window.setActiveTab(e.currentTarget); }}>Home</a>
            <a href="#find-a-pet" className="iphone-mode-tab" onClick={(e) => { e.preventDefault(); const el = document.querySelector('#find-a-pet'); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.pageYOffset - 72, behavior: 'smooth' }); if (window.setActiveTab) window.setActiveTab(e.currentTarget); }}>Find a Pet</a>
            <a href="#services" className="iphone-mode-tab" onClick={(e) => { e.preventDefault(); const el = document.querySelector('#services'); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.pageYOffset - 72, behavior: 'smooth' }); if (window.setActiveTab) window.setActiveTab(e.currentTarget); }}>Services</a>
            <a href="#sanctuary-banner" className="iphone-mode-tab" onClick={(e) => { e.preventDefault(); const el = document.querySelector('#sanctuary-banner'); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.pageYOffset - 72, behavior: 'smooth' }); if (window.setActiveTab) window.setActiveTab(e.currentTarget); }}>About Us</a>
            <a href="#contact" className="iphone-mode-tab" onClick={(e) => { e.preventDefault(); const el = document.querySelector('#contact'); if (el) window.scrollTo({ top: el.getBoundingClientRect().top + window.pageYOffset - 72, behavior: 'smooth' }); if (window.setActiveTab) window.setActiveTab(e.currentTarget); }}>Contact Us</a>
          </div>
        </nav>

        {/* FAR RIGHT CORNER: Darkmode Toggle, Login, Sound, Mobile Menu Button */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          {/* 1st: Theme Toggle */}
          <button onClick={() => window.toggleTheme && window.toggleTheme()} className="btn-apple-secondary btn-header-icon-sm cursor-pointer" title="Toggle Light/Dark Theme">
            <span id="theme-toggle-icon">🌙</span>
          </button>

          {/* 2nd: Ambient Sound Toggle (In header on desktop and mobile) */}
          <button id="ambient-sound-btn" onClick={() => window.toggleAmbientSound && window.toggleAmbientSound()} className="btn-apple-secondary btn-header-icon-sm cursor-pointer flex items-center justify-center" title="Toggle Ambient Sound">
            <span id="sound-icon" className="text-xs">🔈</span>
          </button>

          {/* 3rd: Login (Icon on mobile, text on desktop) */}
          <button onClick={() => window.openAuthModal && window.openAuthModal('login')} className="auth-btn-login btn-apple-secondary btn-header-icon-sm md:btn-header-sm cursor-pointer text-xs sm:text-sm" title="Login / Account">
            <span className="md:hidden text-xs">👤</span>
            <span className="hidden md:inline">Login</span>
          </button>

          {/* 4th: Mobile Menu Button (Only appears in mobile view < 1024px) */}
          <button id="mobile-menu-toggle-btn" onClick={(e) => window.toggleMobileMenu && window.toggleMobileMenu(undefined, e)} className="btn-mobile-hamburger cursor-pointer text-white inline-flex lg:hidden" aria-label="Toggle Mobile Menu" aria-expanded="false">
            <svg id="mobile-menu-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" className="pointer-events-none stroke-white" stroke="white">
              <line x1="4" y1="6" x2="20" y2="6" stroke="white" strokeWidth="2.2" strokeLinecap="round" />
              <line x1="4" y1="12" x2="20" y2="12" stroke="white" strokeWidth="2.2" strokeLinecap="round" />
              <line x1="4" y1="18" x2="20" y2="18" stroke="white" strokeWidth="2.2" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </header>

      {/* 📱 MOBILE FROSTED LIQUID-GLASS NAVIGATION DRAWER (< 1024px) */}
      <div id="mobile-nav-drawer" className="mobile-nav-drawer lg:hidden">
        <div className="mobile-nav-inner px-5 py-6 flex flex-col gap-4">
          <nav className="flex flex-col gap-2" aria-label="Mobile Navigation">
            <a href="#top" className="mobile-nav-link active" onClick={() => { window.scrollTo({ top: 0, behavior: 'smooth' }); if (window.toggleMobileMenu) window.toggleMobileMenu(false); }}>
              <span>Home</span>
              <span className="text-xs font-mono opacity-50">01</span>
            </a>
            <a href="#find-a-pet" className="mobile-nav-link" onClick={() => { if (window.toggleMobileMenu) window.toggleMobileMenu(false); }}>
              <span>Find a Pet</span>
              <span className="text-xs font-mono opacity-50">02</span>
            </a>
            <a href="#services" className="mobile-nav-link" onClick={() => { if (window.toggleMobileMenu) window.toggleMobileMenu(false); }}>
              <span>Services</span>
              <span className="text-xs font-mono opacity-50">03</span>
            </a>
            <a href="#sanctuary-banner" className="mobile-nav-link" onClick={() => { if (window.toggleMobileMenu) window.toggleMobileMenu(false); }}>
              <span>About Us</span>
              <span className="text-xs font-mono opacity-50">04</span>
            </a>
            <a href="#contact" className="mobile-nav-link" onClick={() => { if (window.toggleMobileMenu) window.toggleMobileMenu(false); }}>
              <span>Contact Us</span>
              <span className="text-xs font-mono opacity-50">05</span>
            </a>
          </nav>
        </div>
      </div>

      {/* MAIN PAGE CONTAINER */}
      <div className="relative z-10 w-full pt-28 sm:pt-32 lg:pt-20">

        {/* 🌟 HERO VIEWPORT */}
        <section className="min-h-0 lg:min-h-[calc(100vh-80px)] flex flex-col justify-start lg:justify-center items-center relative pt-8 pb-12 sm:pt-14 sm:pb-16 lg:pt-4" id="top">
          <div className="shell grid grid-cols-1 lg:grid-cols-12 gap-8 sm:gap-10 items-center">

            {/* LEFT HERO CONTENT */}
            <div className="lg:col-span-7 xl:col-span-6 space-y-5 sm:space-y-6">
              <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white font-heading leading-[1.12] sm:leading-[1.08]">
                A New Best Friend <br />
                <span className="text-gradient-cognac">Is Waiting.</span>
              </h1>

              <p className="hero-subtext text-sm sm:text-lg text-slate-300 font-normal sm:font-medium leading-relaxed max-w-lg">
                Discover verified rescue pets looking for a loving home. Track full medical clearance, vaccination records, and arrange doorstep transport.
              </p>

              <div className="flex flex-wrap items-center gap-3 sm:gap-4">
                <a href="#find-a-pet" className="btn-hero-glass">
                  Find a Pet
                </a>
                <a href="#sanctuary-banner" className="btn-hero-glass">
                  About Us
                </a>
              </div>
            </div>

            {/* RIGHT HERO SHOWCASE CARD */}
            <div className="lg:col-span-5 xl:col-span-6 mt-4 lg:mt-0">
              <div className="hero-image-glass-frame relative group overflow-hidden rounded-2xl sm:rounded-3xl p-2 sm:p-2.5 liquid-glass border border-white/15 shadow-2xl">
                <div className="relative h-[280px] sm:h-[380px] lg:h-[480px] w-full rounded-xl sm:rounded-2xl overflow-hidden bg-black/40">
                  <img src="/kindheart_real_hero.jpg" alt="KindHeart Rescued Companion Hero" className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/10"></div>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* 🐾 FIND A PET DISCOVERY & FEATURED GALLERY */}
        <section id="find-a-pet" className="pt-10 pb-12 sm:pt-18 sm:pb-16 relative scroll-mt-20">
          <div className="shell space-y-12 sm:space-y-16">

            {/* SECTION HEADER (GENEROUS MARGIN GAP) */}
            <div className="find-a-pet-header max-w-3xl space-y-3 mb-12 sm:mb-16">
              <span className="text-xs font-mono font-bold tracking-widest text-[#FF8F1C] uppercase block">FIND A PET</span>
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white font-heading leading-tight">
                Find Your New Best Friend
              </h2>
              <p className="text-slate-300 text-sm sm:text-base font-normal max-w-2xl leading-relaxed">
                Every pet deserves a loving home. Find a companion that's waiting to meet you.
              </p>
            </div>

            {/* PET CARDS GRID (4 PER ROW ON DESKTOP) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-4" id="pet-cards-grid">

              {/* CARD 1: BRUNO */}
              <article className="pet-card-hover-wrapper group" onClick={() => window.showPetDetail && window.showPetDetail('Bruno', 'Labrador Retriever', 'Kochi', 'CHIP-88234', '100% Cleared', '/featured_dog.jpg', 'Gentle and outgoing 2-year-old Labrador Retriever. Highly socialized, excellent with children, and loves daily park adventures.')}>
                <img src="/featured_dog.jpg" alt="Bruno - Labrador Retriever" className="pet-card-hover-bg" loading="lazy" />

                {/* Static Bottom Title */}
                <div className="pet-card-static-scrim">
                  <h3 className="text-xl font-bold text-white font-heading">Bruno</h3>
                  <p className="text-xs text-slate-300 font-medium font-mono">Labrador Retriever &bull; 2 years</p>
                </div>

                {/* Hover Details Overlay (Appears on Hover) */}
                <div className="pet-card-details-overlay">
                  <div>
                    <span className="text-[10px] font-bold font-mono tracking-widest text-[#FF8F1C] uppercase block mb-1">AVAILABLE FOR ADOPTION</span>
                    <h3 className="text-2xl font-bold text-white font-heading leading-tight mb-0.5">Bruno</h3>
                    <p className="text-xs font-semibold text-[#FF8F1C] font-mono mb-2">Labrador Retriever &bull; 2 years</p>

                    <p className="text-xs text-slate-200 leading-relaxed line-clamp-3 mb-2">
                      Gentle and outgoing 2-year-old Labrador Retriever. Highly socialized, excellent with children, and loves daily park adventures.
                    </p>
                  </div>

                  <button className="pet-adopt-btn" aria-label="Adopt Bruno" onClick={(e) => { e.stopPropagation(); window.openAdoptionModal ? window.openAdoptionModal('Bruno') : (window.showPetDetail && window.showPetDetail('Bruno', 'Labrador Retriever', 'Kochi', 'CHIP-88234', '100% Cleared', '/featured_dog.jpg', 'Gentle and outgoing 2-year-old Labrador Retriever. Highly socialized, excellent with children, and loves daily park adventures.')); }}>
                    <span>Adopt Me</span>
                    <span>🐾 &rarr;</span>
                  </button>
                </div>
              </article>

              {/* CARD 2: LUNA */}
              <article className="pet-card-hover-wrapper group" onClick={() => window.showPetDetail && window.showPetDetail('Luna', 'Siamese Mix', 'Kochi', 'CHIP-44102', '100% Cleared', '/luna_siamese.jpg', 'Sweet and tranquil Siamese mix with bright blue eyes. Enjoys cozy sunlit windowsills and calm indoor companionship.')}>
                <img src="/luna_siamese.jpg" alt="Luna - Siamese Mix" className="pet-card-hover-bg" loading="lazy" />

                {/* Static Bottom Title */}
                <div className="pet-card-static-scrim">
                  <h3 className="text-xl font-bold text-white font-heading">Luna</h3>
                  <p className="text-xs text-slate-300 font-medium font-mono">Siamese Mix &bull; 1 year</p>
                </div>

                {/* Hover Details Overlay (Appears on Hover) */}
                <div className="pet-card-details-overlay">
                  <div>
                    <span className="text-[10px] font-bold font-mono tracking-widest text-[#FF8F1C] uppercase block mb-1">AVAILABLE FOR ADOPTION</span>
                    <h3 className="text-2xl font-bold text-white font-heading leading-tight mb-0.5">Luna</h3>
                    <p className="text-xs font-semibold text-[#FF8F1C] font-mono mb-2">Siamese Mix &bull; 1 year</p>

                    <p className="text-xs text-slate-200 leading-relaxed line-clamp-3 mb-2">
                      Sweet and tranquil Siamese mix with bright blue eyes. Enjoys cozy sunlit windowsills and calm indoor companionship.
                    </p>
                  </div>

                  <button className="pet-adopt-btn" aria-label="Adopt Luna" onClick={(e) => { e.stopPropagation(); window.openAdoptionModal ? window.openAdoptionModal('Luna') : (window.showPetDetail && window.showPetDetail('Luna', 'Siamese Mix', 'Kochi', 'CHIP-44102', '100% Cleared', '/luna_siamese.jpg', 'Sweet and tranquil Siamese mix with bright blue eyes. Enjoys cozy sunlit windowsills and calm indoor companionship.')); }}>
                    <span>Adopt Me</span>
                    <span>🐾 &rarr;</span>
                  </button>
                </div>
              </article>

              {/* CARD 3: PIP & SUNNY */}
              <article className="pet-card-hover-wrapper group" onClick={() => window.showPetDetail && window.showPetDetail('Pip & Sunny', 'Turquoise Parakeet', 'Kochi', 'BAND-1904', 'Health Screened', '/rescued_bird.jpg', 'Bright and cheerful rescued parakeet pair. Loves whistling melodies, exploring perches, and eating fresh greens.')}>
                <img src="/rescued_bird.jpg" alt="Pip & Sunny - Turquoise Parakeet" className="pet-card-hover-bg" loading="lazy" />

                {/* Static Bottom Title */}
                <div className="pet-card-static-scrim">
                  <h3 className="text-xl font-bold text-white font-heading">Pip & Sunny</h3>
                  <p className="text-xs text-slate-300 font-medium font-mono">Turquoise Parakeet &bull; 8 months</p>
                </div>

                {/* Hover Details Overlay (Appears on Hover) */}
                <div className="pet-card-details-overlay">
                  <div>
                    <span className="text-[10px] font-bold font-mono tracking-widest text-[#FF8F1C] uppercase block mb-1">AVAILABLE FOR ADOPTION</span>
                    <h3 className="text-2xl font-bold text-white font-heading leading-tight mb-0.5">Pip & Sunny</h3>
                    <p className="text-xs font-semibold text-[#FF8F1C] font-mono mb-2">Turquoise Parakeet &bull; 8 months</p>

                    <p className="text-xs text-slate-200 leading-relaxed line-clamp-3 mb-2">
                      Bright and cheerful rescued parakeet pair. Loves whistling melodies, exploring perches, and eating fresh greens.
                    </p>
                  </div>

                  <button className="pet-adopt-btn" aria-label="Adopt Pip & Sunny" onClick={(e) => { e.stopPropagation(); window.openAdoptionModal ? window.openAdoptionModal('Pip & Sunny') : (window.showPetDetail && window.showPetDetail('Pip & Sunny', 'Turquoise Parakeet', 'Kochi', 'BAND-1904', 'Health Screened', '/rescued_bird.jpg', 'Bright and cheerful rescued parakeet pair.')); }}>
                    <span>Adopt Me</span>
                    <span>🐾 &rarr;</span>
                  </button>
                </div>
              </article>

              {/* CARD 4: CLOVER */}
              <article className="pet-card-hover-wrapper group" onClick={() => window.showPetDetail && window.showPetDetail('Clover', 'Holland Lop', 'Kochi', 'CHIP-31902', '100% Cleared', '/rescued_rabbit.jpg', 'Incredibly docile Holland Lop bunny with soft floppy ears. Completely litter-trained and loves gentle head scratches.')}>
                <img src="/rescued_rabbit.jpg" alt="Clover - Holland Lop" className="pet-card-hover-bg" loading="lazy" />

                {/* Static Bottom Title */}
                <div className="pet-card-static-scrim">
                  <h3 className="text-xl font-bold text-white font-heading">Clover</h3>
                  <p className="text-xs text-slate-300 font-medium font-mono">Holland Lop &bull; 1.5 years</p>
                </div>

                {/* Hover Details Overlay (Appears on Hover) */}
                <div className="pet-card-details-overlay">
                  <div>
                    <span className="text-[10px] font-bold font-mono tracking-widest text-[#FF8F1C] uppercase block mb-1">AVAILABLE FOR ADOPTION</span>
                    <h3 className="text-2xl font-bold text-white font-heading leading-tight mb-0.5">Clover</h3>
                    <p className="text-xs font-semibold text-[#FF8F1C] font-mono mb-2">Holland Lop &bull; 1.5 years</p>

                    <p className="text-xs text-slate-200 leading-relaxed line-clamp-3 mb-2">
                      Incredibly docile Holland Lop bunny with soft floppy ears. Completely litter-trained and loves gentle head scratches.
                    </p>
                  </div>

                  <button className="pet-adopt-btn" aria-label="Adopt Clover" onClick={(e) => { e.stopPropagation(); window.openAdoptionModal ? window.openAdoptionModal('Clover') : (window.showPetDetail && window.showPetDetail('Clover', 'Holland Lop', 'Kochi', 'CHIP-31902', '100% Cleared', '/rescued_rabbit.jpg', 'Incredibly docile Holland Lop bunny with soft floppy ears.')); }}>
                    <span>Adopt Me</span>
                    <span>🐾 &rarr;</span>
                  </button>
                </div>
              </article>

            </div>

          </div>
        </section>

        {/* 🛠️ SERVICES SECTION */}
        <section id="services" className="pt-10 pb-16 sm:pt-14 sm:pb-20 relative scroll-mt-24">
          <div className="shell space-y-12 sm:space-y-16">

            {/* SECTION HEADER (MATCHES FIND A PET) */}
            <div className="services-header max-w-4xl space-y-3 mt-2 sm:mt-3 mb-12 sm:mb-16">
              <span className="text-xs font-mono font-bold tracking-widest text-[#FF8F1C] uppercase block">SERVICES</span>
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white font-heading leading-tight">
                Our KindHeart Services
              </h2>
              <p className="text-slate-300 font-normal leading-relaxed text-sm sm:text-base max-w-2xl">
                From professional pet grooming to lifelong post-adoption veterinary support, KindHeart provides complete compassionate care.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
              {/* Service 1: Veterinary Care */}
              <div className="service-card-image-blur group">
                <img src="/real_veterinary_care.jpg" alt="Veterinary Care" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Veterinary Care</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">Complete medical screenings, microchipping, and verified vaccination clearance.</p>
                  </div>
                </div>
              </div>

              {/* Service 2: Shelter Network */}
              <div className="service-card-image-blur group">
                <img src="/kindheart_real_shelter.jpg" alt="Shelter Network" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Shelter Network</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">Connecting 320+ certified non-profit animal rescue sanctuaries with loving homes.</p>
                  </div>
                </div>
              </div>

              {/* Service 3: Doorstep Transport */}
              <div className="service-card-image-blur group">
                <img src="/service_transport.jpg" alt="Safe Doorstep Transport" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Safe Transport</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">GPS-monitored climate-controlled transport delivering pets safely to your doorstep.</p>
                  </div>
                </div>
              </div>

              {/* Service 4: Adoption Counseling */}
              <div className="service-card-image-blur group">
                <img src="/service_adoption_counseling.jpg" alt="Adoption Counseling" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Adoption Counseling</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">Dedicated family matching consultations to ensure lifelong harmonious bonds.</p>
                  </div>
                </div>
              </div>

              {/* Service 5: Wellness & Therapy */}
              <div className="service-card-image-blur group">
                <img src="/service_wellness_therapy.jpg" alt="Rehabilitation & Wellness Therapy" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Wellness & Therapy</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">Specialized physical rehabilitation, trauma recovery, and nutritional support.</p>
                  </div>
                </div>
              </div>

              {/* Service 6: Pet Grooming & Spa */}
              <div className="service-card-image-blur group">
                <img src="/service_grooming.jpg" alt="Pet Grooming & Spa" className="service-card-bg-img" />
                <div className="service-card-default-scrim flex flex-col justify-end p-6">
                  <div>
                    <h3 className="text-2xl font-bold text-white font-heading drop-shadow-md">Pet Grooming & Spa</h3>
                    <p className="text-xs text-slate-200 mt-1 font-medium leading-relaxed">Therapeutic warm baths, gentle coat conditioning, nail trimming, and hygienic care for adopted pets.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* 🐾 CINEMATIC ANIMATED PET RESCUE BANNER (ABOUT US) */}
        <section id="sanctuary-banner" className="shell pt-12 pb-0 sm:pt-16 sm:pb-0 scroll-mt-24 relative">
          {/* Animated Ambient Background Glow Orbs */}
          <div className="about-ambient-glow -top-10 -right-10 z-0"></div>
          <div className="about-ambient-glow -bottom-10 -left-10 z-0" style={{ animationDelay: '-3s', background: 'radial-gradient(circle, rgba(255, 143, 28, 0.2) 0%, transparent 70%)' }}></div>

          {/* ABOUT US SECTION HEADER */}
          <div className="about-header max-w-4xl space-y-3 mb-10 sm:mb-14 md:mb-16 relative z-10">
            <span className="text-xs font-mono font-bold tracking-widest text-[#FF8F1C] uppercase block">ABOUT US</span>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white font-heading leading-tight">
              About KindHeart
            </h2>
            <p className="text-slate-300 font-normal leading-relaxed text-sm sm:text-base max-w-2xl">
              Dedicated to rescuing, rehabilitating, and connecting companion pets with loving families.
            </p>
          </div>

          <div
            className="about-banner-container rounded-3xl p-8 sm:p-12 md:p-16 relative overflow-hidden min-h-[500px] flex flex-col justify-center items-center text-center z-10"
          >
            {/* 🎬 Looping Cinematic Sanctuary Video (361057.mp4) with Poster Fallback (Crisp & Natural) */}
            <video
              autoPlay
              loop
              muted
              playsInline
              preload="auto"
              poster="/kindheart_3d_elephant.jpg"
              className="about-sanctuary-video absolute inset-0 w-full h-full object-cover pointer-events-none"
            >
              <source src="/361057.mp4" type="video/mp4" />
            </video>
            {/* Subtle Scrim Matching Hero & Find a Pet Background */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/25 to-black/20 pointer-events-none"></div>

            {/* Shimmer Sweep Light Ray */}
            <div className="about-shimmer-sweep"></div>

            <div className="relative z-20 max-w-3xl mx-auto text-center flex flex-col items-center space-y-6">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white font-heading leading-tight tracking-tight drop-shadow-lg text-center">
                Nurturing Rescued Pets, <br />
                <span className="text-gradient-cognac">Finding Forever Homes.</span>
              </h2>
              <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-medium drop-shadow-md max-w-2xl mx-auto text-center">
                KindHeart provides compassionate rehabilitation, safe foster networks, and lifetime medical support for abandoned companion animals, connecting thousands of rescued pets with caring adopters across 320+ partner shelters.
              </p>

              {/* Centered Impact Metric Cards with Pet Adoption Focus */}
              <div className="about-impact-grid grid grid-cols-1 sm:grid-cols-3 gap-3.5 sm:gap-4 mt-7 sm:mt-9 pt-1 sm:pt-2 w-full max-w-2xl mx-auto">
                <div className="about-impact-pill p-4 sm:p-5 rounded-2xl text-center flex flex-col items-center justify-center cursor-pointer shadow-lg group/pill">
                  <span className="text-2xl sm:text-3xl font-extrabold text-gradient-cognac font-heading block group-hover/pill:scale-105 transition-transform mb-1">12,500+</span>
                  <span className="text-xs sm:text-sm text-slate-200 font-medium block text-center">Happy Adoptions</span>
                  <div className="w-full max-w-[120px] bg-white/20 h-1 rounded-full mt-3 overflow-hidden mx-auto">
                    <div className="bg-gradient-to-r from-[#FF8F1C] to-[#E06000] h-full rounded-full w-[85%] animate-pulse"></div>
                  </div>
                </div>

                <div className="about-impact-pill p-4 sm:p-5 rounded-2xl text-center flex flex-col items-center justify-center cursor-pointer shadow-lg group/pill">
                  <span className="text-2xl sm:text-3xl font-extrabold text-gradient-cognac font-heading block group-hover/pill:scale-105 transition-transform mb-1">98%</span>
                  <span className="text-xs sm:text-sm text-slate-200 font-medium block text-center">Placement Success</span>
                  <div className="w-full max-w-[120px] bg-white/20 h-1 rounded-full mt-3 overflow-hidden mx-auto">
                    <div className="bg-gradient-to-r from-[#FF8F1C] to-[#E06000] h-full rounded-full w-[94%] animate-pulse"></div>
                  </div>
                </div>

                <div className="about-impact-pill p-4 sm:p-5 rounded-2xl text-center flex flex-col items-center justify-center cursor-pointer shadow-lg group/pill">
                  <span className="text-2xl sm:text-3xl font-extrabold text-gradient-cognac font-heading block group-hover/pill:scale-105 transition-transform mb-1">320+</span>
                  <span className="text-xs sm:text-sm text-slate-200 font-medium block text-center">Rescue Partners</span>
                  <div className="w-full max-w-[120px] bg-white/20 h-1 rounded-full mt-3 overflow-hidden mx-auto">
                    <div className="bg-gradient-to-r from-[#FF8F1C] to-[#E06000] h-full rounded-full w-[100%] animate-pulse"></div>
                  </div>
                </div>
              </div>

              {/* Centered Buttons: Explore More & Contact Us */}
              <div className="about-actions-group pt-4 sm:pt-6 mt-6 sm:mt-8 flex flex-wrap items-center justify-center gap-4">
                <a href="#find-a-pet" className="btn-apple-primary text-xs sm:text-sm py-3.5 px-7 cursor-pointer shadow-xl hover:shadow-orange-500/25 active:scale-95 transition-all">
                  <span>Explore More</span>
                </a>
                <a href="#contact" className="btn-hero-glass btn-apple-secondary text-xs sm:text-sm py-3.5 px-7 flex items-center justify-center shadow-lg active:scale-95 transition-all" style={{ borderRadius: '999px' }}>
                  <span>Contact Us</span>
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* 📬 CONTACT US SECTION */}
        <section id="contact" className="shell pt-14 pb-16 sm:pt-20 sm:pb-24 scroll-mt-24 relative scroll-reveal">
          {/* Ambient Subtle Background Glow */}
          <div className="about-ambient-glow -bottom-10 -right-10 z-0"></div>

          <div className="space-y-10 sm:space-y-14 relative z-10">
            {/* SECTION HEADER (HUMANIZED & SHORTENED WITH SPACE BELOW) */}
            <div className="contact-header max-w-3xl space-y-3">
              <span className="text-xs font-semibold tracking-wider text-[#FF8F1C] uppercase block font-mono">CONTACT US</span>
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white font-heading leading-tight">
                Get in Touch With Us
              </h2>
              <p className="text-slate-300 text-sm sm:text-base font-normal max-w-2xl leading-relaxed">
                We're here to help you adopt, foster, volunteer, or support rescued pets.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
              {/* Left: Realistic Sanctuary Support Photo Card (Centered content, no badges) */}
              <div className="lg:col-span-5 h-full">
                <div className="contact-photo-card h-full min-h-[300px] sm:min-h-[440px] lg:min-h-[500px] relative rounded-2xl sm:rounded-3xl overflow-hidden border border-white/15 shadow-2xl group flex flex-col items-center justify-center text-center">
                  <img
                    src="/contact_sanctuary_help.jpg"
                    alt="KindHeart Pet Support Team"
                    className="contact-photo-img absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                  />
                  <div className="contact-photo-scrim absolute inset-0 bg-gradient-to-t from-black/95 via-black/55 to-black/35"></div>

                  {/* Centered Warm Sanctuary Note Overlay */}
                  <div className="relative z-10 p-6 sm:p-10 flex flex-col items-center justify-center text-center h-full space-y-4">
                    <h3 className="text-2xl sm:text-3xl font-bold text-white font-heading leading-tight drop-shadow-md">
                      Compassionate Support, <br /><span className="text-gradient-cognac">Every Step of the Way.</span>
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-normal max-w-sm drop-shadow">
                      Whether you're adopting, fostering, volunteering, or inquiring about pet care, our adoption caretakers are always here to assist you.
                    </p>
                  </div>
                </div>
              </div>

              {/* Right: Borderless Form Card with Centered Heading & Spacious Field Gaps */}
              <div className="lg:col-span-7 h-full flex flex-col justify-center items-center">
                <form
                  onSubmit={(e) => window.handleContactSubmit && window.handleContactSubmit(e)}
                  className="contact-form-card w-full max-w-xl mx-auto flex flex-col justify-center h-full border-0"
                >
                  {/* Centered Heading & Subtitle with Generous Space Below */}
                  <div className="contact-form-intro space-y-3 text-center max-w-lg mx-auto mb-10 sm:mb-14">
                    <h3 className="text-2xl sm:text-3xl font-extrabold text-white font-heading tracking-tight text-center">
                      Send Us an Inquiry
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal text-center max-w-md mx-auto">
                      Fill out the details below and our team will get back to you promptly.
                    </p>
                  </div>

                  {/* Field Inputs with Dedicated Explicit Vertical Gaps */}
                  <div className="w-full">
                    {/* Row 1: Full Name & Email Address */}
                    <div className="contact-form-row contact-grid-two">
                      <div>
                        <input
                          type="text"
                          id="contact-name"
                          required
                          placeholder="Your Full Name"
                          aria-label="Your Full Name"
                          className="contact-input-field"
                        />
                      </div>
                      <div>
                        <input
                          type="email"
                          id="contact-email"
                          required
                          placeholder="Email Address"
                          aria-label="Email Address"
                          className="contact-input-field"
                        />
                      </div>
                    </div>

                    {/* Row 2: Phone Number */}
                    <div className="contact-form-row">
                      <input
                        type="tel"
                        id="contact-phone"
                        placeholder="Phone Number"
                        aria-label="Phone Number"
                        className="contact-input-field"
                      />
                    </div>

                    {/* Row 3: Message */}
                    <div className="contact-form-row">
                      <textarea
                        id="contact-message"
                        rows="4"
                        required
                        placeholder="How can our pet adoption and rescue team help you today?"
                        aria-label="Your Message"
                        className="contact-input-field resize-none"
                      ></textarea>
                    </div>
                  </div>

                  {/* Submit Button with Clean Dedicated Spacing */}
                  <div className="contact-form-btn-wrap w-full">
                    <button
                      type="submit"
                      className="w-full btn-apple-primary py-4 text-sm font-bold cursor-pointer justify-center shadow-xl hover:shadow-orange-500/25 active:scale-[0.98] transition-all"
                    >
                      <span>Send Enquiry Message</span>
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </section>

        {/* 🐾 MINIMALIST CENTERED FROSTED-BLURRED COMPACT FOOTER */}
        <footer className="footer-kindheart-blurred w-full mt-8 sm:mt-12 py-6 sm:py-8 text-center">
          <div className="footer-centered-content max-w-4xl mx-auto px-6 text-center flex flex-col items-center justify-center">
            {/* 1. Centered Brand Name with Space Above & Below */}
            <a
              href="#top"
              className="footer-brand-wrap inline-flex items-center justify-center gap-2 text-xl sm:text-2xl font-extrabold tracking-tight text-white font-heading hover:opacity-90 transition-opacity mx-auto mb-3 sm:mb-4"
              onClick={(e) => {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
                const homeTab = document.querySelector('.iphone-mode-tab');
                if (window.setActiveTab && homeTab) window.setActiveTab(homeTab);
              }}
            >
              <span className="font-heading font-extrabold tracking-tight text-white">
                Kind<span className="text-[#FF8F1C]">Heart</span>
              </span>
            </a>

            {/* 2. Centered Navigation Menu */}
            <nav className="footer-nav-wrap flex flex-wrap items-center justify-center gap-x-4 sm:gap-x-8 gap-y-2 text-[11px] sm:text-xs font-bold uppercase tracking-widest text-slate-300 mx-auto mb-3 sm:mb-4">
              <a
                href="#top"
                onClick={(e) => {
                  e.preventDefault();
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                  const homeTab = document.querySelector('.iphone-mode-tab');
                  if (window.setActiveTab && homeTab) window.setActiveTab(homeTab);
                }}
                className="hover:text-white transition-colors"
              >
                Home
              </a>
              <a href="#find-a-pet" className="hover:text-white transition-colors">Find a Pet</a>
              <a href="#services" className="hover:text-white transition-colors">Services</a>
              <a href="#sanctuary-banner" className="hover:text-white transition-colors">About Us</a>
              <a href="#contact" className="hover:text-white transition-colors">Contact</a>
            </nav>

            {/* 3. Centered Circular Social Media Icons */}
            <div className="footer-social-wrap flex flex-row items-center justify-center gap-3 sm:gap-3.5 mx-auto mb-3 sm:mb-4">
              {/* Twitter / X */}
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded-full border border-white/20 flex items-center justify-center text-slate-300 hover:text-[#FF8F1C] hover:border-[#FF8F1C] hover:scale-110 transition-all"
                aria-label="Twitter"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              {/* Facebook */}
              <a
                href="https://facebook.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded-full border border-white/20 flex items-center justify-center text-slate-300 hover:text-[#FF8F1C] hover:border-[#FF8F1C] hover:scale-110 transition-all"
                aria-label="Facebook"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.82 0-1.611.211-1.956.54-.344.33-.424.966-.424 1.87v1.57h4.088l-.565 3.667h-3.523v7.98H9.101z"/>
                </svg>
              </a>
              {/* Instagram */}
              <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-8 h-8 sm:w-9 sm:h-9 rounded-full border border-white/20 flex items-center justify-center text-slate-300 hover:text-[#FF8F1C] hover:border-[#FF8F1C] hover:scale-110 transition-all"
                aria-label="Instagram"
              >
                <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </a>
            </div>

            {/* 4. Copyright Text Line */}
            <p className="footer-copyright-wrap text-[11px] sm:text-xs text-slate-400 font-normal text-center mx-auto">
              Copyright &copy; 2026 All rights reserved | This website is made with <span className="text-[#FF8F1C]">❤️</span> by <strong className="text-white font-semibold">KindHeart</strong>
            </p>
          </div>
        </footer>

      </div>

      {/* 🔑 PET ADOPTION AUTH MODAL */}
      <div id="auth-modal" className="modal-overlay">
        <div className="auth-modal-card relative overflow-hidden">
          {/* Ambient Warm Pet Sanctuary Glow Accents */}
          <div className="auth-card-glow pointer-events-none"></div>

          {/* Close Button with Smooth Hover */}
          <button onClick={() => window.closeAuthModal && window.closeAuthModal()} className="service-close-btn absolute top-4 right-4 z-30" title="Close" aria-label="Close modal">✕</button>

          {/* Top Pet Mascot Banner & Sanctuary Badge */}
          <div className="flex items-center gap-3.5 pb-4 border-b border-white/10">
            <div className="relative shrink-0">
              <img src="/login_pet_mascot.jpg" alt="KindHeart Pet Companions" className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl object-cover border-2 border-[#FF8F1C]/40 shadow-lg shadow-amber-500/20" />
              <span className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-gradient-to-br from-[#FF8F1C] to-[#E06000] flex items-center justify-center text-[10px] text-white shadow">🐾</span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-[#FF8F1C] text-[10px] font-bold tracking-wider uppercase font-mono mb-1">
                <span>🐾</span>
                <span>KindHeart Sanctuary Portal</span>
              </div>
              <h3 id="auth-modal-title" className="text-lg sm:text-xl font-extrabold text-white font-heading tracking-tight leading-snug">
                Welcome Back to KindHeart 🐾
              </h3>
              <p id="auth-modal-sub" className="text-[11px] sm:text-xs text-slate-300 font-normal leading-tight">
                Your furry rescue companions are waiting for you!
              </p>
            </div>
          </div>

          {/* Interactive Mode Switcher (Sign In / New Adopter) */}
          <div className="mt-4 p-1 rounded-xl bg-black/40 border border-white/10 flex items-center gap-1">
            <button type="button" id="auth-tab-login" onClick={() => window.switchAuthMode && window.switchAuthMode('login')} className="auth-mode-tab flex-1 py-1.5 text-xs font-bold rounded-lg transition-all text-white bg-[#FF8F1C] shadow-sm flex items-center justify-center gap-1.5 cursor-pointer">
              <span>🔑</span>
              <span>Sign In</span>
            </button>
            <button type="button" id="auth-tab-register" onClick={() => window.switchAuthMode && window.switchAuthMode('register')} className="auth-mode-tab flex-1 py-1.5 text-xs font-bold rounded-lg transition-all text-slate-400 hover:text-white flex items-center justify-center gap-1.5 cursor-pointer">
              <span>🐾</span>
              <span>New Adopter</span>
            </button>
          </div>

          {/* Auth Form */}
          <form onSubmit={(e) => window.handleAuthSubmit && window.handleAuthSubmit(e)} className="mt-4 space-y-3.5">
            {/* Name field (shown only in register mode) */}
            <div id="auth-name-field" className="hidden">
              <label className="block text-[11px] font-mono text-slate-300 font-bold mb-1 flex items-center gap-1.5">
                <span>👤</span>
                <span>Your Full Name</span>
              </label>
              <input type="text" id="auth-input-name" placeholder="Sarah Jenkins" className="auth-input-styled w-full" />
            </div>

            {/* Email field */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-[11px] font-mono text-slate-300 font-bold flex items-center gap-1.5">
                  <span>✉️</span>
                  <span>Adopter Email Address</span>
                </label>
                <button type="button" onClick={() => window.autofillDemoLogin && window.autofillDemoLogin()} className="text-[10px] text-[#FF8F1C] hover:underline font-mono font-bold flex items-center gap-1 cursor-pointer">
                  <span>✨</span>
                  <span>Auto-fill Demo</span>
                </button>
              </div>
              <input type="email" id="auth-input-email" required placeholder="alex@example.com" className="auth-input-styled w-full" />
            </div>

            {/* Password field */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-[11px] font-mono text-slate-300 font-bold flex items-center gap-1.5">
                  <span>🔒</span>
                  <span>Security Password</span>
                </label>
                <button type="button" onClick={(e) => window.togglePasswordVisibility && window.togglePasswordVisibility('auth-input-password', e.currentTarget)} className="text-[10px] text-slate-400 hover:text-slate-200 font-mono flex items-center gap-1 cursor-pointer">
                  <span id="pw-toggle-label">Show</span>
                </button>
              </div>
              <input type="password" id="auth-input-password" required placeholder="••••••••" className="auth-input-styled w-full" />
            </div>

            {/* Extra Option: Remember Me & Quick Pet Link */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer select-none">
                <input type="checkbox" defaultChecked className="accent-[#FF8F1C] w-3.5 h-3.5 rounded cursor-pointer" />
                <span>Keep me signed in</span>
              </label>
              <a href="#pets" onClick={() => window.closeAuthModal && window.closeAuthModal()} className="text-[11px] text-emerald-400 hover:underline font-medium">
                Explore Rescues First 🐾
              </a>
            </div>

            {/* Submit Button */}
            <button type="submit" id="auth-submit-btn" className="w-full btn-apple-primary py-3 px-4 text-xs sm:text-sm font-bold cursor-pointer flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 hover:shadow-amber-500/35 transition-all">
              <span>Sign In to Meet Pets</span>
              <span>🐾 &rarr;</span>
            </button>
          </form>

          {/* Trust Badge Footer */}
          <div className="mt-4 pt-3 border-t border-white/10 flex items-center justify-between text-[10px] text-slate-400">
            <span className="flex items-center gap-1">
              <span>❤️</span>
              <span>KindHeart Animal Sanctuary</span>
            </span>
            <span className="flex items-center gap-1 text-emerald-400 font-medium">
              <span>✓</span>
              <span>Safe & Verified Adoption</span>
            </span>
          </div>
        </div>
      </div>

      {/* 📋 ADOPTION APPLICATION MODAL */}
      <div id="adoption-modal" className="modal-overlay">
        <div className="modal-card p-6 sm:p-8 relative">
          <button onClick={() => window.closeAdoptionModal && window.closeAdoptionModal()} className="service-close-btn absolute top-5 right-5 z-30" title="Close">✕</button>
          <div className="space-y-6">
            <div>
              <h3 className="text-2xl font-extrabold text-white font-heading">Adoption Application 🐾</h3>
              <p className="text-xs text-slate-300 font-medium mt-1">Submit your application to adopt or sponsor a rescue companion.</p>
            </div>
            <form onSubmit={(e) => window.handleAdoptionSubmit && window.handleAdoptionSubmit(e)} className="space-y-4">
              <div>
                <label className="block text-xs font-mono text-slate-300 font-bold mb-1.5">Selected Pet / Companion</label>
                <input type="text" id="adopt-pet-name" readOnly className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2.5 text-xs text-emerald-400 font-mono font-bold" />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-300 font-bold mb-1.5">Your Full Name</label>
                <input type="text" required placeholder="Jane Doe" className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500" />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-300 font-bold mb-1.5">Phone Number</label>
                <input type="tel" required placeholder="+91 98765 43210" className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500" />
              </div>
              <button type="submit" className="w-full btn-apple-primary py-3 text-xs font-bold cursor-pointer justify-center">Submit Application</button>
            </form>
          </div>
        </div>
      </div>

      {/* 📱 PET DETAIL PREVIEW MODAL */}
      <div id="fullscreen-preview-modal" className="modal-overlay">
        <div className="modal-card p-6 sm:p-8 relative">
          <button onClick={() => window.closePetPreviewModal && window.closePetPreviewModal()} className="service-close-btn absolute top-4 right-4 z-30" title="Close Preview">✕</button>
          <div className="space-y-6">
            <div className="h-64 rounded-2xl overflow-hidden relative border border-white/15">
              <img id="modal-pet-image" src="" alt="Pet Preview" className="w-full h-full object-cover" />
            </div>
            <div className="space-y-3">
              <span id="modal-pet-shelter" className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-widest block">Kochi Sanctuary</span>
              <h3 id="modal-pet-name" className="text-3xl font-extrabold text-white font-heading">Bruno</h3>
              <p id="modal-pet-type" className="text-xs font-mono text-slate-300">Golden Retriever · 2 Years</p>
              <p id="modal-pet-desc" className="text-xs text-slate-300 leading-relaxed font-medium">Verified pet details...</p>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] font-mono text-slate-400 block">Microchip ID:</span>
                  <span id="modal-pet-chip" className="text-xs font-bold text-white font-mono">CHIP-98402</span>
                </div>
                <div className="p-3 rounded-xl bg-white/5 border border-white/10">
                  <span className="text-[10px] font-mono text-slate-400 block">Vaccinations:</span>
                  <span id="modal-pet-vax" className="text-xs font-bold text-emerald-400 font-mono">Verified Complete</span>
                </div>
              </div>

              {/* ACTION BUTTONS MATCHING OTHER SITE BUTTONS */}
              <div className="flex items-center gap-3 pt-4 border-t border-white/10">
                <button id="modal-adopt-btn" onClick={() => window.adoptCurrentProfilePet ? window.adoptCurrentProfilePet() : (window.openAdoptionModal && window.openAdoptionModal('Bruno'))} className="flex-1 btn-apple-primary py-3 px-5 text-xs sm:text-sm font-bold flex items-center justify-center gap-2 cursor-pointer shadow-lg transition-all">
                  <span>Adopt Me</span>
                  <span>🐾 &rarr;</span>
                </button>
                <button onClick={() => window.closePetPreviewModal && window.closePetPreviewModal()} className="btn-apple-secondary py-3 px-5 text-xs sm:text-sm font-bold flex items-center justify-center gap-2 cursor-pointer transition-all">
                  <span>Close</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ⬆️ SCROLL TO TOP ARROW BUTTON (WITH GENERATED BRAND LOGO) */}
      <button id="scroll-to-top-btn" onClick={() => window.scrollToTop && window.scrollToTop()}
        className="fixed bottom-6 right-6 z-40 w-12 h-12 rounded-full border border-amber-500/40 shadow-2xl backdrop-blur-xl flex items-center justify-center transition-all duration-300 opacity-0 pointer-events-none scale-75 hover:scale-110 active:scale-95 cursor-pointer overflow-hidden p-0"
        title="Scroll to Top"
        aria-label="Scroll to Top">
        <img src="/scroll_up_logo.png" alt="Scroll to Top" className="w-full h-full object-cover rounded-full pointer-events-none drop-shadow-md" />
      </button>

    </div>
  );
}
