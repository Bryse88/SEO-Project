# SmartScheduler: AI-Powered Collaborative Calendar and Task Management

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


## Usage

1. **Register and Login**

   - Register a new account and log in to access the main features.

2. **Create and Manage Events**

   - Use the event creation form to add new events to your calendar, specifying the title, description, start and end times, and importance level.
   - Optionally, allow OpenAI to suggest the best time for your event based on your current schedule.

3. **View and Analyze Your Schedule**

   - Use the analytics dashboard to get insights into your time management and adjust your schedule for optimal efficiency.

4. **Collaborate with Team Members**

   - Share your calendar with team members and collaborate on events in real-time.

## Collaboration Features

- **Shared Calendars**: Create and manage shared calendars for teams and projects.
- **Real-Time Updates**: Ensure that any changes to the calendar are immediately reflected across all user devices.
- **Task Management Integration**: Sync tasks and deadlines with the calendar for seamless project management.


