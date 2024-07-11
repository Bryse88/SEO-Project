
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

function addNoteToList(noteText) {
    const notesList = document.getElementById('notesList');
    const li = document.createElement('li');
    li.textContent = noteText;

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', function() {
        deleteNoteFromServer(noteText);
        li.remove();
    });

    li.appendChild(deleteButton);
    notesList.appendChild(li);
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

window.onload = function() {
    fetch('/get_notes')
        .then(response => response.json())
        .then(data => {
            data.notes.forEach(note => addNoteToList(note));
        });
};
