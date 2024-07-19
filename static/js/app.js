document.getElementById('noteForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const noteInput = document.getElementById('noteInput');
    const noteText = noteInput.value;

    if (noteText.trim()) {
        addNoteToList(noteText);
        saveNoteToServer(noteText);
        noteInput.value = '';
    }
});

let noteId = 0;

function addNoteToList(noteText) {
    const notesList = document.getElementById('notesList');
    const li = document.createElement('li');

    const noteSpan = document.createElement('p');
    noteSpan.textContent = noteText;
    noteSpan.classList.add('noteSpan'); // Add this line

    const noteInput = document.createElement('input');
    noteInput.type = 'text';
    noteInput.value = noteText;
    noteInput.style.display = 'none';

    const buttonsDiv = document.createElement('div');
    buttonsDiv.classList.add('buttonsDiv');

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.id = `deleteButton-${noteId}`;
    deleteButton.classList.add('deleteButton');
    deleteButton.addEventListener('click', function() {
        deleteNoteFromServer(noteText);
        li.remove();
    });

    const editButton = document.createElement('button');
    editButton.textContent = 'Edit';
    editButton.id = `editButton-${noteId}`;
    editButton.classList.add('editButton');
    editButton.addEventListener('click', function() {
        noteSpan.style.display = 'none';
        noteInput.style.display = 'inline-block';
        editButton.style.display = 'none';
        saveButton.style.display = 'inline-block';
    });

    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save';
    saveButton.classList.add('saveButton');
    saveButton.style.display = 'none';
    saveButton.addEventListener('click', function() {
        const newNoteText = noteInput.value;
        if (newNoteText && newNoteText.trim() !== '' && newNoteText !== noteText) {
            updateNoteOnServer(noteText, newNoteText);
            noteSpan.textContent = newNoteText;
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

window.onload = function() {
    fetch('/get_notes')
        .then(response => response.json())
        .then(data => {
            data.notes.forEach(note => addNoteToList(note));
        });
};
