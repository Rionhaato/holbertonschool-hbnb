const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
let allPlaces = [];
const PLACE_STORAGE_KEY = 'hbnb_current_place_id';
const PLACE_IMAGE_MAP = {
    'demo loft': 'images/places/demo-loft.png',
    'city studio': 'images/places/city-studio.png',
    'mountain cabin': 'images/places/mountain-cabin.png',
    'beach house': 'images/places/beach-house.png'
};
const PLACE_LOCATION_LABELS = {
    'demo loft': 'Rome, Italy',
    'city studio': 'New York City, USA',
    'mountain cabin': 'Alaska, USA',
    'beach house': 'Penang, Malaysia'
};

function setCookie(name, value, maxAgeSeconds = 86400) {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; SameSite=Lax`;
}

function deleteCookie(name) {
    document.cookie = `${name}=; path=/; max-age=0; SameSite=Lax`;
}

function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split('; ') : [];

    for (const cookie of cookies) {
        const [cookieName, ...cookieValue] = cookie.split('=');
        if (cookieName === name) {
            return decodeURIComponent(cookieValue.join('='));
        }
    }

    return null;
}

function showLoginError(message) {
    const errorBox = document.getElementById('login-error');
    if (!errorBox) {
        return;
    }

    errorBox.textContent = message;
    errorBox.hidden = false;
}

function clearLoginError() {
    const errorBox = document.getElementById('login-error');
    if (!errorBox) {
        return;
    }

    errorBox.textContent = '';
    errorBox.hidden = true;
}

async function loginUser(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });

    let data = null;
    try {
        data = await response.json();
    } catch (error) {
        data = null;
    }

    if (!response.ok) {
        const message = data && data.message ? data.message : 'Invalid email or password.';
        throw new Error(message);
    }

    return data;
}

function updateAuthenticationUI() {
    const token = getCookie('token');
    const userEmail = getCookie('user_email');
    const authLinks = document.querySelectorAll('.auth-link');
    const userChip = document.getElementById('user-chip');
    const userEmailLabel = document.getElementById('user-email');
    const userAvatar = document.getElementById('user-avatar');

    authLinks.forEach((link) => {
        link.classList.toggle('is-hidden', Boolean(token));
    });

    if (userChip) {
        userChip.classList.toggle('is-hidden', !token);
    }

    if (token && userEmail) {
        if (userEmailLabel) {
            userEmailLabel.textContent = userEmail;
        }
        if (userAvatar) {
            userAvatar.textContent = userEmail.charAt(0).toUpperCase();
        }
    }

    return token;
}

function logoutUser() {
    deleteCookie('token');
    deleteCookie('user_id');
    deleteCookie('user_email');
    window.location.href = 'login.html';
}

function initLogoutButton() {
    const logoutButton = document.getElementById('logout-button');
    if (!logoutButton) {
        return;
    }

    logoutButton.addEventListener('click', () => {
        logoutUser();
    });
}

function getRequestHeaders(token) {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return headers;
}

function setPlacesStatus(message, extraClass = 'status-message') {
    const statusBox = document.getElementById('places-status');
    if (!statusBox) {
        return;
    }

    statusBox.textContent = message;
    statusBox.className = `form-message ${extraClass}`;
    statusBox.hidden = false;
}

function hidePlacesStatus() {
    const statusBox = document.getElementById('places-status');
    if (!statusBox) {
        return;
    }

    statusBox.hidden = true;
}

function buildPlaceLocation(place) {
    const normalizedTitle = (place.title || '').trim().toLowerCase();
    return PLACE_LOCATION_LABELS[normalizedTitle] || 'Location available on request';
}

function getPlaceImageSrc(place) {
    const normalizedTitle = (place.title || '').trim().toLowerCase();
    return PLACE_IMAGE_MAP[normalizedTitle] || 'images/places/demo-loft.png';
}

function createPlaceCard(place, index) {
    const article = document.createElement('article');
    const media = document.createElement('div');
    const mediaImage = document.createElement('img');
    const content = document.createElement('div');
    const title = document.createElement('h3');
    const location = document.createElement('p');
    const price = document.createElement('p');
    const description = document.createElement('p');
    const detailsLink = document.createElement('a');

    article.className = 'place-card';
    article.dataset.price = String(place.price);
    media.className = 'card-media';
    mediaImage.src = getPlaceImageSrc(place);
    mediaImage.alt = `${place.title} preview`;
    media.appendChild(mediaImage);
    content.className = 'card-content';
    title.textContent = place.title;
    location.className = 'place-meta';
    location.textContent = buildPlaceLocation(place);
    price.className = 'place-price';
    price.textContent = `$${Number(place.price).toFixed(2)} / night`;
    description.textContent = place.description || 'No description provided for this place yet.';
    detailsLink.href = `place.html?id=${encodeURIComponent(place.id)}`;
    detailsLink.className = 'details-button';
    detailsLink.textContent = 'View Details';
    detailsLink.addEventListener('click', () => {
        saveCurrentPlaceId(place.id);
    });

    content.appendChild(title);
    content.appendChild(location);
    content.appendChild(price);
    content.appendChild(description);
    content.appendChild(detailsLink);
    article.appendChild(media);
    article.appendChild(content);

    return article;
}

function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) {
        return;
    }

    placesList.innerHTML = '';

    if (!places.length) {
        setPlacesStatus('No places match the selected price.', 'empty-message');
        return;
    }

    hidePlacesStatus();
    places.forEach((place, index) => {
        placesList.appendChild(createPlaceCard(place, index));
    });
}

function applyPriceFilter() {
    const placesList = document.getElementById('places-list');
    const priceFilter = document.getElementById('price-filter');

    if (!placesList || !priceFilter) {
        return;
    }

    const selectedValue = priceFilter.value;
    const cards = placesList.querySelectorAll('.place-card');
    let visibleCount = 0;

    cards.forEach((card) => {
        const price = Number(card.dataset.price);
        const matches = selectedValue === 'all' || price <= Number(selectedValue);
        card.style.display = matches ? '' : 'none';
        if (matches) {
            visibleCount += 1;
        }
    });

    if (!cards.length) {
        return;
    }

    if (visibleCount === 0) {
        setPlacesStatus('No places match the selected price.', 'empty-message');
    } else {
        hidePlacesStatus();
    }
}

function initPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    if (!priceFilter) {
        return;
    }

    priceFilter.addEventListener('change', () => {
        applyPriceFilter();
    });
}

async function fetchPlaces(token) {
    const response = await fetch(`${API_BASE_URL}/places/`, {
        method: 'GET',
        headers: getRequestHeaders(token)
    });

    if (!response.ok) {
        throw new Error('Unable to load places from the API.');
    }

    return response.json();
}

function getPlaceIdFromURL() {
    const searchParams = new URLSearchParams(window.location.search);
    return searchParams.get('id');
}

function saveCurrentPlaceId(placeId) {
    if (!placeId) {
        return;
    }

    localStorage.setItem(PLACE_STORAGE_KEY, placeId);
}

function getStoredPlaceId() {
    return localStorage.getItem(PLACE_STORAGE_KEY);
}

function updateContextualNavLinks(placeId) {
    if (!placeId) {
        return;
    }

    saveCurrentPlaceId(placeId);

    document.querySelectorAll('.place-nav-link').forEach((link) => {
        link.href = `place.html?id=${encodeURIComponent(placeId)}`;
    });

    document.querySelectorAll('.review-nav-link').forEach((link) => {
        link.href = `add_review.html?id=${encodeURIComponent(placeId)}`;
    });
}

async function initContextualNavLinks() {
    const knownPlaceId = getPlaceIdFromURL() || getStoredPlaceId();
    if (knownPlaceId) {
        updateContextualNavLinks(knownPlaceId);
        return;
    }

    try {
        const places = await fetchPlaces(getCookie('token'));
        if (places.length) {
            updateContextualNavLinks(places[0].id);
        }
    } catch (error) {
        return;
    }
}

async function fetchPlaceDetails(token, placeId) {
    const response = await fetch(`${API_BASE_URL}/places/${encodeURIComponent(placeId)}`, {
        method: 'GET',
        headers: getRequestHeaders(token)
    });

    if (!response.ok) {
        throw new Error('Unable to load the selected place.');
    }

    return response.json();
}

function setPlaceStatus(message, extraClass = 'status-message') {
    const statusBox = document.getElementById('place-status');
    if (!statusBox) {
        return;
    }

    statusBox.textContent = message;
    statusBox.className = `form-message ${extraClass}`;
    statusBox.hidden = false;
}

function hidePlaceStatus() {
    const statusBox = document.getElementById('place-status');
    if (!statusBox) {
        return;
    }

    statusBox.hidden = true;
}

function setReviewMessage(message, extraClass = 'status-message') {
    const messageBox = document.getElementById('review-message');
    if (!messageBox) {
        return;
    }

    messageBox.textContent = message;
    messageBox.className = `form-message ${extraClass}`;
    messageBox.hidden = false;
}

function hideReviewMessage() {
    const messageBox = document.getElementById('review-message');
    if (!messageBox) {
        return;
    }

    messageBox.hidden = true;
}

function createDetailCard(titleText, bodyNode) {
    const article = document.createElement('article');
    const title = document.createElement('h3');

    article.className = 'place-info';
    title.textContent = titleText;
    article.appendChild(title);
    article.appendChild(bodyNode);

    return article;
}

function buildHostName(owner) {
    if (!owner) {
        return 'Host information unavailable';
    }

    const fullName = `${owner.first_name || ''} ${owner.last_name || ''}`.trim();
    return fullName || owner.email || owner.id;
}

function buildReviewerName(review) {
    if (review.author) {
        const fullName = `${review.author.first_name || ''} ${review.author.last_name || ''}`.trim();
        return fullName || review.author.email || review.author.id;
    }

    return review.user_id;
}

function displayPlaceDetails(place) {
    const hero = document.getElementById('place-hero');
    const heroCopy = document.getElementById('place-hero-copy');
    const heroImage = document.getElementById('place-hero-image');
    const detailsSection = document.getElementById('place-details');
    const detailsContent = document.getElementById('place-details-content');
    const reviewsSection = document.getElementById('reviews-section');
    const reviewsList = document.getElementById('reviews-list');
    const addReviewLink = document.getElementById('add-review-link');
    const token = getCookie('token');
    const hostParagraph = document.createElement('p');
    const descriptionParagraph = document.createElement('p');
    const locationParagraph = document.createElement('p');
    const amenitiesList = document.createElement('ul');
    const heroPhoto = document.createElement('img');

    heroCopy.innerHTML = '';
    detailsContent.innerHTML = '';
    reviewsList.innerHTML = '';
    heroImage.innerHTML = '';

    const eyebrow = document.createElement('p');
    eyebrow.className = 'eyebrow';
    eyebrow.textContent = 'Selected stay';
    const title = document.createElement('h2');
    title.textContent = place.title;
    const price = document.createElement('p');
    price.className = 'place-price';
    price.textContent = `$${Number(place.price).toFixed(2)} / night`;
    const summary = document.createElement('p');
    summary.textContent = place.description || 'No description provided for this place yet.';
    heroCopy.appendChild(eyebrow);
    heroCopy.appendChild(title);
    heroCopy.appendChild(price);
    heroCopy.appendChild(summary);

    heroPhoto.src = getPlaceImageSrc(place);
    heroPhoto.alt = `${place.title} hero image`;
    heroImage.className = 'hero-image';
    heroImage.appendChild(heroPhoto);

    hostParagraph.textContent = buildHostName(place.owner);
    descriptionParagraph.textContent = place.description || 'No description provided for this place yet.';
    locationParagraph.textContent = buildPlaceLocation(place);
    amenitiesList.className = 'amenities-list';

    if (place.amenities && place.amenities.length) {
        place.amenities.forEach((amenity) => {
            const item = document.createElement('li');
            item.textContent = amenity.name;
            amenitiesList.appendChild(item);
        });
    } else {
        amenitiesList.classList.add('is-plain');
        const item = document.createElement('li');
        item.textContent = 'No amenities listed.';
        amenitiesList.appendChild(item);
    }

    detailsContent.appendChild(createDetailCard('Host', hostParagraph));
    detailsContent.appendChild(createDetailCard('Description', descriptionParagraph));
    detailsContent.appendChild(createDetailCard('Location', locationParagraph));
    detailsContent.appendChild(createDetailCard('Amenities', amenitiesList));

    if (place.reviews && place.reviews.length) {
        place.reviews.forEach((review) => {
            const article = document.createElement('article');
            const reviewHeader = document.createElement('div');
            const heading = document.createElement('h3');
            const rating = document.createElement('p');
            const comment = document.createElement('p');
            const author = document.createElement('p');

            article.className = 'review-card';
            reviewHeader.className = 'review-header';
            heading.textContent = 'Guest review';
            rating.className = 'rating';
            rating.textContent = `${Number(review.rating)} / 5`;
            comment.textContent = review.text || 'No review comment provided.';
            author.className = 'review-author';
            author.textContent = `By ${buildReviewerName(review)}`;

            reviewHeader.appendChild(heading);
            reviewHeader.appendChild(rating);
            article.appendChild(reviewHeader);
            article.appendChild(comment);
            article.appendChild(author);
            reviewsList.appendChild(article);
        });
    } else {
        const emptyReview = document.createElement('article');
        const emptyText = document.createElement('p');

        emptyReview.className = 'review-card';
        emptyText.textContent = 'No reviews yet for this place.';
        emptyReview.appendChild(emptyText);
        reviewsList.appendChild(emptyReview);
    }

    if (token) {
        addReviewLink.hidden = false;
        addReviewLink.href = `add_review.html?id=${encodeURIComponent(place.id)}`;
    } else {
        addReviewLink.hidden = true;
    }

    hero.hidden = false;
    detailsSection.hidden = false;
    reviewsSection.hidden = false;
    hidePlaceStatus();
}

async function initPlacePage() {
    const detailsSection = document.getElementById('place-details');
    if (!detailsSection) {
        return;
    }

    const token = updateAuthenticationUI();
    const placeId = getPlaceIdFromURL();

    if (!placeId) {
        setPlaceStatus('No place id was provided in the URL.', 'error-message');
        return;
    }

    setPlaceStatus('Loading place details...');

    try {
        const place = await fetchPlaceDetails(token, placeId);
        updateContextualNavLinks(placeId);
        displayPlaceDetails(place);
    } catch (error) {
        setPlaceStatus(error.message, 'error-message');
    }
}

async function submitReview(token, placeId, userId, reviewText, rating) {
    const response = await fetch(`${API_BASE_URL}/reviews/`, {
        method: 'POST',
        headers: getRequestHeaders(token),
        body: JSON.stringify({
            text: reviewText,
            rating,
            user_id: userId,
            place_id: placeId
        })
    });

    let data = null;
    try {
        data = await response.json();
    } catch (error) {
        data = null;
    }

    if (!response.ok) {
        const message = data && data.message ? data.message : 'Failed to submit review.';
        throw new Error(message);
    }

    return data;
}

function requireAuthentication() {
    const token = getCookie('token');
    if (!token) {
        window.location.href = 'index.html';
        return null;
    }

    return token;
}

function initAddReviewPage() {
    const reviewForm = document.getElementById('review-form');
    if (!reviewForm) {
        return;
    }

    const token = requireAuthentication();
    if (!token) {
        return;
    }

    updateAuthenticationUI();
    hideReviewMessage();

    const placeId = getPlaceIdFromURL();
    const userId = getCookie('user_id');
    const reviewHeading = document.getElementById('review-heading');
    const reviewSubheading = document.getElementById('review-subheading');

    if (!placeId) {
        setReviewMessage('No place id was provided in the URL.', 'error-message');
        reviewForm.classList.add('is-hidden');
        return;
    }

    reviewHeading.textContent = 'Add a review for this place';
    reviewSubheading.textContent = 'Loading selected place...';

    if (!userId) {
        setReviewMessage('Your session is missing the user id required by the API. Please log in again.', 'error-message');
        reviewForm.classList.add('is-hidden');
        return;
    }

    fetchPlaceDetails(token, placeId)
        .then((place) => {
            reviewHeading.textContent = `Add a review for ${place.title}`;
            reviewSubheading.textContent = `Submitting feedback for ${place.title}.`;
            updateContextualNavLinks(place.id);
        })
        .catch(() => {
            reviewHeading.textContent = 'Add a review for this place';
            reviewSubheading.textContent = `Submitting feedback for place ${placeId}.`;
        });

    reviewForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        hideReviewMessage();

        const submitButton = reviewForm.querySelector('button[type="submit"]');
        const ratingInput = document.getElementById('rating');
        const reviewTextInput = document.getElementById('review-text');
        const reviewText = reviewTextInput.value.trim();

        if (!ratingInput.value) {
            setReviewMessage('Select a rating before submitting.', 'error-message');
            ratingInput.focus();
            return;
        }

        if (!reviewText) {
            setReviewMessage('Write a review before submitting.', 'error-message');
            reviewTextInput.focus();
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Submitting...';

        try {
            await submitReview(token, placeId, userId, reviewText, Number(ratingInput.value));
            setReviewMessage('Review submitted successfully.', 'status-message');
            reviewForm.reset();
        } catch (error) {
            setReviewMessage(error.message, 'error-message');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Submit Review';
        }
    });
}

async function initIndexPage() {
    const placesList = document.getElementById('places-list');
    if (!placesList) {
        return;
    }

    const token = updateAuthenticationUI();
    initPriceFilter();
    setPlacesStatus('Loading places...');

    try {
        allPlaces = await fetchPlaces(token);
        displayPlaces(allPlaces);
        applyPriceFilter();
    } catch (error) {
        allPlaces = [];
        placesList.innerHTML = '';
        setPlacesStatus(error.message, 'error-message');
    }
}

function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) {
        return;
    }

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        clearLoginError();

        const submitButton = loginForm.querySelector('button[type="submit"]');
        const emailInput = document.getElementById('email');
        const passwordInput = document.getElementById('password');

        if (!emailInput.checkValidity()) {
            showLoginError('Enter a valid email address.');
            emailInput.focus();
            return;
        }

        if (!passwordInput.value.trim()) {
            showLoginError('Password is required.');
            passwordInput.focus();
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';

        try {
            const data = await loginUser(emailInput.value.trim(), passwordInput.value);
            setCookie('token', data.access_token);
            setCookie('user_id', data.user_id);
            setCookie('user_email', data.email);
            window.location.href = 'index.html';
        } catch (error) {
            showLoginError(error.message);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Login';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    updateAuthenticationUI();
    initLogoutButton();
    initContextualNavLinks();
    initLoginForm();
    initIndexPage();
    initPlacePage();
    initAddReviewPage();
});
