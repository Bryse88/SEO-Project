# SmartScheduler: AI-Powered Collaborative Calendar and Task Management

<<<<<<< HEAD
## Contributing:

Bryson Turner(FullStack), Lap Pham (Frontend), Adam Bataineh(backend) 

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Usage](#usage)
    1. [Register and Login](#register-and-login)
    2. [Create and Manage Events](#create-and-manage-events)
    3. [View and Manage Notes](#view-and-manage-notes)
    4. [Collaborate with Team Members](#collaborate-with-team-members)
4. [Frameworks and Libraries](#frameworks-and-libraries)
5. [Languages Used](#languages-used)
6. [Collaboration Features](#collaboration-features)

## Overview

SmartScheduler is an advanced calendar and task management application designed to enhance productivity and efficiency. Utilizing the power of Google Calendar API, Flask, GCP, and OpenAI's GPT-3, SmartScheduler offers intelligent scheduling, categorization, and collaboration features. The application helps users manage their time more effectively by automatically suggesting optimal time slots for new events based on existing schedules and priorities. Additionally, it provides an integrated notes feature to keep all your important information in one place.

## Features

- **Event Prioritization**: Assign categorization levels to events (projects, breaks, family) and schedule them accordingly.
- **AI-Powered Scheduling**: Leverage OpenAI's GPT-3 to analyze your schedule and suggest the best time slots for new events.
- **Collaboration Features**: Share calendars and collaborate with team members in real-time.
- **Integrated Notes**: Store and view notes directly on the website, linked with your calendar events.
=======
## Overview

SmartScheduler is an advanced calendar and task management application designed to enhance productivity and efficiency. Utilizing the power of Google Calendar API, Flask, GCP, and OpenAI's GPT-3, SmartScheduler offers intelligent scheduling, prioritization, and collaboration features. The application helps users manage their time more effectively by automatically suggesting optimal time slots for new events based on existing schedules and priorities.

## Features

- **Event Prioritization**: Assign importance levels to events (High, Medium, Low) and schedule them accordingly.
- **AI-Powered Scheduling**: Leverage OpenAI's GPT-3 to analyze your schedule and suggest the best time slots for new events.
- **Natural Language Processing**: Create events using natural language commands.
- **Comprehensive Analytics Dashboard**: Gain insights into time management, including time spent on high-priority tasks versus low-priority ones, and identify the busiest times of the day.
- **Collaboration Features**: Share calendars and collaborate with team members in real-time.
- **Email Notifications**: Get automated email reminders for upcoming events.
- **Mobile Support**: Access and manage your schedule on the go with a responsive design.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Bryse88/SEO-Project.git
   cd SEO-Project
2. **Create and Activate a Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   python3 -m venv venv
   source venv/bin/activate
   
3. **Create and Activate a Virtual Environment

   ```bash
   python3 -m venv venv
   source venv/bin/activate

4. **Install Dependencies

   ```bash
   pip install -r requirements.txt


5. **Set Up Environment Variables**

   Create a `.env` file in the project root with the following content:

   ```plaintext
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   OPENAI_API_KEY=your-openai-api-key

6. **Run the Application**

   ```bash
   flask run

7. **Access the Application

  Open your web browser and navigate to http://localhost:5050.
>>>>>>> main


## Usage

1. **Register and Login**

   - Register a new account and log in to access the main features.

2. **Create and Manage Events**

   - Use the event creation form to add new events to your calendar, specifying the title, description, start and end times, and importance level.
   - Optionally, allow OpenAI to suggest the best time for your event based on your current schedule.

<<<<<<< HEAD
3. **View and Manage Notes**

   - Create, view, and organize your notes directly on the website.
   - Link notes with calendar events for easy reference and better organization.
=======
3. **View and Analyze Your Schedule**

   - Use the analytics dashboard to get insights into your time management and adjust your schedule for optimal efficiency.
>>>>>>> main

4. **Collaborate with Team Members**

   - Share your calendar with team members and collaborate on events in real-time.

<<<<<<< HEAD

## Frameworks and Libraries

- **Flask**: A lightweight WSGI web application framework used for developing the web application.
- **Flask-OAuthlib**: An OAuth library for Flask used to handle Google OAuth authentication.
- **Flask-Bootstrap**: Integrates Bootstrap with Flask to make the front-end responsive and modern.
- **Google API Client**: A Python client library for accessing Google APIs, used for interacting with Google Calendar.
- **OpenAI API**: Utilized for AI-powered scheduling and natural language processing to suggest optimal time slots and manage tasks.
- **Jinja2**: A templating engine for Python used by Flask to render HTML templates dynamically.
- **Werkzeug**: A comprehensive WSGI web application library used by Flask for handling requests and responses.
- **python-dotenv**: A library to load environment variables from a `.env` file.


## Languages Used

- **Python**: The primary language used for the backend development, including Flask for the web framework, interacting with APIs, and handling business logic.
- **HTML**: Used for structuring the web pages.
- **CSS**: Used for styling the web pages to ensure they are visually appealing and responsive.
- **JavaScript**: Used for enhancing the interactivity of the web pages.


=======
>>>>>>> main
## Collaboration Features

- **Shared Calendars**: Create and manage shared calendars for teams and projects.
- **Real-Time Updates**: Ensure that any changes to the calendar are immediately reflected across all user devices.
- **Task Management Integration**: Sync tasks and deadlines with the calendar for seamless project management.
<<<<<<< HEAD
=======


>>>>>>> main
