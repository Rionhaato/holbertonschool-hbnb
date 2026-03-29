const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';
let allPlaces = [];

function setCookie(name, value, maxAgeSeconds = 86400) {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; SameSite=Lax`;
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
    const authLinks = document.querySelectorAll('.auth-link');

    authLinks.forEach((link) => {
        link.classList.toggle('is-hidden', Boolean(token));
    });

    return token;
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
    const latitude = Number(place.latitude).toFixed(4);
    const longitude = Number(place.longitude).toFixed(4);
    return `${latitude}, ${longitude}`;
}

function createPlaceCard(place, index) {
    const article = document.createElement('article');
    const mediaClasses = ['coastal-stay', 'urban-suite', 'lake-cabin'];
    const mediaClass = mediaClasses[index % mediaClasses.length];
    const media = document.createElement('div');
    const content = document.createElement('div');
    const title = document.createElement('h3');
    const location = document.createElement('p');
    const price = document.createElement('p');
    const description = document.createElement('p');
    const detailsLink = document.createElement('a');

    article.className = 'place-card';
    article.dataset.price = String(place.price);
    media.className = `card-media ${mediaClass}`;
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
    initLoginForm();
    initIndexPage();
});
