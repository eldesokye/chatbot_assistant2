# 🤖 Chatbot Assistant 2

**Chatbot Assistant 2** is a modular, extensible chatbot framework designed to experiment with **LLM-powered agents, tools, and prompts**, with both **CLI-style execution** and a **Streamlit web interface**.

This project is an early-stage but well-structured foundation for building **production-style AI assistants**.

---

## 📌 Project Purpose

The goal of this repository is to:

* Build a clean structure for an AI chatbot assistant
* Experiment with **agents, tools, and prompts**
* Separate configuration, API logic, and UI
* Support rapid iteration and future expansion

It is ideal for:

* Learning AI assistant architecture
* Prototyping LLM agents
* Building Streamlit-based chat applications

---

## 🗂️ Project Structure

```text
chatbot_assistant2/
│
├── utils/                   # Utility helpers
├── agents.py                # Agent definitions and logic
├── tools.py                 # Tool functions used by agents
├── prompts.py               # Prompt templates
├── api_client.py            # LLM / API client abstraction
├── config.py                # Configuration & settings
├── app.py                   # Main application entry point
├── streamlit_chatbot.py     # Streamlit-based chatbot UI
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── LICENSE                  # MIT License
└── .gitignore
```

---

## 🚀 Features

* 🧠 Agent-based chatbot architecture
* 🛠️ Tool calling support
* 🧾 Centralized prompt management
* ⚙️ Config-driven design
* 🌐 Streamlit web interface
* 🔌 API abstraction layer (OpenAI / others)

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **LLM APIs (OpenAI-compatible)**
* **Streamlit**
* **Prompt Engineering**

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/eldesokye/chatbot_assistant2.git
cd chatbot_assistant2
```

### 2️⃣ Create & activate virtual environment

```bash
python -m venv venv
source venv/binactivate   # Linux / Mac
venv\\Scripts\\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Chatbot

### Option 1: Run core app

```bash
python app.py
```

### Option 2: Run Streamlit UI

```bash
streamlit run streamlit_chatbot.py
```

---

## 🧠 Architecture Overview

* **agents.py**: Defines how the chatbot reasons and responds
* **tools.py**: External or internal tools agents can use
* **prompts.py**: Central place for system & task prompts
* **api_client.py**: Handles communication with LLM APIs
* **streamlit_chatbot.py**: User-facing web interface

This separation mirrors **production-grade AI assistant design**.

---

## 🔮 Future Enhancements

* Memory & conversation history
* Multi-agent orchestration
* RAG integration
* Authentication & user sessions
* FastAPI backend
* Docker support

---

## 👨‍💻 Author

**Hesham El Desoky**
Generative AI & Machine Learning Engineer

---

## 📜 License

This project is licensed under the **MIT License**.

---

⭐ This project is a foundation for more advanced AI assistant systems.
