from functools import wraps
from flask import g, request, Blueprint, render_template, redirect, url_for, flash, abort, session, make_response
from gingo.data.models import db, User, Product, Customer, Purchase, PurchaseItem
from gingo.data.parsers import CustomerXmlParser, ProductXmlParser
from reportlab.pdfgen import canvas

admin = Blueprint('admin', __name__, template_folder='templates')

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		load_user()
		if g.user is None:
			return redirect(url_for('.login', next=request.url))
		return f(*args, **kwargs)
	return decorated_function


@admin.before_request
def load_user():
	if session.get("user_id"):
		user = User.query.filter_by(id=session["user_id"]).first()
	else:
		user = None

	g.user = user


@admin.route('/')
@login_required
def index():
	return render_template('admin_index.htm')

	
@admin.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		# do the login
		username = request.form.get('username')
		password = request.form.get('password')
		
		if username and password:
			user = User.query.filter(User.username == username).filter(User.is_admin == True).first()
			if user:
				if user.password == password:
					session['user_id'] = user.id
					return redirect(url_for('.index'))
		flash('Nome utente o password errati.', category='error')
		return redirect(url_for('.login'))
	else:
		# show the login form
		return render_template('login.htm')

@admin.route('/logout', methods=['GET'])
def logout():
	if session.get("user_id"):
		session.pop("user_id")
		flash('Sessione di lavoro conclusa.', category='success')
	return redirect(url_for('.login'))


# @admin.route('/search', methods=['GET', 'POST'])
# def search(page=1):
	# if request.method == 'POST':
		# query = request.form.get('q')
		# products = Product.query.filter(Product.name.contains(query)).paginate(page, 10, False)
		# customers = Customer.query.filter(Customer.name.contains(query)).paginate(page, 10, False)
		
		# return render_template("search.htm", query=query, products=products, customers=customers)


@admin.route('/products/search', methods=['GET', 'POST'])
@admin.route('/products/search?q=<string:query>', methods=['GET', 'POST'])
def search_products(query=None, page=1):
	if query:
		products = Product.query.filter(Product.name.contains(query)).paginate(page, 10, False)
		
	return render_template("search.htm", query=query, products=products)

@admin.route('/customers/search/<string:query>', methods=['GET'])
#@admin.route('/customers/search', methods=['GET', 'POST'])
def search_customers(query=None, page=1):
	customers = None
	# if request.method == 'POST':
		# q = request.form.get('query', None)
	# q=request.args.get('q', None)
	
	if query:
		try:
			print(query)
			customers = Customer.query.filter(Customer.name.contains(query)).paginate(page, 10, False)
		except:
			pass
		
	return render_template("customers.htm", query=query, customers=customers)

#####################
## 	  products    ##
#####################	

@admin.route('/products', methods=['GET'])
@admin.route('/products/<int:page>', methods=['GET'])
@login_required
def display_products(page=1):
	products = Product.query.paginate(page, 10, False)
	return render_template("products.htm", products=products)


@admin.route('/products/edit/<int:product_id>', methods=['GET'])
@login_required
def edit_product(product_id):
	if product_id:
		product = Product.query.get(product_id)
	
		if product != None:
			return render_template("product.htm", product=product)
	
	return redirect(url_for('.display_product'))


@admin.route('/products/save', methods=['POST'])
@login_required
def save_product():
	product_id = request.form['product_id']
	
	product = Product.query.get(product_id)
	if product == None:
		product = Product()
	
	product.code=request.form['code']
	product.name=request.form['name']
	product.price=request.form['price']
	
	db.session.add(product)
	db.session.commit()
	flash('Salvataggio effettuato.', category='success')
	return redirect(url_for('.display_products'))


@admin.route('/products/new', methods=['GET'])
@login_required
def new_product():
	product = Product()
	return render_template("product.htm", product=product)


@admin.route('/products/del/<int:product_id>', methods=['GET'])
@login_required
def delete_product(product_id):
	product = Product.query.get(product_id)
	if product != None:
		db.session.delete(product)
		db.session.commit()
		flash('Cancellazione effettuata.', category='success')
		return redirect(url_for('.display_products'))

	abort(404)


@admin.route('/products/import', methods=['GET', 'POST'])
@login_required
def import_products():	
	if request.method == 'GET':
		return render_template("import_products.htm")
	else:
		f = request.files['fproducts']
		imp = ProductXmlParser(f)
		products = imp.parse()
		
		created = 0
		updated = 0
		
		for new_product in products:
			existing_product = Product.query.filter_by(code=new_product.code).first()
			if existing_product:
				existing_product.name = new_product.name
				existing_product.price = new_product.price
				updated = updated + 1
			else:
				db.session.add(new_product)
				created = created + 1
		
		db.session.commit()
		
		if created:	
			message = 'Importati {0} nuovi prodotti.'.format(created)
		else:
			message = 'Nessun nuovo prodotto importato'
		
		flash(message, category='success')
		return redirect(url_for('.display_products'))
	

#####################
## 	  customers    ##
#####################

@admin.route('/customers', methods=['GET'])
@admin.route('/customers/<int:page>', methods=['GET'])
@login_required
def display_customers(page=1):
	customers = Customer.query.paginate(page, 10, False)
	return render_template("customers.htm", customers=customers)


@admin.route('/customers/edit/<int:customer_id>', methods=['GET'])
@login_required
def edit_customer(customer_id):
	if customer_id:
		customer = Customer.query.get(customer_id)
	
		if customer != None:
			return render_template("customer.htm", customer=customer)
	
	return redirect(url_for('.display_customers'))


@admin.route('/customers/new', methods=['GET'])
@login_required
def new_customer():
	customer = Customer()
	return render_template("customer.htm", customer=customer)


@admin.route('/customers/del/<int:customer_id>', methods=['GET'])
@login_required
def delete_customer(customer_id):
	customer = Customer.query.get(customer_id)
	if customer != None:
		db.session.delete(customer)
		db.session.commit()
		flash('Cancellazione effettuata.', category='success')
		return redirect(url_for('.display_customers'))

	abort(404)


@admin.route('/customers/save', methods=['POST'])
@login_required
def save_customer():
	customer_id = request.form['customer_id']
	
	customer = Customer.query.get(customer_id)
	if customer == None:
		customer = Customer()
	
	customer.code=request.form['code']
	customer.name=request.form['name']
	customer.address=request.form['address']
	customer.cap=request.form['cap']
	customer.city=request.form['city']
	customer.prov=request.form['prov']
	customer.part_iva=request.form['part_iva']
	
	db.session.add(customer)
	db.session.commit()
	flash('Salvataggio effettuato.', category='success')
	return redirect(url_for('.display_customers'))


@admin.route('/customers/import', methods=['GET', 'POST'])
@login_required
def import_customers():	
	if request.method == 'GET':
		return render_template("import_customers.htm")
	else:
		f = request.files['fcustomers']
		imp = CustomerXmlParser(f)
		customers = imp.parse()
		
		created = 0
		updated = 0
		
		for new_customer in customers:
			existing_customer = Customer.query.filter_by(code=new_customer.code).first()
			if existing_customer:
				existing_customer.code = new_customer.code
				existing_customer.name = new_customer.name
				existing_customer.part_iva = new_customer.part_iva
				existing_customer.address = new_customer.address
				existing_customer.city = new_customer.city
				existing_customer.cap = new_customer.cap
				existing_customer.prov = new_customer.prov
				updated = updated + 1
			else:
				db.session.add(new_customer)
				created = created + 1
		
		db.session.commit()
		
		if created:	
			message = 'Importati {0} nuovi clienti.'.format(created)
		else:
			message = 'Nessun nuovo cliente importato'
		
		flash(message, category='success')
		return redirect(url_for('.display_customers'))

#####################
## 	    orders     ##
#####################
		
@admin.route('/orders', methods=['GET'])
@admin.route('/orders/<int:page>', methods=['GET'])
@login_required
def display_orders(page=1):
	orders = Purchase.query.order_by(Purchase.creation_date.desc()).paginate(page, 10, False)
	return render_template("orders.htm", orders=orders)

@admin.route('/orders/del/<int:o_id>', methods=['GET'])
@login_required
def cancella_ordine(o_id=0):
	order = Purchase.query.get(o_id)
	if order != None:
		db.session.delete(order)
		db.session.commit()
		flash('Cancellazione effettuata.', category='success')
		return redirect(url_for('.display_orders'))

	abort(404)
	
@admin.route('/download_doc/<int:id_doc>', methods=['GET'])
@login_required
def download_doc(id_doc):
	o = Purchase.query.get(id_doc)

	import cStringIO
	output = cStringIO.StringIO()

	p = canvas.Canvas(output)
	p.setLineWidth(.3)
	p.setFont('Helvetica', 12)
	p.drawString(30,750, o.customer.code + " -  " + o.customer.name)
	p.drawString(30,735, "Ordine n. " + str(o.id) + " del " + o.creation_date.strftime('%d/%m/%Y'))
	
	y = 710
	for item in o.items:
		notes = item.notes.encode('utf-8')
		# print notes
		notes = ("*** " + notes + " ***") if len(notes) > 0 else ""
		# print notes
		notes = unicode(notes, 'utf-8')
		pcode = item.product.code if item.product != None else ""
		pname = item.product.name if item.product != None else ""		
		p.drawString(30,y, str(item.qty) + "x  [" + pcode + "] " + pname + notes)
		y = y-25
	
	
	p.showPage()
	p.save()

	pdf_out = output.getvalue()
	output.close()

	response = make_response(pdf_out)
	# filename = o.id + 'pdf'
	response.headers['Content-Disposition'] = "attachment; filename='ordine.pdf'"
	response.mimetype = 'application/pdf'
	return response
