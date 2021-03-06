from flask import Blueprint, jsonify, request
from app.models import db, User, Transaction, Comment, Like
from sqlalchemy import and_, or_, desc
import datetime

transaction_routes = Blueprint("transactions", __name__, url_prefix="/transaction")

#Route to get all public transactions


@transaction_routes.route("/public/<int:page>")
def get_all_transactions(page):
    results = Transaction.query.filter(and_(Transaction.completed==True, Transaction.privacy==0))\
        .order_by(desc(Transaction.updated_at)).paginate(page, 5, False)
    more_data = results.has_next
    transactions = results.items
    data = [transaction.to_dict() for transaction in transactions]
    return {"data": data, "more_data": more_data}, 200


@transaction_routes.route("/<int:userid>/<int:page>")
def get_user_transactions(userid, page):
    results = Transaction.query.filter(or_(Transaction.payee_id == userid, Transaction.payer_id == userid), Transaction.completed == True)\
        .order_by(desc(Transaction.updated_at)).paginate(page, 5, False)
    more_data = results.has_next
    transactions = results.items
    data = [transaction.to_dict() for transaction in transactions]
    return {"data": data, "more_data": more_data}, 200


@transaction_routes.route("/<int:userid>/friends/<int:page>")
def get_friend_transactions(userid, page):
    user = User.query.get(userid)
    friends_list = [friend.id for friend in user.friends]
    
    results = Transaction.query.filter(or_( and_(Transaction.payer_id.in_(friends_list), or_(and_(Transaction.completed == True, Transaction.privacy == 0), and_(Transaction.completed == True, Transaction.privacy == 1))), and_(Transaction.payee_id.in_(friends_list), or_(and_(Transaction.completed == True, Transaction.privacy == 0), and_(Transaction.completed == True, Transaction.privacy == 1))))).order_by(desc(Transaction.updated_at)).paginate(page, 5, False)

    more_data = results.has_next
    transactions = results.items
    data = [transaction.to_dict() for transaction in transactions]
    return {"data": data, "more_data": more_data}, 200

# @transaction_routes.route("/<int:userid>/friends/<int:page>")
# def get_friend_transactions(userid, page):
#     user = User.query.get(userid)
#     results = Transaction.query.filter(or_(and_(Transaction.completed==True, Transaction.privacy==0), and_(Transaction.completed==True, Transaction.privacy==1)))\
#         .order_by(desc(Transaction.updated_at)).paginate(page, 5, False)
#     more_data = results.has_next
#     transactions = results.items
#     friends_list = [friend.id for friend in user.friends]
#     friend_transactions = [transaction for transaction in transactions if ((transaction.payer_id in friends_list)) or ((transaction.payee_id in friends_list))]
#     data = [transaction.to_dict() for transaction in friend_transactions]
#     return {"data": data, "more_data": more_data}, 200

# @transaction_routes.route("/public")
# def get_all_transactions():
#     transactions = Transaction.query.filter(and_(
#         Transaction.completed == True, Transaction.privacy == 0)).order_by(desc(Transaction.updated_at)).all()
#     data = [transaction.to_dict() for transaction in transactions]
#     return {"data": data}, 200

#Route to get all user's transactions
# @transaction_routes.route("/<int:userid>")
# def get_user_transactions(userid):
#     transactions = Transaction.query.filter(or_(Transaction.payee_id == userid, Transaction.payer_id == userid), Transaction.completed == True)\
#         .order_by(desc(Transaction.updated_at)).all()
#     data = [transaction.to_dict() for transaction in transactions]
#     return {"data": data}, 200


#Route to get all user's friends transactions
# @transaction_routes.route("/<int:userid>/friends")
# def get_friend_transactions(userid):
#     user = User.query.get(userid)
#     friends_list = [friend.id for friend in user.friends]
#     transactions = Transaction.query.filter(or_(and_(Transaction.completed==True, Transaction.privacy==0), and_(Transaction.completed==True, Transaction.privacy==1))).order_by(desc(Transaction.updated_at)).all()
#     friend_transactions = [transaction for transaction in transactions if ((transaction.payer_id in friends_list)) or ((transaction.payee_id in friends_list))]
#     data = [transaction.to_dict() for transaction in friend_transactions]
#     return {"data": data}, 200


#Route to get users unfulfilled debit transactions
@transaction_routes.route("/<int:userid>/debit")
def get_pending_debits(userid):
    transactions = Transaction.query.filter(Transaction.payer_id==userid, Transaction.completed==False)\
        .order_by(desc(Transaction.updated_at)).all()
    data = [transaction.to_dict() for transaction in transactions]
    return {"data": data}, 200

#Route to get users unfulfilled credit transactions
@transaction_routes.route("/<int:userid>/credit")
def get_pending_credits(userid):
    transactions = Transaction.query.filter(Transaction.payee_id==userid, Transaction.completed==False)\
        .order_by(desc(Transaction.updated_at)).all()
    data = [transaction.to_dict() for transaction in transactions]
    return {"data": data}, 200

#Route to post transaction (pay a user)
''' request json should look like this:
{
    "amount": 100.00,
    "payee_id": (user id of person recieving payment),
    "payer_id": (user id of person making payment),
    "message": "Optional message",
    "completed": true
}
'''
@transaction_routes.route("/pay", methods = ["POST"])
def create_payment_transaction():
    data = request.json
    transaction = Transaction(**data)
    payer = User.query.get(data["payer_id"])
    payee = User.query.get(data["payee_id"])
    transaction.updated_at = datetime.datetime.now()
    db.session.add(transaction)
    db.session.add(payer)
    payer.balance = float(payer.balance) - float(data["amount"])
    db.session.add(payee)
    payee.balance = float(payee.balance) + float(data["amount"])
    db.session.commit()
    return transaction.to_dict(), 200


#Route to post transaction (request payment from a user)
''' request json should look like this: **make sure completed is false
{
    "amount": 100.00,
    "payee_id": (user id of person recieving payment),
    "payer_id": (user id of person making payment),
    "message": "Optional message",
    "completed: false
}
'''
@transaction_routes.route("/request", methods = ["POST"])
def create_request_transaction():
    data = request.json
    transaction = Transaction(**data)
    db.session.add(transaction)
    transaction.updated_at = datetime.datetime.now()
    db.session.commit()
    return transaction.to_dict(), 200


#Route to update transaction (confirm payment)
''' request json should look like this, only need the transaction id:
{
    "transaction_id": id of transaction
}
'''
@transaction_routes.route("/confirm", methods = ["POST"])
def confirm_payment():
    data = request.json
    transaction = Transaction.query.get(data["transaction_id"])
    payer = User.query.get(transaction.payer_id)
    payee = User.query.get(transaction.payee_id)
    db.session.add(transaction)
    db.session.add(payer)
    payer.balance = payer.balance - transaction.amount
    db.session.add(payee)
    payee.balance = payee.balance + transaction.amount
    transaction.completed = True
    db.session.commit()
    return transaction.to_dict(), 200
