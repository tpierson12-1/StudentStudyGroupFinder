# Student Study Group Finder

gtgrrhr

## Project Overview

Student Study Group Finder is a group project designed to help students find and join study groups based on shared classes, topics, and learning needs. The goal of the project is to make it easier for students to connect with others, organize study sessions, and collaborate more effectively.

## Features

- User account system
- Tutor support
- Study group creation and membership
- Topics connected to study groups
- Session scheduling
- RSVP tracking for sessions
- Sample data for testing
- Demo SQL queries for common project functions

## Tools Used

- HTML
- CSS
- Python
- FastAPI
- MySQL
- MySQL Workbench

## Database Features

The database currently includes tables for:

- APP_USER
- Tutor
- STUDY_GROUP
- GroupMembership
- Topic
- GroupTopic
- Location
- Session
- SessionRSVP

The SQL file also includes:

- sample insert data
- demo queries for testing
- foreign key relationships
- many-to-many relationship tables with composite primary keys

## How to Run the Front End

1. Open the project folder in VS Code
2. Start a local server in the project folder:
   ```bash
   python3 -m http.server 8000
   ```
