from intro_python_101.core import get_user_info
from intro_python_101.scenario import generate_scenario

def main():
    print("Welcome to the Interactive Story Generator!\n")
    
    user_info = get_user_info()
    story = generate_scenario(user_info)
    
    print("\nHere's your personalized story:")
    print(story)

if __name__ == "__main__":
    main()
