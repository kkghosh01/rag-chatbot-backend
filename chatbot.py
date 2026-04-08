from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a customer service assistant for {business_name}.
Business type: {business_type}
Location: {location}

STRICT RULES:
- ONLY use information provided below. Never make up information.
- If unsure, say: "এই বিষয়ে নিশ্চিত না, 01712-345678 এ call করুন"
- Always respond in Bengali
- Never mention other cities or locations outside of what's given

Business info:
{business_info}
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_input}"),
])

chain = prompt | llm

business_config = {
    "business_name": "Tasty Bites Restaurant",
    "business_type": "Restaurant",
    "location": "Dhaka, Bangladesh",
    "business_info": """
    - Opening hours: 10am - 11pm (everyday)
    - Special dishes: Kacchi Biryani, Beef Bhuna, Fish Curry
    - Home delivery available (Dhaka only)
    - Contact: 01712-345678
    - Average cost: 300-500 taka per person
    """
}

chat_history = []

print(f"🍽️ {business_config['business_name']} Chatbot Ready!\n")

while True:
    user_input = input("Customer: ")
    if user_input.lower() == "exit":
        break

    response = chain.invoke({
        **business_config,
        "chat_history": chat_history,
        "user_input": user_input,
    })

    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response.content))

    print(f"Bot: {response.content}\n")