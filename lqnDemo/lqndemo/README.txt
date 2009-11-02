Code overview
=============

Requirements
------------

This demo app for the lqn network is built on top of repoze.bfg. It helps to have some understanding of the framework, so please have a look at 

http://docs.repoze.org/bfg/1.1/index.html
http://docs.repoze.org/bfg/1.1/tutorials/bfgwiki/index.html

Within this framework I have been using zpt templates

http://docs.zope.org/zope2/zope2book/ZPT.html

As a storage backend zodb is used

http://zope.org/Documentation/Articles/ZODB1

The one thing to know about zodb is that its basically a mechanism to store pickles of your objects. That means no sql, no schemas. You throw an instance of a class that inherited from Persistent at it, and ideally whenever you modify an object, the changes will be made persistent.

The idea
--------

Users of the system have an account, and can do transactions. Accounts have ids (10001, 10002) which are used to login, and realnames, which are used for display. Transactions that are made between the accounts are added to update the balance of that account (and get recalculated on each new transaction). The vouchers are not checked against balance / deducted from the account upon creation, so they can safely be thrown away when not used. Vouchers have a (secret) id, which is printed as part of the qr code. 


Basic architecture
------------------

The models.py file contains the basic components, run.py the basic startup mechanism, instantiating a lqnServer and setting up dummy accounts. Views are defined in views.py (for the logic) and templates/... for the layout. The views are glued to the models in configure.zcml (which might be changed later, there was a bug in repoze.bfg). The lqn system uses object traversal, that is first system tries to resolve a url to a chain of objects (/foo/bar/baz -> root['foo']['bar']['baz']), and if it can't find an object, it tries a view. Views are glued to models using interfaces or their classes - by this one could e.g. have multiple index.html, with different behaviour depending on what type of object it is called.

Views
-----

In the lqn app views handle both GET and POST requests, aka form submits. This is to make the code a bit more sorted. All the views check if there is POST data, and if so try to work with the submited form data. Errors in validation are stored in an errors dict which is passed back to the form. All the forms use the master.pt template as its base layout container, this is also where the (optional) message gets displayed.

Tests
-----

From the top level directory (which contains the lqnDemo.ini) 'nosetests' can be run. This will run the doctests that can be found in the app.

