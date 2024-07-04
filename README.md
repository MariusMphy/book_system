# Project: Book Recommendation System

## Functionality:

### Stage 1: Main access. All users can:
1. Access home page, list of books, search page and more will be added.
2. Check book details (Title, Author, genres, rating, reviews).
3. 


### Stage 2: User area

1. User is able to register, login and logout.
2. When logged in, user is able to:
    - View profile, edit profile, change password.
    - In book details additionally see his rating and rate or update rating, see if book is in his read list or add to it, view review or write/update one.
    - See his read list, remove from it.
    - See his reviews, update them.


### Stage 3: Admin area
1. When logged in, admin, in addition to user options, is able to:
    - View administrator home page.
    - access add author, add book, add multiple books pages.
    - add book page allows to add new book to DB, creating title, selecting author and assigning genres.
    - add multiple books from prepared .csv file.
    - access Flask-admin page with all collections.


### Stage 4: Book Search and Filters

Objective: Enhance the catalog with search and filter functionalities.

Requirements:
- Implement functions to search books by title, author or genre.
- Allow users to filter books based on rating and other fields.
- Save search results in JSON format (or in db).

### Stage 5: Recommender System

Objective: Develop a recommendation engine for books.
Requirements:
- Implement a basic recommendation algorithm (e.g., collaborative filtering).
- Allow users to view personalized book recommendations.
- Use AI for advanced recommendations (optional)

### Stage 6: Deployment and API Integration
    
Objective: Deploy the web application and integrate external APIs.

Requirements:
- Containerize the application using Docker.
- Deploy the application to a cloud platform.
- Integrate with an external book API (e.g., Google Books API) to fetch additional book details.

### Stage 7: Integrate with all lithuanian book stores (optional)
   
Objective: Integrate external lithuanian APIs.
