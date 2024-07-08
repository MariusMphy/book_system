books_list =[
    {"Author": "Fyodor Dostoevsky", "Title": "The Idiot", "Genres": "Fiction, Classic, Psychological"},
    {"Author": "Herman Melville", "Title": "Bartleby, the Scrivener", "Genres": "Fiction, Classic, Novella"},
    {"Author": "George Eliot", "Title": "Middlemarch", "Genres": "Fiction, Classic, Historical"},
    {"Author": "Charlotte Brontë", "Title": "Jane Eyre", "Genres": "Fiction, Classic, Romance"},
    {"Author": "William Faulkner", "Title": "The Sound and the Fury", "Genres": "Fiction, Classic, Modernist"},
    {"Author": "William Faulkner", "Title": "As I Lay Dying", "Genres": "Fiction, Classic, Modernist"},
    {"Author": "Joseph Heller", "Title": "Catch-22", "Genres": "Fiction, Classic, War"},
    {"Author": "J.D. Salinger", "Title": "The Catcher in the Rye", "Genres": "Fiction, Classic, Young Adult"},
    {"Author": "Jack London", "Title": "The Call of the Wild", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "Albert Camus", "Title": "The Plague", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Albert Camus", "Title": "The Fall", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Marcel Proust", "Title": "Swann's Way", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "J.K. Rowling", "Title": "Harry Potter Series", "Genres": "Fantasy, Fiction, Young Adult"},
    {"Author": "Emily Dickinson", "Title": "The Complete Poems of Emily Dickinson", "Genres": "Poetry, Classic, Collection"},
    {"Author": "Franz Kafka", "Title": "The Metamorphosis", "Genres": "Fiction, Classic, Novella"},
    {"Author": "F. Scott Fitzgerald", "Title": "Tender is the Night", "Genres": "Fiction, Classic, Tragedy"},
    {"Author": "Ernest Hemingway", "Title": "The Old Man and the Sea", "Genres": "Fiction, Classic, Novella"},
    {"Author": "John Steinbeck", "Title": "Of Mice and Men", "Genres": "Fiction, Classic, Novella"},
    {"Author": "Leo Tolstoy", "Title": "Resurrection", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Edith Wharton", "Title": "The Age of Innocence", "Genres": "Fiction, Classic, Romance"},
    {"Author": "Gustave Flaubert", "Title": "Sentimental Education", "Genres": "Fiction, Classic, Romance"},
    {"Author": "Charles Dickens", "Title": "David Copperfield", "Genres": "Fiction, Classic, Bildungsroman"},
    {"Author": "Thomas Mann", "Title": "The Magic Mountain", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Hermann Hesse", "Title": "Steppenwolf", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Harper Lee", "Title": "To Kill a Mockingbird", "Genres": "Fiction, Classic, Historical"},
    {"Author": "Leo Tolstoy", "Title": "Childhood, Boyhood, and Youth", "Genres": "Fiction, Classic, Bildungsroman"},
    {"Author": "Mark Twain", "Title": "The Adventures of Tom Sawyer", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "Henry James", "Title": "The Portrait of a Lady", "Genres": "Fiction, Classic, Romance"},
    {"Author": "Ralph Ellison", "Title": "Invisible Man", "Genres": "Fiction, Classic, Social Commentary"},
    {"Author": "James Baldwin", "Title": "Go Tell It on the Mountain", "Genres": "Fiction, Classic, Bildungsroman"},
    {"Author": "Vladimir Nabokov", "Title": "Lolita", "Genres": "Fiction, Classic, Psychological"},
    {"Author": "James Joyce", "Title": "Finnegans Wake", "Genres": "Fiction, Classic, Modernist"},
    {"Author": "Aldous Huxley", "Title": "Brave New World", "Genres": "Fiction, Dystopian, Classic"},
    {"Author": "Virginia Woolf", "Title": "Orlando", "Genres": "Fiction, Classic, Modernist"},
    {"Author": "Oscar Wilde", "Title": "The Picture of Dorian Gray", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Robert Louis Stevenson", "Title": "Treasure Island", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "George Orwell", "Title": "Animal Farm", "Genres": "Fiction, Allegory, Classic"},
    {"Author": "William Golding", "Title": "Lord of the Flies", "Genres": "Fiction, Allegory, Classic"},
    {"Author": "Edgar Allan Poe", "Title": "The Complete Tales and Poems of Edgar Allan Poe", "Genres": "Fiction, Classic, Collection"},
    {"Author": "Lewis Carroll", "Title": "Alice's Adventures in Wonderland", "Genres": "Fiction, Fantasy, Classic"},
    {"Author": "Miguel de Cervantes", "Title": "The Exemplary Novels of Cervantes", "Genres": "Fiction, Classic, Collection"},
    {"Author": "Marcel Proust", "Title": "Time Regained", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Thomas Hardy", "Title": "Tess of the d'Urbervilles", "Genres": "Fiction, Classic, Tragedy"},
    {"Author": "Joseph Conrad", "Title": "Lord Jim", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "Jack Kerouac", "Title": "On the Road", "Genres": "Fiction, Classic, Beat"},
    {"Author": "Herman Melville", "Title": "Billy Budd, Sailor", "Genres": "Fiction, Classic, Novella"},
    {"Author": "Arthur Miller", "Title": "The Crucible", "Genres": "Fiction, Classic, Play"},
    {"Author": "Kurt Vonnegut", "Title": "Slaughterhouse-Five", "Genres": "Fiction, Classic, War"},
    {"Author": "Mikhail Bulgakov", "Title": "The Master and Margarita", "Genres": "Fiction, Classic, Satire"},
    {"Author": "James Joyce", "Title": "Dubliners", "Genres": "Fiction, Classic, Collection"},
    {"Author": "Fyodor Dostoevsky", "Title": "Notes from Underground", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "Albert Camus", "Title": "The Myth of Sisyphus", "Genres": "Non-fiction, Classic, Philosophical"},
    {"Author": "Antoine de Saint-Exupéry", "Title": "The Little Prince", "Genres": "Fiction, Fantasy, Classic"},
    {"Author": "Ray Bradbury", "Title": "Fahrenheit 451", "Genres": "Fiction, Dystopian, Classic"},
    {"Author": "J.R.R. Tolkien", "Title": "The Hobbit", "Genres": "Fiction, Fantasy, Classic"},
    {"Author": "Miguel de Cervantes", "Title": "Don Quixote", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "Marcel Proust", "Title": "In Search of Lost Time", "Genres": "Fiction, Classic, Philosophical"},
    {"Author": "James Joyce", "Title": "Ulysses", "Genres": "Fiction, Classic, Modernist"},
    {"Author": "F. Scott Fitzgerald", "Title": "The Great Gatsby", "Genres": "Fiction, Classic, Tragedy"},
    {"Author": "Herman Melville", "Title": "Moby Dick", "Genres": "Fiction, Classic, Adventure"},
    {"Author": "Leo Tolstoy", "Title": "War and Peace", "Genres": "Fiction, Classic, Historical"},
    {"Author": "William Shakespeare", "Title": "Hamlet", "Genres": "Fiction, Classic, Play"},
    {"Author": "Homer", "Title": "The Odyssey", "Genres": "Fiction, Classic, Epic"},
    {"Author": "Gabriel García Márquez", "Title": "One Hundred Years of Solitude", "Genres": "Fiction, Magical Realism, Classic"},
    {"Author": "Dante Alighieri", "Title": "The Divine Comedy", "Genres": "Fiction, Classic, Poetry"},
    {"Author": "Fyodor Dostoevsky", "Title": "The Brothers Karamazov", "Genres": "Fiction, Classic, Philosophical"}
]