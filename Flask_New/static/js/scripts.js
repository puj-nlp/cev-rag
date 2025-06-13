document.getElementById('chatinput').addEventListener('submit', function(event) {
    event.preventDefault();
    var input = document.querySelector('#chatinput input');
    var message = input.value;
    if (message.trim()) {
        var newMessage = document.createElement('div');
        newMessage.className = 'message user';
        newMessage.textContent = message;
        document.getElementById('chatlog').appendChild(newMessage);
        input.value = '';  // Clear input after sending

        // Remove welcome message (if it exists)
        const welcomeMessage = document.getElementById('welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
    }
});