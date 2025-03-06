def get_user_info():
    """Prompt the user for basic information."""
    name = input("Enter your first name: ").strip().capitalize()
    family_name = input("Enter your family name: ").strip().capitalize()
    age = input("Enter your age: ").strip()
    hobby = input("What's your favorite hobby? ").strip().capitalize()
    
    return {
        "name": name,
        "family_name": family_name,
        "age": age,
        "hobby": hobby
    }
