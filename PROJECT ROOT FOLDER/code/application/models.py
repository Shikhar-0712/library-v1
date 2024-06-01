from application.database import db 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True , auto_increment=True)
    name = db.Column(db.String(255) , nullable=False)
    phone = db.Column(db.String(10) , nullable=False , unique=True)
    email = db.Column(db.String(50) , nullable=False , unique=True)
    password = db.Column(db.String(50) , nullable=False)
    name = db.Column(db.String(255) , nullable=False)
    address = db.Column(db.String(50) , nullable=True)
    role = db.Column(db.String(50) , nullable=False , default="customer")

    def __init__(self, name , phone , email, password, address,role):
        self.name = name
        self.phone =phone
        self.email=email
        self.password = password 
        self.address=address
        self.role=role

    def __repr__(self):
        return '<User %r>' % self.name    
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "phone":self.phone,
            "email":self.email,
            "password":self.password,
            "address":self.address,
            "role":self.role
        }

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True , auto_increment=True)
    name = db.Column(db.String(255) , nullable=False)
    description = db.Column(db.String(255) , nullable=False)
    date_created=db.Column(db.Date , nullable=False)
    books=db.relationship('Book' , backref=db.backref('section' , lazy=True))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Section %r>' % self.name
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "date_created":self.date_created,
            "description":self.description
        }

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True , auto_increment=True)
    name = db.Column(db.String(255) , nullable=False)
    content = db.Column(db.String(255) , nullable=False)
    author = db.Column(db.String(255) , nullable=False)
    quantity = db.Column(db.Integer , nullable=False , default=1)
    date_issue=db.Column(db.Date , nullable=True)
    return_date=db.Column(db.Date , nullable=True)
    section_id = db.Column(db.Integer , db.ForeignKey('section.id') , nullable=False)

    def __init__(self, name,content,author,quantity,date_issue,return_date, section_id):
        self.name = name
        self.content = content
        self.quantity = quantity
        self.author = author
        self.date_issue = date_issue
        self.return_date = return_date  
        self.section_id = section_id

    def __repr__(self):
        return '<Book %r>' % self.name
    
    def to_dict(self):
        return {
            "id":self.id,
            "name":self.name,
            "content":self.content,
            "author":self.author,
            "quantity":self.quantity,
            "date_issue":self.date_issue,
            "return_date":self.return_date,
            "section_id":self.section_id
        }


class Cart1(db.Model):
    id = db.Column(db.Integer, primary_key=True , auto_increment=True)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id') , nullable=False)
    book_id = db.Column(db.Integer , db.ForeignKey('book.id') , nullable=False)
    quantity = db.Column(db.Integer , nullable=False )
    is_ordered = db.Column(db.Boolean , nullable=False , default=False)
    issue_id=db.Column(db.Integer , db.ForeignKey('issue.id') , nullable=True)

    def __init__(self, user_id , book_id , quantity):
        self.user_id = user_id
        self.book_id = book_id
        self.quantity = quantity

    def __repr__(self):
        return '<Cart %r>' % self.user_id
    
    def to_dict(self):
        return {
            "id":self.id,
            "user_id":self.user_id,
            "book_id":self.book_id,
            "quantity":self.quantity,
            "is_ordered":self.is_ordered
        }
    
class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    carts=db.relationship('Cart1' , backref=db.backref('issue' , lazy=True))

    def __init__(self, user_id , book_id):
        self.user_id = user_id
        self.book_id = book_id

    def __repr__(self):
        return '<Issue %r>' % self.user_id
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id
        }


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Feedback {self.id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment
        }
