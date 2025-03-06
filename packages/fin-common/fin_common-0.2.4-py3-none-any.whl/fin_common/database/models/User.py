from fin_common.database.utils import *
from fin_common.database.models.Stock import Holding, Transaction

class PortfolioAnalysis:
    def __init__(self, risk_level, diversification_score):
        self.risk_level = risk_level
        self.diversification_score = diversification_score

    @staticmethod
    def from_dict(data):
        return PortfolioAnalysis(
            risk_level=data.get("risk_level"),
            diversification_score=data.get("diversification_score")
        )
    
    def to_dict(self):
        return {
            "risk_level": self.risk_level,
            "diversification_score": self.diversification_score
        }
    

class User: # equivalent to Profile
    def __init__(self, password, email, risk_level="N/A", investment_goals="N/A", investment_experience="N/A", income=0, investment_preferences="N/A", cash=0, holdings=[], portfolio_analysis=PortfolioAnalysis("N/A", 0), transactions=[], subscribe_newsletter=True):
        self.password = password
        self.email = email
        self.risk_level = risk_level
        self.investment_goals = investment_goals
        self.investment_experience = investment_experience
        self.income = income
        self.investment_preferences = investment_preferences
        self.cash = cash
        self.holdings: Holding = holdings
        self.transactions: Transaction = transactions
        self.history = [] # list of dictionaries with date and value
        self.subscribe_newsletter = subscribe_newsletter
        self.portfolio_analysis: PortfolioAnalysis = portfolio_analysis
        
    @staticmethod
    def from_dict(data):
        return User(
            password=data.get("password"),
            email=data.get("email"),
            risk_level=data.get("risk_level", "N/A"),
            investment_goals=data.get("investment_goals", "N/A"),
            investment_experience=data.get("investment_experience", "N/A"),
            income=data.get("income", 0),
            investment_preferences=data.get("investment_preferences", "N/A"),
            cash=data.get("cash", 0),
            holdings=[Holding.from_dict(holding) for holding in data.get("holdings", [])],
            transactions=[Transaction.from_dict(transaction) for transaction in data.get("transactions", [])],
            portfolio_analysis=data.get("portfolio_analysis", {}),
            subscribe_newsletter=data.get("subscribe_newsletter", True)
        )
    
    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "risk_level": self.risk_level,
            "investment_goals": self.investment_goals,
            "investment_experience": self.investment_experience,
            "income": self.income,
            "investment_preferences": self.investment_preferences,
            "cash": self.cash,
            "holdings": [holding.to_dict() for holding in self.holdings],  # Assuming Holding class has a to_dict method
            "portfolio_analysis": self.portfolio_analysis.to_dict(),
            "transactions": [transaction.to_dict() for transaction in self.transactions],  # Assuming Transaction class has a to_dict method
            "history": self.history,
            "subscribe_newsletter": self.subscribe_newsletter
        }

def is_valid_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

def find_user(query):
    return find_from_collection("users", query)

def create_user(email, password, subscribe_newsletter):
    if find_user({"email": email}) != None:
        return False, "User already exists"
    elif not is_valid_email(email):
        return False, "Invalid email format"

    user = User(
        password=password,
        email=email,
        subscribe_newsletter=subscribe_newsletter
    )
    
    insert_into_collection("users", user.to_dict())
    return True, "Success"

def update_user_profile(user):
    if '_id' in user:
        del user['_id']

    if find_user({"email": user['email']}) == None:
        return False, "User does not exist"
    update_collection("users", user, {"email": user['email']})
    return True, "User updated"


