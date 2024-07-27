/*
     ------ 42 Oauth --------
     √ 42 Doc: https://api.intra.42.fr/apidoc/guides/web_application_flow

*/
fourtyTwoAuthBtn = document.querySelector('.fourty-two');

fourtyTwoAuthBtn.addEventListener('click', redirectToOauth)

function redirectToOauth() {
    const clientId = window.clientId; // 
    console.log(clientId)
    const redirectUri = 'http://localhost/oauth/callback/';
    const authorizationEndpoint = 'https://api.intra.42.fr/oauth/authorize';
    const responseType = 'code';
    const scope = 'public';

    const authUrl = `${authorizationEndpoint}?response_type=${responseType}&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}`;
    
    window.location.href = authUrl;
}