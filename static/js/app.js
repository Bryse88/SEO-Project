//Note: I changed the button variable to be three different buttons, saveButton, editButton, and deleteButton for styling in CSS

document.getElementById('noteForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const noteInput = document.getElementById('noteInput');
    const noteText = noteInput.value;

    if (noteText.trim()) {
        addNoteToList(noteText, 'You');
        saveNoteToServer(noteText);
        noteInput.value = '';
    }
});

let noteId = 0;

function addNoteToList(noteText, author) {
    const notesList = document.getElementById('notesList');
    const li = document.createElement('li');

    const noteSpan = document.createElement('p');
    noteSpan.textContent = `${noteText} (by ${author})`;
    noteSpan.classList.add('noteSpan');

    const noteInput = document.createElement('input');
    noteInput.type = 'text';
    noteInput.value = noteText;
    noteInput.style.display = 'none';

    const buttonsDiv = document.createElement('div');
    buttonsDiv.classList.add('buttonsDiv');

    const deleteButton = document.createElement('deleteButton'); // Here for example
    deleteButton.textContent = 'Delete';
    deleteButton.id = `deleteButton-${noteId}`;
    deleteButton.classList.add('deleteButton'); // Add this line
    deleteButton.addEventListener('click', function() {
        deleteNoteFromServer(noteText);
        li.remove();
    });

    const editButton = document.createElement('editButton');
    editButton.textContent = 'Edit';
    editButton.id = `editButton-${noteId}`;
    editButton.classList.add('editButton'); // Add this line
    editButton.addEventListener('click', function() {
        noteSpan.style.display = 'none';
        noteInput.style.display = 'inline-block';
        editButton.style.display = 'none';
        saveButton.style.display = 'inline-block';
    });

    const saveButton = document.createElement('saveButton');
    saveButton.textContent = 'Save';
    saveButton.classList.add('saveButton');
    saveButton.style.display = 'none';
    saveButton.addEventListener('click', function() {
        const newNoteText = noteInput.value;
        if (newNoteText && newNoteText.trim() !== '' && newNoteText !== noteText) {
            updateNoteOnServer(noteText, newNoteText);
            noteSpan.textContent = `${newNoteText} (by ${author})`;
            noteText = newNoteText; 
        }
        noteSpan.style.display = 'inline-block';
        noteInput.style.display = 'none';
        editButton.style.display = 'inline-block';
        saveButton.style.display = 'none';
    });

    li.appendChild(noteSpan);
    li.appendChild(noteInput);
    buttonsDiv.appendChild(editButton);
    buttonsDiv.appendChild(saveButton);
    buttonsDiv.appendChild(deleteButton);
    li.appendChild(buttonsDiv);
    notesList.appendChild(li);

    noteId++;
}

function saveNoteToServer(noteText) {
    fetch('/add_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ note: noteText })
    }).then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function deleteNoteFromServer(noteText) {
    fetch('/delete_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ note: noteText })
    }).then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

function updateNoteOnServer(oldNoteText, newNoteText) {
    fetch('/update_note', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ oldNote: oldNoteText, newNote: newNoteText })
    }).then(response => response.json())
    .then(data => {
        console.log(data);
    });
}
//Added everything below this for collaboration.
function fetchNotes() {
    fetch('/get_notes')
        .then(response => response.json())
        .then(data => {
            const notesList = document.getElementById('notesList');
            notesList.innerHTML = ''; // Clear existing notes
            data.notes.forEach(note => addNoteToList(note.text, note.author));
        });
}

// Fetch notes initially and then periodically
window.onload = function() {
    fetchNotes();
    setInterval(fetchNotes, 5000); // Fetch notes every 5 seconds
};

document.getElementById('inviteCollaboratorBtn').addEventListener('click', function() {
    const invitee = document.getElementById('inviteeInput').value;
    inviteCollaborator(invitee);
});

function inviteCollaborator(invitee) {
    fetch('/invite_collaborator', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ invitee: invitee })
    }).then(response => response.json())
    .then(data => {
        console.log(data);
    });
}
