# BooksRental

#### Description:
    This project is here to facilitate the borrowing of books by bookshops.Users not having an account are provided with a registration page which allows them to create their account by providing details such as: cardNumber, firstname, lastname, email, and address.For already registered users, there is a log in page provided for them.

#### Styling
A little bit of css was used and bootstrap for the most part 
<br>

### Some Specificstions about the book store project
**A user can loan a maximum of one book at a time**
**The maximum period a user can be with a loaned book is 7 days**
**A user can only view available books and the books he/she has loan**
**An admin can view all the books in the database(loaned or not) and can also add/delete books and delete a user account who fails to return a book within the allowed period**

### Database details
There are 3 tables.
**people** For users of the system.
**books** For books of the database which has a field loanee referencing the card_number field of the people table.
**loans** For all the loaned books and their respective people who loaned them. A kind of history of any book which has ever been loaned.
It has two fields loanee which references the card_number of the peolpe table and book_id which references the book_id field of the books table.

## Files within the project
### add_book.html
    This file has the functionalities for adding books to our database. This file works with the /add_book route.

### admin_index.html
    This file is rendered(for admins loged in) for the default admin route. This file works with the /admin route

### admin_layout.html
    This file is the layout file which all the admin pages inherits from

### apology.html
    This file which is displayed with the error message when an error occurs

### del_book.html
    This file is for admins to delete books from the database. This file works with the /del_book route

### del_user.html
    This file is for admins to delete users(The ones who dont't return books after the specifed range). This file works with the del_user route

### index.html
    This file is file rentered(for loged in users) for the default route. This file works with the / route

### layout.html
    This file layout file which the other common users files inherits from.

### loan.html
    This file is for users to loan or rent books. This file works with the /loan route

### login.html
    This file is login file where common users and admin log in from.It is also the file rendered by default for users not signed in. This file works with the /login route

### register.html
    This file is the register page where users create their accounts. This file works with the /register route

### return.html
    This file is for common users to return the books they loaned. This file works with the /returning route

### bookStore.db
    This file is database file which contain all of our tables. sqlite3 was used as the DBMS here.

### app.py
    This file is the python file with all of our routes and functionalities of the back-end

### mystyle.css
    This file contains very basic and simple stylings.
