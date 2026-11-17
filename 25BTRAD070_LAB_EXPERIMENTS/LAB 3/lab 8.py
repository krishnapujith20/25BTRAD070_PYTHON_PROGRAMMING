contacts = {}


def add_contact(name, phone, email):
    if name in contacts:
        print(f"Contact '{name}' already exists.")
    else:
        contacts[name] = [phone, email]
        print(f"Contact '{name}' added successfully.")


def search_contact(name):
    if name in contacts:
        print(
            f"Name: {name} | Phone: {contacts[name][0]} | Email: {contacts[name][1]}"
        )
    else:
        print(f"Contact '{name}' not found.")


def update_contact(name, phone, email):
    if name in contacts:
        contacts[name] = [phone, email]
        print(f"Contact '{name}' updated successfully.")
    else:
        print(f"Contact '{name}' not found.")


def delete_contact(name):
    if name in contacts:
        del contacts[name]
        print(f"Contact '{name}' deleted successfully.")
    else:
        print(f"Contact '{name}' not found.")