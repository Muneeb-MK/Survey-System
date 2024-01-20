import sqlite3

def create_database():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surveys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            survey_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            FOREIGN KEY(survey_id) REFERENCES surveys(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            answer_id INTEGER NOT NULL,
            FOREIGN KEY(question_id) REFERENCES questions(id),
            FOREIGN KEY(answer_id) REFERENCES answers(id)
        )
    """)

    conn.commit()
    conn.close()

def create_survey():
    """Creates a new survey with questions and answers."""
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()

    survey_name = input("Enter the survey name: ")
    cursor.execute("INSERT INTO surveys (name) VALUES (?)", (survey_name,))
    survey_id = cursor.lastrowid

    while True:
        question = input("Enter a question (or 'done' to finish): ")
        if question.lower() == "done":
            break

        cursor.execute("INSERT INTO questions (survey_id, question) VALUES (?, ?)", (survey_id, question))
        question_id = cursor.lastrowid

        while True:
            answer = input("Enter an answer choice (or 'done' to finish): ")
            if answer.lower() == "done":
                break

            cursor.execute("INSERT INTO answers (question_id, answer) VALUES (?, ?)", (question_id, answer))

    conn.commit()
    conn.close()

def run_survey():
    """Runs the survey and collects responses."""
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM surveys")
    surveys = cursor.fetchall()

    if not surveys:
        print("No surveys available. Please create a survey first.")
        return

    print("Available Surveys:")
    for survey_id, survey_name in surveys:
        print(f"{survey_id}) {survey_name}")

    while True:
        try:
            survey_id_choice = int(input("Enter the survey ID to run: "))
            cursor.execute("SELECT name FROM surveys WHERE id = ?", (survey_id_choice,))
            selected_survey = cursor.fetchone()

            if selected_survey:
                print(f"Running survey: {selected_survey[0]}")
                break
            else:
                print("Invalid survey ID. Please enter a valid ID.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Fetch and run the questions and answers for the selected survey...
    cursor.execute("SELECT id, question FROM questions WHERE survey_id = ?", (survey_id_choice,))
    questions = cursor.fetchall()

    for question_id, question in questions:
        print(question)
        cursor.execute("SELECT id, answer FROM answers WHERE question_id = ?", (question_id,))
        answers = cursor.fetchall()

        for answer_id, answer in answers:
            print(f"{answer_id}) {answer}")

        while True:
            try:
                response = int(input("Enter your choice: "))
                cursor.execute("INSERT INTO responses (question_id, answer_id) VALUES (?, ?)", (question_id, response))
                break
            except ValueError:
                print("Invalid choice. Please enter a number.")

    conn.commit()
    conn.close()

def generate_report():
    """Generates a report of the survey results."""
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()

    cursor.execute("SELECT surveys.name, questions.question, answers.answer, COUNT(*) AS num_responses FROM surveys JOIN questions ON surveys.id = questions.survey_id JOIN answers ON questions.id = answers.question_id JOIN responses ON answers.id = responses.answer_id GROUP BY surveys.id, questions.id, answers.id")
    results = cursor.fetchall()

    for survey_name, question, answer, num_responses in results:
        print(f"Survey: {survey_name}")
        print(f"Question: {question}")
        print(f"Answer: {answer} ({num_responses} responses)")
        print("-" * 50)

    conn.close()


if __name__ == "__main__":
    create_database()

    while True:
        print("\nSurvey Software")
        print("1. Create a survey")
        print("2. Run a survey")
        print("3. Generate report")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            create_survey()
        elif choice == "2":
            run_survey()
        elif choice == "3":
            generate_report()
        elif choice == "4":
            break
        else:
            print("Invalid choice")
