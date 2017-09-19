#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import os, sys
from xml.dom.minidom import parseString
from models import Customer, Product

class XmlParser:

	def __init__(self, fd):
		self.results = []
		self.dom = parseString(fd.read())

	def parse(self):
		self.handleRoot(self.dom)
		return self.results
	
	def handleRoot(self, dom):
		pass
		
	def getText(self, nodelist):
		rc = []
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				rc.append(node.data)
		# return u''.join(rc).encode('utf-8')
		return ''.join(rc)


class CustomerXmlParser(XmlParser):

	def handleRoot(self, dom):
		clienti = dom.getElementsByTagName("CLIENTI")
		self.handleClienti(clienti)

	def handleClienti(self, clienti):
		for cliente in clienti:
			self.handleCliente(cliente)

	def handleCliente(self, cliente):
		cl = Customer()
		cl.name = self.handleClienteRagSoc(cliente.getElementsByTagName("RAGSOC")[0])
		cl.code = self.handleClienteCodCli(cliente.getElementsByTagName("CODCLI")[0])
		
		try:
			cl.address = self.handleClienteIndir(cliente.getElementsByTagName("INDIR")[0])
		except(TypeError, IndexError):
			cl.address = None
		
		try:
			cl.cap = self.handleClienteCap(cliente.getElementsByTagName("CAP")[0])
		except(TypeError, IndexError):
			pass
			
		try:
			cl.city = self.handleClienteLocal(cliente.getElementsByTagName("LOCAL")[0])
		except(TypeError, IndexError):
			pass
			
		try:
			cl.prov = self.handleClienteProv(cliente.getElementsByTagName("PROV")[0])
		except(TypeError, IndexError):
			pass
		
		try:
			cl.part_iva = self.handleClientePartIva(cliente.getElementsByTagName("PARTIVA")[0])
		except(TypeError, IndexError):
			pass
		
		self.results.append(cl)

	########## GESTIONE ATTRIBUTI DEL CLIENTE ##############
	def handleClienteRagSoc(self, ragsoc):
		return self.getText(ragsoc.childNodes)

	def handleClienteCodCli(self, codcli):
		return self.getText(codcli.childNodes)

	def handleClienteIndir(self, indir):
		return self.getText(indir.childNodes)

	def handleClienteCap(self, cap):
		return self.getText(cap.childNodes)

	def handleClienteLocal(self, loc):
		return self.getText(loc.childNodes)

	def handleClienteProv(self, prov):
		return self.getText(prov.childNodes)

	def handleClientePartIva(self, partiva):
		return self.getText(partiva.childNodes)

	########## FINE - GESTIONE ATTRIBUTI DEL CLIENTE ##############


class ProductXmlParser(XmlParser):

	def handleRoot(self, dom):
		prodotti = dom.getElementsByTagName("ARTICOL")
		self.handleProdotti(prodotti)
	
	def handleProdotti(self, prodotti):
		for prodotto in prodotti:
			self.handleProdotto(prodotto)
	
	def handleProdotto(self, prodotto):
		p = Product()
		
		try:
			p.code = self.getText(prodotto.getElementsByTagName("CODART")[0].childNodes)
			p.name = self.getText(prodotto.getElementsByTagName("DESART")[0].childNodes)
			p.price = self.getText(prodotto.getElementsByTagName("PREZZO1")[0].childNodes).replace(',', '.')
		except(TypeError, IndexError):
			pass
		
		self.results.append(p)
