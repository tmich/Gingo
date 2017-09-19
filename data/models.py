# models
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
from hashlib import md5
import uuid

db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(32))
	code	 = db.Column(db.String(36))		# UUID
	is_admin = db.Column(db.Boolean)

	def __init__(self, username, password, is_admin):
		self.username = username
		self.password = password
		self.is_admin = is_admin
		self.code     = str(uuid.uuid4())

	def __repr__(self):
		return '<User %r>' % self.username

class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(10))
	name = db.Column(db.String(80))
	price = db.Column(db.Float)
	
	def __init__(self, code=None, name=None, price=0.00):
		self.code = code
		self.name = name
		self.price = price
	
	def __repr__(self):
		return '<Product %r>' % self.name
		
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'	: self.id,
			'code'	: unicode(self.code),
			#'name'	: unicode(self.name),
			'name'	: self.name.decode('iso-8859-1').encode('utf8'),
			'price'	: self.price,
			'hash'	: ''
		}
	
	@property
	def hash(self):
		price = unicode(self.price if self.price != None else 0.00)
		name  = unicode(self.name)
		hsh   = md5(name + price)
		return hsh.hexdigest()

class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.Text)
	name = db.Column(db.String(200))
	address = db.Column(db.Text)
	part_iva = db.Column(db.Text)
	cap = db.Column(db.Text)
	city = db.Column(db.Text)
	prov = db.Column(db.Text)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	user = db.relationship('User',
		backref=db.backref('customer', lazy='dynamic'))
	
	def __init__(self, code=None, name=None, user=None):
		self.code = code
		self.name = name
		self.user = user
	
	def __repr__(self):
		return '<Customer %r>' % self.name
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'		: self.id,
			'code'		: self.code,
			'name'		: self.name.decode('iso-8859-1').encode('utf8'),
			'address'	: self.address,
			'iva'		: self.part_iva,
			'cap'		: self.cap,
			'city'		: self.city,
			'prov'		: self.prov,
			'tel'		: '',
			'user_id'	: self.user_id if self.user_id != None else 0,
			'hash'		: ''
		}
		
	@property
	def hash(self):
		# addr  = unicode(self.address if self.address != None else "")
		# name  = unicode(self.name)
		# hsh   = md5('%s%s' % ( name, price))
		# return hsh.encode().hexdigest()
		tobehashed = '%s%s%s%s%s' % (self.name, self.address if self.address != None else "" , self.city if self.city != None else "" , self.part_iva if self.part_iva != None else "" , self.cap if self.cap != None else "")
		return md5(unicode(tobehashed)).hexdigest().encode()

class Purchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
	creation_date = db.Column(db.DateTime)
	
	user = db.relationship('User',
		backref=db.backref('purchases', lazy='dynamic'))
	
	customer = db.relationship('Customer',
		backref=db.backref('purchases', lazy='dynamic'))
	
	def __init__(self, user, customer):
		self.user = user
		self.customer = customer
		self.creation_date = datetime.today()
	
	def __repr__(self):
		return '<Purchase %r>' % self.id
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id'			: self.id,
			'customer_code'	: unicode(self.customer.code),
			'customer_name'	: unicode(self.customer.name),
			'creation_date'	: unicode(self.creation_date),
			'items'			: [it.serialize for it in self.items] if self.items != None else []
		}

class PurchaseItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
	qty = db.Column(db.Integer)
	notes = db.Column(db.Text)
	discount = db.Column(db.Text)
	
	product = db.relationship('Product')
	purchase = db.relationship('Purchase',
		backref=db.backref('items', lazy='dynamic'))
	
	def __init__(self, qty, product, notes=None, discount=None):
		#self.purchase = purchase
		self.qty = qty
		self.product = product
		self.notes = notes
		self.discount = discount

	def __repr__(self):
		return '<PurchaseItem %r %r>' % (self.qty, self.product.name)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		if self.product != None:
			return {
				'id'	: self.id,
				'name' 	: self.product.name,
				'code' 	: self.product.code,
				'qty'	: self.qty,
				'notes'	: self.notes
			}
		else:
			return {
				'id'	: 0,
				'name' 	: '',
				'code' 	: '',
				'qty'	: 0,
				'notes'	: ''
			}

class IcewerPurchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
	creation_date = db.Column(db.DateTime)
	
	user = db.relationship('User',
		backref=db.backref('icewer_purchases', lazy='dynamic'))
	
	customer = db.relationship('Customer',
		backref=db.backref('icewer_purchases', lazy='dynamic'))
	
	def __init__(self, user, customer):
		self.user = user
		self.customer = customer
		self.creation_date = datetime.today()
	
	def __repr__(self):
		return '<Purchase %r>' % self.id
		
class IcewerPurchaseItem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	purchase_id = db.Column(db.Integer, db.ForeignKey('icewer_purchase.id'))
	product_code = db.Column(db.Text)
	qty = db.Column(db.Integer)
	notes = db.Column(db.Text)
	discount = db.Column(db.Text)
	
	purchase = db.relationship('IcewerPurchase',
		backref=db.backref('items', lazy='dynamic'))
	
	def __init__(self, qty, product_code, notes=None, discount=None):
		self.qty = qty
		self.product_code = product_code
		self.notes = notes
		self.discount = discount

	def __repr__(self):
		return '<IcewerPurchaseItem %r %r>' % (self.qty, self.product_code)

class Favorite(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	hits = db.Column(db.Integer)
	
	customer = db.relationship('Customer',
		backref=db.backref('favorites', lazy='dynamic'))
	
	product = db.relationship('Product')
	
	def __init__(self, product, customer, hits):
		self.product = product
		self.customer = customer
		self.hits = hits
	
	def __repr__(self):
		return '<Favorite %r %r>' % (self.product.name, self.customer.name)

class DiscountProduct(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	discount_value = db.Column(db.Float)
	discount_type = db.Column(db.String(1), nullable=False)
	
	customer = db.relationship('Customer',
		backref=db.backref('discounted_products', lazy='dynamic'))
	
	product = db.relationship('Product')
	
	def __init__(self, product, customer, discount_value, discount_type):
		self.product = product
		self.customer = customer
		self.discount_value = discount_value
		self.discount_type = discount_type
	
	def __repr__(self):
		return '<DiscountProduct %r %r %r %r>' % (self.product.name, self.customer.name, self.discount_value, self.discount_type)
