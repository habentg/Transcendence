const signupBtn = document.getElementById('signupBtn');
const signinBtn = document.getElementById('signinBtn');

signupBtn.addEventListener('click', () => {
    window.location.href ='http://127.0.0.1/signup/';
})

signinBtn.addEventListener('click', () => {
    window.location.href ='http://127.0.0.1/signin/';
})