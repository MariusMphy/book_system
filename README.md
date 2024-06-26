## Project: Book Recommendation System

View page on port 5017: 
<a href="http://127.0.0.1:5017" target="_blank">http://127.0.0.1:5017</a>

### Stage 1: Basic Book Catalog

Objective: Create an application to manage a book catalog.

Requirements:
- Implement classes for users, books, authors, genre, review, user_favorite and user_read_list.
- create system fo automatically fill db with data (can be fictional).


### Stage 2: User Ratings and Persistence

Objective: Add user ratings and persist data.

Requirements:
- Implement user registration and login using a simple authentication system.
- Use SQLAlchemy to store user data, books, ratings and other information in a database.


### Stage 3: Book Search and Filters

Objective: Enhance the catalog with search and filter functionalities.

Requirements:
- Implement functions to search books by title, author or genre.
- Allow users to filter books based on rating and other fields.
- Save search results in JSON format (or in db).

### Stage 4: Recommender System

Objective: Develop a recommendation engine for books.
Requirements:
- Implement a basic recommendation algorithm (e.g., collaborative filtering).
- Allow users to view personalized book recommendations.
- Use Flask to create a web interface for the application.

### Stage 5: Deployment and API Integration
    
Objective: Deploy the web application and integrate external APIs.

Requirements:
- Containerize the application using Docker.
- Deploy the application to a cloud platform.
- Integrate with an external book API (e.g., Google Books API) to fetch additional book details.