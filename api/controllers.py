# ----------------
# api calls (v1.0)
# ----------------
from flask import Blueprint, render_template, request, abort
from flask.json import jsonify
from models import *
from datetime import datetime
import os, json, sys

## BASE_PATH = '/api/v1.0'

api = Blueprint('api', __name__, template_folder='templates')

#json_products  = jsonify(json_list=[i.serialize for i in Product.query.all()])
#json_customers = jsonify(json_list=[i.serialize for i in Customer.query.all()])

MAX_ORDERS = 200

@api.route('/')
def hello_world():
	return 'Hello World!'
	
@api.route('/login', methods=['POST'])
def login():
	# do the login
	username = request.json['username']
	password = request.json['password']
	
	print "richiesto login, username %s, password %s" % (username, password)
	
	if username and password:
		user = User.query.filter(User.username == username).filter(User.is_admin == False).first()
		if user:
			if user.password == password:
				return jsonify({"code" : user.code, 'username' : username})
	abort(401)

@api.route('/products', methods=['GET'])
def get_products():
	return jsonify(json_list=[i.serialize for i in Product.query.all()])


@api.route('/customers', methods=['GET'])
def get_customers():
	return jsonify(json_list=[i.serialize for i in Customer.query.all()])

	
@api.route('/orders/new', methods=['POST'])
def new_order():
	user_id = request.json['user_id']
	customer_code = request.json['customer_code']
	type = request.json['type']
	
	if type == "I":
		abort(500)

	customer = Customer.query.filter(Customer.code == customer_code).first()
	print("  Cliente: " + customer.name)
	purchase = Purchase(User.query.get(user_id), customer)
	db.session.add(purchase)
	
	for i in request.json['items']:
		item = PurchaseItem(qty=i['qty'], product=Product.query.filter(Product.code == i['product_code']).first(), notes=i['notes'])
		item.purchase = purchase
		db.session.add(item)
	
	db.session.commit()

	#print("Ricevuto ordine con {0} prodotti:".format(purchase.items.count()))
	#print("  Cliente: " + Customer.query.filter(Customer.code == customer_code).first().name)
	#print("  Creato: " + purchase.creation_date.strftime('%d-%m-%Y %H:%M:%S'))
	#for item in purchase.items:
	#	print("%rx %r [%r]" % (item.qty, item.product.name, item.notes))	

	return jsonify({"id" : purchase.id})

# metodo per tests da C#
@api.route('/orders/nuovo', methods=['POST'])
def nuovo_ordine():
	ss = request.form["json"]
	json = jsonify({"risposta" : ss})
	return json
	
	user_id = json['user_id']
	customer_code = json['customer_code']
	type = json['type']
	
	if type == "I":
		abort(500)

	customer = Customer.query.filter(Customer.code == customer_code).first()
	print("  Cliente: " + customer.name)
	purchase = Purchase(User.query.get(user_id), customer)
	db.session.add(purchase)
	
	for i in json['items']:
		item = PurchaseItem(qty=i['qty'], product=Product.query.filter(Product.code == i['product_code']).first(), notes=i['notes'])
		item.purchase = purchase
		db.session.add(item)
	
	db.session.commit()
	return jsonify({"id" : purchase.id})


@api.route('/icewer/new', methods=['POST'])
def new_order_icewer():
	user_id = request.json['user_id']
	customer_code = request.json['customer_code']
	type = request.json['type']
	
	if type != "I":
		abort(500)
	
	purchase = IcewerPurchase(User.query.get(user_id), Customer.query.filter(Customer.code == customer_code).first())
	db.session.add(purchase)
	
	for i in request.json['items']:
		item = IcewerPurchaseItem(qty=i['qty'], product_code=['product_code'], notes=i['notes'])
		item.purchase = purchase
		db.session.add(item)
	
	db.session.commit()
	
	#print("Ricevuto ordine ICE-WER con {0} prodotti:".format(o.items.count()))
	#print("Cliente: " + Customer.query.filter(Customer.code == customer_code).first().name)
	#print("Data creazione: " + o.creation_date.strftime('%d-%m-%Y %H:%M:%S'))
	#for item in o.items:
	#	print("%rx %r [%r]" % (item.qty, item.product_code, item.notes))
	
	return jsonify({"id" : o.id})

@api.route('/last_orders/<int:from_id>', methods=['GET'])
def last_orders(from_id):
	last_orders = []
	orders_list = Purchase.query.filter(Purchase.id > from_id).filter(Purchase.customer_id != None).order_by('id')[-MAX_ORDERS:]
	for o in orders_list:
		try:
			last_orders.append(o.serialize)
		except:
			continue
	#print("Trovati {0} ordini".format(len(last_orders)))

	return jsonify(json_list=last_orders)
	
@api.route('/last_orders_test/<int:from_id>', methods=['GET'])
def last_orders_test(from_id):
	last_orders = []
	orders_list = Purchase.query.filter(Purchase.id > from_id).filter(Purchase.customer_id != None).order_by('id')[-MAX_ORDERS:]
	for o in orders_list:
		try:
			last_orders.append(o.serialize)
		except:
			continue
	#print("Trovati {0} ordini".format(len(last_orders)))

	return jsonify(json_list=last_orders)
	
# @api.route('/checkAppVersion', methods=['GET']):
# def check_app_version():
	# return jsonify({"success" : True, "latestVersion" : 2, "appURI" : url_for('.downloadApp')})

# @api.route('/downloadApp', methods=['GET']):
# def downloadApp():
	# return 1
