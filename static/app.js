
{% extends "layout.html" %}
{% block title %}Notes{% endblock %}
{% block content %}
<h1>Notes App</h1>
<form id="noteForm">
    <textarea id="noteInput" placeholder="Write your note here..."></textarea>
    <button type="submit">Add Note</button>
</form>
<ul id="notesList"></ul>
{% endblock %}
