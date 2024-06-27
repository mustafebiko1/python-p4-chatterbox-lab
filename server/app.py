from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by(Message.created_at).all()
        if messages is not None:
            message_list = [
                {
                    "id": message.id,
                    "body": message.body,
                    "username": message.username,
                    "created_at": message.created_at.isoformat(),
                    "updated_at": message.updated_at.isoformat() 
                }
                for message in messages
            ]
            return jsonify({"messages": message_list})
        else:
            return jsonify({"messages": []})
    
    elif request.method == "POST":
        data = request.json
        body = data.get("body")
        username = data.get("username")
        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()

        response_data = {
            "id": new_message.id,
            "body": new_message.body,
            "username": new_message.username,
            "created_at": new_message.created_at.isoformat(),
            "updated_at": new_message.updated_at.isoformat()
        }
        return jsonify(response_data), 200, {'Content-Type': 'application/json'}



@app.route('/messages/<int:id>', methods=["DELETE", "PATCH"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    if message:
        if request.method == 'DELETE':
            db.session.delete(message)
            db.session.commit()
            message_body = {
                "delete_successful": True,
                "message": "message deleted."    
            }

            response = make_response(
                jsonify(message_body),
                200
            )

            return response

        elif request.method == 'PATCH':
            data = request.json
            new_body = data.get("body")
            if new_body:
                message.body = new_body
                db.session.commit()
                updated_message = {
                    "id": message.id,
                    "body": message.body,
                    "username": message.username,
                    "created_at": message.created_at.isoformat(),
                    "updated_at": message.updated_at.isoformat()
                }
                return jsonify(updated_message)
            else:
                return jsonify({"error": "No update"}), 200
    else:
        return jsonify({"error": "Message not found"}), 404


if __name__ == '__main__':
    app.run(port=5555)