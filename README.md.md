
# 🔐 An Efficient Search Scheme Over Encrypted Data on Cloud  
### **Author: Rubeshkanna Ravichandran — Aspiring Data Analyst**

---

## 📌 **Project Overview**

This project demonstrates a **secure and efficient searchable encryption system** that allows users to upload encrypted data to the cloud and search over it **without decrypting the entire dataset**.  
It uses:

- **Fernet symmetric encryption**  
- **Secure keyword-based search**  
- **Streamlit Web Application UI**  
- **Cloud-ready architecture (Firebase/AWS compatible)**  

This is useful for **privacy-preserving cloud storage**, **secure document search**, and **data protection applications**.

---

## 🚀 **Features**

### 🔑 Encryption  
- Encrypts text data using **Fernet AES-128** based encryption.  
- Stores encrypted files securely in cloud storage or locally.

### 🔍 Searchable Encryption  
- Searches encrypted data **after decrypting line-by-line**, ensuring privacy.  
- Supports **keyword-based matching**.

### 🌐 Web Application  
Built with **Streamlit**, providing:  
- Login system  
- Data upload page  
- Encryption module  
- Search dashboard  
- Activity logs

### 👥 Multi-User System  
- Each user gets isolated encrypted storage.  
- Session management using Streamlit.

---

## 🏗️ **Project Structure**

```
project/
│── app.py                # Streamlit main web app
│── encrypted_search.py    # Core encryption + search functions
│── secret.key             # Auto-generated encryption key
│── cloud_data.txt         # Encrypted data file
│── requirements.txt       # Required Python libraries
│── README.md              # Documentation
```

---

## ⚙️ **How It Works (Workflow)**

### 1️⃣ Generate Encryption Key  
A Fernet key is generated and stored securely.

### 2️⃣ Encrypt Data  
Data is encrypted line-by-line and uploaded to cloud storage/ local disk.

### 3️⃣ Search in Encrypted Data  
Keyword is compared with each decrypted line → matched results displayed.

### 4️⃣ Web Interface  
Users interact through a Streamlit dashboard.

---

## 📦 **Installation Guide**

### **Step 1 — Install Requirements**
```
pip install -r requirements.txt
```

If Streamlit missing:
```
pip install streamlit cryptography
```

---

## ▶️ **Run the Web App**
```
streamlit run app.py
```

App opens in browser automatically.

---

## 🔧 **Technologies Used**

| Component | Technology |
|----------|------------|
| Encryption | Cryptography (Fernet) |
| Frontend | Streamlit |
| Cloud Storage | Firebase / AWS S3 (Optional) |
| Language | Python |
| Search Method | Keyword matching |

---

## 📊 **Use Cases**

✔ Secure document storage  
✔ Confidential healthcare data search  
✔ Financial encrypted data archive  
✔ Cloud-based privacy-preserving search  

---

## 🧪 Testing

- Unit tests for encryption  
- Keyword search accuracy testing  
- Streamlit UI testing  
- Cloud upload/download test cases  

---

## 🤝 **Contributing**

Pull requests are welcome!  
You may contribute by:

- Improving encryption logic  
- Expanding UI features  
- Adding database support  

---

## 🧑‍💻 **Author**

**Rubeshkanna Ravichandran**  
*Aspiring Data Analyst | Python Developer | Cloud & Security Enthusiast*

---

## 📜 **License**

This project is licensed under the **MIT License** — free to use and modify.

---
