from fin_common.database.utils import *

class ChatHistory:
    def __init__(self, email, messages):
        self.email = email
        self.messages = messages
    
    @staticmethod
    def from_dict(data):
        return ChatHistory(
            email=data["email"],
            messages=data["messages"]
        )
    
    def to_dict(self):
        return {
            "email": self.email,
            "messages": self.messages
        }
    class Message:
        def __init__(self, role, content):
            self.role = role # user or bot
            self.content = content
        
        @staticmethod
        def from_dict(data):
            return ChatHistory(
                role=data["role"],
                content=data["content"]
            )
        
        def to_dict(self):
            return {
                "role": self.role,
                "content": self.content
            }

def find_chat_history(email):
    result = find_from_collection("chat_history", {"email": email})
    return [] if result == None else result['messages']

def save_chat_history(email, messages):
    serialized_messages = [
        message.to_dict() if isinstance(message, ChatHistory.Message) else message
        for message in messages
    ]
    update_collection(
        "chat_history",
        {"email": email, "messages": serialized_messages},
        {"email": email}
    )

def initialize_chat_history(email):
    insert_into_collection(
        "chat_history", 
        {"email": email, "messages": []}
    )

def clear_chat_history(email):
    delete_from_collection_if_exists("chat_history", {"email": email})