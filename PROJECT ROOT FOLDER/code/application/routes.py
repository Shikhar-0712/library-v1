from datetime import datetime, timedelta
from sqlalchemy import func
from application import app
from flask import flash, redirect, render_template,request, session, url_for
from application.models import Cart1, Feedback, Section, User,Book,Issue
from application.database import db
from application.variables import *

def revoke_access_for_overdue_books():
    current_date = datetime.now().date()
    overdue_books = Book.query.filter(Book.return_date < current_date).all()
    for book in overdue_books:
        revoke_access(book.id) 

@app.route('/')
def index():
    revoke_access_for_overdue_books()
    sections=Section.query.all()
    return render_template('index.html' , sections=sections)

@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password=request.form['password']
        address = request.form['address']

        if len(password) != 8:
            flash("Password must be exactly 8 characters long.")
            return render_template('register.html')
        
        user=User(name,phone,email,password,address,USER)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user'] = user.to_dict()
            print("login in successful and logged in user", user)
            if session.get('user')['role'] == "super_admin":
                return redirect(url_for('super_admin'))
            elif session.get('user')['role'] == "admin":
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/super_admin')
def super_admin():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] != "super_admin":
        return redirect(url_for('login'))
    return render_template('superAdmin.html')

@app.route('/admin_register' , methods=['POST'])
def admin_register():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] != "super_admin":
        return redirect(url_for('login'))
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    password=request.form['password']
    address = request.form['address']
    user=User(name,phone,email,password,address,ADMIN)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('super_admin'))


@app.route('/admin')
def admin():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    sections=Section.query.all()
    return render_template('admin.html', sections=sections) 

@app.route('/add_section' , methods=['POST'])
def add_section():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    name = request.form['section']
    description = request.form['description']
    section=Section(name)
    section.description=description
    section.date_created=db.func.current_date()
    db.session.add(section)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/add_book' , methods=['POST'])
def add_book():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    name = request.form['book']
    content=request.form['content']
    author = request.form['author']
    section_id= request.form['section']
    date_issue=None
    return_date=None
    book=Book(name,content,author,int(1),date_issue,return_date,section_id)
    section=Section.query.filter_by(id=section_id).first()
    section.books.append(book)
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete_section' , methods=['POST'])
def delete_section():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    section_id = request.form['section_id']
    section=Section.query.filter_by(id=section_id).first()
    for book in section.books:
        db.session.delete(book)
    db.session.delete(section)
    db.session.commit()
    return redirect(url_for('admin'))
    
@app.route('/delete_book' , methods=['POST'])
def delete_product():
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    book_id= request.form['book']
    book=Book.query.filter_by(id=book_id).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    book=Book.query.filter_by(id=id).first()
    if request.method == 'POST':
        name = request.form['book']
        content = request.form['content']
        author = request.form['author']
        section_id = request.form['section']
        
        # Update book details
        book.name = name
        book.content = content
        book.author = author
        
        # Update section
        section = Section.query.get_or_404(section_id)
        book.section = section
        
        db.session.commit()
        return redirect(url_for('admin'))
    
    sections = Section.query.all()
    return render_template('update.html', book=book,books=Book.query.all(), sections=sections, update_type="book")



@app.route('/edit_section/<int:id>' , methods=['GET','POST'])
def edit_section(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    if session.get('user')['role'] == USER:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name=request.form['section']
        description=request.form['description']
        section=Section.query.filter_by(id=id).first()
        section.name=name
        section.description=description
        db.session.commit()
        return redirect(url_for('admin'))
    section=Section.query.filter_by(id=id).first()
    return render_template('update.html', section=section, sections=Section.query.all(), update_type="section")


@app.route('/add_to_cart' , methods=['POST'])
def add_to_cart():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    user_id = session.get('user')['id']
    
    book_id = request.form['book_id']
    quantity = request.form['quantity']
    book=Book.query.filter_by(id=book_id).first()
    if book.quantity < int(quantity):
        print('Out of Stock')
        return redirect(url_for('index'))
    cart=Cart1.query.filter_by(user_id=session.get('user')['id'],book_id=book_id).first()
    if cart:
        cart.quantity=cart.quantity+int(quantity)
        book.quantity=book.quantity-int(quantity)
        db.session.commit()
        print('Updated cart')
        return redirect(url_for('index'))
    cart=Cart1(session.get('user')['id'],book_id,quantity)
    book.quantity=book.quantity-int(quantity)
    db.session.add(cart)
    db.session.commit()
    print('Added to cart')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if not session.get('user'):
        return redirect(url_for('login'))
    carts=Cart1.query.filter_by(user_id=session.get('user')['id'] , is_ordered=False).all()
    books=Book.query.filter(Book.id.in_([cart.book_id for cart in carts])).all()
    return render_template('cart.html', carts=carts, books=books)

@app.route('/delete_from_cart/<int:id>' , methods=['GET','POST'])
def delete_from_cart(id):
    if not session.get('user'):
        return redirect(url_for('login'))
    cart=Cart1.query.filter_by(id=id).first()
    book=Book.query.filter_by(id=cart.book_id).first()
    book.quantity=book.quantity+cart.quantity
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/issues')
def orders():
    if not session.get('user'):
        return redirect(url_for('login'))
    user=User.query.filter_by(id=session.get('user')['id']).first()
    carts=Cart1.query.filter_by(user_id=session.get('user')['id']).all()

    user_id = session.get('user')['id']

    issued_books_count = Cart1.query.filter_by(user_id=user_id, is_ordered=True).count()
    
    if issued_books_count > 4:
        return redirect(url_for('index'))

    for cart in carts:
        book=Book.query.filter_by(id=cart.book_id).first()
        issue=Issue(session.get('user')['id'] , cart.book_id)
        issue.carts.append(cart)
        cart.is_ordered = True 
        book.date_issue = datetime.now().date()
        book.return_date = book.date_issue + timedelta(days=7)
        db.session.add(issue)
        db.session.commit()   
    return render_template('order.html' , issue=issue)

@app.route('/issued')
def issued():
    users_with_books = User.query.join(Issue).join(Cart1).distinct().all()
    issued_books = {}
    for user in users_with_books:
        issues = Issue.query.filter_by(user_id=user.id).all()
        books_issued = []
        for issue in issues:
            carts = Cart1.query.filter_by(issue_id=issue.id).all()
            for cart in carts:
                book = Book.query.get(cart.book_id)
                if book:
                    book_info = {
                        'name': book.name,
                        'quantity': cart.quantity,
                        'id': book.id,
                        'content': book.content,
                        'author': book.author,
                        'section': book.section.name,
                        'date_issue': book.date_issue,
                        'return_date': book.return_date
                    }
                    books_issued.append(book_info)
        issued_books[user.name] = books_issued
    return render_template('issue.html', issued_books=issued_books)


@app.route('/revoke_access/<int:book_id>', methods=['POST'])
def revoke_access(book_id):
    cart = Cart1.query.filter_by(book_id=book_id, is_ordered=True).first()
    if cart:
        db.session.delete(cart)
        book = Book.query.get(book_id)
        if book:
            cart.is_ordered = False
            book.date_issue = None
            book.return_date = None
            book.quantity += 1  
            db.session.commit()
        else:
            return "Book not found", 404
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/my_issues')
def my_issues():
    user_id = session.get('user')['id']  # Retrieve user ID from session
    issued_books = []
    issues = Issue.query.filter_by(user_id=user_id).all()
    for issue in issues:
        carts = Cart1.query.filter_by(issue_id=issue.id , is_ordered=True).all()
        for cart in carts:
            book = Book.query.get(cart.book_id)
            if book:
                book_info = {
                    'name': book.name,
                    'quantity': cart.quantity,
                    'content': book.content,
                    'id': book.id,
                    'author': book.author,
                    'section': book.section.name,
                    'date_issue': book.date_issue,
                    'return_date': book.return_date
                }
                issued_books.append(book_info)
    return render_template('my_issues.html', issued_books=issued_books)

@app.route('/return_book/<int:book_id>', methods=['POST'])
def return_book(book_id):
    cart = Cart1.query.filter_by(book_id=book_id, is_ordered=True).first()
    if cart:
        db.session.delete(cart)
        cart.is_ordered = False
        book = Book.query.get(book_id)
        if book:
            book.date_issue = None
            book.return_date = None
            book.quantity += 1  
            db.session.commit()
        else:
            return "Book not found", 404
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    book_id = request.form.get('book_id')
    user_id = session.get('user')['id']  
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    feedback = Feedback(book_id=book_id, user_id=user_id, rating=rating, comment=comment)
    db.session.add(feedback)
    db.session.commit()
    return redirect(url_for('my_issues', book_id=book_id))


@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query', '')
    search_type = request.args.get('search_type', 'name')

    search_query_formatted = search_query.lower().replace(' ', '')

    if search_type == 'author':
        books = Book.query.filter(func.lower(func.replace(func.replace(Book.author, ' ', ''), ' ', '')).like('%{}%'.format(search_query_formatted))).all()
    elif search_type == 'section':
        books = Book.query.join(Section).filter(func.lower(func.replace(func.replace(Section.name, ' ', ''), ' ', '')).like('%{}%'.format(search_query_formatted))).all()
    elif search_type == 'name':
        books = Book.query.filter(func.lower(func.replace(func.replace(Book.name, ' ', ''), ' ', '')).like('%{}%'.format(search_query_formatted))).all()
    elif search_type == 'content':
        books = Book.query.filter(func.lower(func.replace(func.replace(Book.content, ' ', ''), ' ', '')).like('%{}%'.format(search_query_formatted))).all()    
    elif search_type == 'rating':
        books = db.session.query(Book).join(Feedback).filter(Feedback.rating >= search_query).all()
    else:
        books = Book.query.filter(func.lower(func.replace(func.replace(Book.name, ' ', ''), ' ', '')).like('%{}%'.format(search_query_formatted))).all()

    return render_template('search_results.html', books=books, search_query=search_query, search_type=search_type)


@app.route('/history')
def history():
    if not session.get('user'):
        return redirect(url_for('login'))
    
    issued_books = Issue.query.all()
    
    issued_books_info = []
    
    for issue in issued_books:
        user = User.query.filter_by(id=issue.user_id).first()
        book = Book.query.filter_by(id=issue.book_id).first()
        
        issued_book_info = {
            'user_name': user.name,
            'book_name': book.name
        }
        
        issued_books_info.append(issued_book_info)
    
    return render_template('history.html', issued_books=issued_books_info)
