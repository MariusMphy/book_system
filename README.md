
# Book Recommendation System

Book Recommendation System is web application, designed for book enthusiasts to discover, rate and review books.

## Key features of Book Recommendation System:
1. Book Catalog: Users can search for books, view information and read reviews by other members.
2. User Reviews and Ratings: Members can write reviews and rate books they have read, providing personal insights and feedback.
3. Bookshelves: Users can organize their reading list by adding or removing books as "Want to Read."
4. Recommendations: Based on user ratings, Book Recommendation System offers personalized book recommendations.

## Guide to explore the features:
1. Register as "Admin" (this option is implemented solely for demonstration purpose).
2. Login as "Admin", go to "Fill DB" and use all three options to fill database with data (for demonstration purpose).
3. Explore admin options: "Add author", "Add book", "View users", Flask-admin.
4. Logout or login to explore regular or registered user options.

### Administrator has exclusive rights to:
- add new author
- add new book
- view all users
- fill database (only for demonstration purpose)
- access Flask-admin

### Regular user has options to:
- register
- view top books
- view all books in database
- view each book's information (title, author, genres, rating, read listed count, reviews)
- view rated books
- view reviewed books
- view read listed books
- search for books; filter and sort results

### Registered user in addition to regular user options is able to:
- login
- access profile information
- edit profile
- change password
- rate books, change rating, view self rated books
- add to read list, remove from read list, view personal read list
- write review, update review, view personal reviews
- get list of recommended books based on personal ratings
- view personal search history


### How to use:

1. **Clone the repository**:
    ```sh
    git clone https://github.com/MariusMphy/book_system.git
    cd book_system
    ```

2. **Set up the virtual environment:**:
    ```sh
    python -m venv venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory of the project and add the following variables:
    ```
    book_system_key=your_key_here
    ```

5. **Run the application**:
    ```sh
    python run.py # or py run.py
    ```

6. **Access the application**:
    In your web browser go to: `http://127.0.0.1:5000/`.

7. **Deployed for limited time** at https://mariusmphy.pythonanywhere.com/