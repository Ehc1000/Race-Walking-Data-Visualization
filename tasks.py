from flask import Blueprint

tasks_bp = Blueprint("tasks", __name__)

def main():
    print("This function runs when the script is executed directly!")


if __name__ == "__main__":
    main()
