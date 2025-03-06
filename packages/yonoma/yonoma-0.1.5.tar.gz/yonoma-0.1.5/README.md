# Yonoma Email Marketing Python SDK

The official **Python** client library for the **Yonoma Email Marketing API**.

---

## **📥 Installation**

### Install via **pip**:
```sh
pip install yonoma
```

or manually install from GitHub:
```sh
pip install git+https://github.com/YonomaHQ/yonoma-email-marketing-python
```

---

## **🚀 Quick Start**

### **Note:** This SDK requires **Python 3.7 or above**.

```python
from yonoma import Yonoma

# Initialize the client
yonoma = Yonoma(api_key="YOUR-API-KEY")
```

---

# **📂 Features**

## **📌 Lists**

### **Create a new lists**
```python
from yonoma.lists import Lists

Lists = Lists(yonoma)

response = Lists.create(list_name="New lists")
print(response)
```

### **Get a list of Lists**
```python
response = Lists.list_all()
print(response)
```

### **Retrieve a specific lists**
```python
response = Lists.retrieve(list_id="list_id")
print(response)
```

### **Update a lists**
```python
response = Lists.update(list_id="A0SADFD6PJ", list_name="Updated lists Name")
print(response)
```

### **Delete a lists**
```python
response = Lists.delete(list_id="list_id")
print(response)
```

---

## **📌 Tags**

### **Create a new tag**
```python
from yonoma.tags import Tags

Tags = Tags(yonoma)

response = Tags.create(tag_name="New Tag")
print(response)
```

### **Get a list of tags**
```python
response = Tags.list_all()
print(response)
```

### **Retrieve a specific tag**
```python
response = Tags.retrieve(tag_id="TAG_ID")
print(response)
```

### **Update a tag**
```python
response = Tags.update(tag_id="TAG_ID", tag_name="Updated Tag Name")
print(response)
```

### **Delete a tag**
```python
response = Tags.delete(tag_id="TAG_ID")
print(response)
```

---

## **📌 Contacts**

### **Create a new contact**
```python
from yonoma.contacts import Contacts

contacts = Contacts(yonoma)

response = contacts.create(
    list_id="list_id",
    email="email@example.com",
    status="Subscribed",  # or "Unsubscribed"
    data={
        "firstName": "Contact",
        "lastName": "One",
        "phone": "1234567890",
        "address": "123, NY street",
        "city": "NY City",
        "state": "NY",
        "country": "US",
        "zipcode": "10001"
    }
)
print(response)
```

### **Update a contact**
```python
response = contacts.update(
    list_id="list_id",
    contact_id="CONTACT_ID",
    status="Subscribed"  # or "Unsubscribed"
)
print(response)
```

### **Add a tag to a contact**
```python
response = contacts.add_tag(contact_id="CONTACT_ID", tag_id="TAG_ID")
print(response)
```

### **Remove a tag from a contact**
```python
response = contacts.remove_tag(contact_id="CONTACT_ID", tag_id="TAG_ID")
print(response)
```

---

## **🔗 Useful Links**

- **PyPI Package**: [Yonoma on PyPI](https://pypi.org/project/yonoma/)
- **GitHub Repository**: [Yonoma GitHub](https://github.com/YonomaHQ/yonoma-email-marketing-python)
- **Yonoma API Docs**: [Yonoma API Documentation](https://yonoma.io/api-reference/introduction)

---

## **📜 License**
This package is licensed under the **MIT License**.

---

This is the **official Python SDK** for **Yonoma Email Marketing**, providing seamless API integrations. 🚀

