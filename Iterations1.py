import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox
from openai import OpenAI

# Initialize OpenAI API key
client = OpenAI(api_key="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")

class QuestionGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.all_questions = []
        self.all_keywords = []
        self.all_responses = []

    def initUI(self):
        self.setWindowTitle('ChatGPT Question Generator')
        self.setGeometry(100, 100, 600, 400)

        # Layout
        layout = QVBoxLayout()

        # Topic Input
        self.topicInput = QLineEdit(self)
        self.topicInput.setPlaceholderText('Enter a topic...')
        layout.addWidget(self.topicInput)

        # Generate 10 Questions Button
        self.generate10Btn = QPushButton('Start Iterative Q&A Generation', self)
        self.generate10Btn.clicked.connect(self.startIterativeQAGeneration)
        layout.addWidget(self.generate10Btn)

        # Text Area for Questions and Keywords
        self.questionsArea = QTextEdit(self)
        self.questionsArea.setReadOnly(True)
        layout.addWidget(self.questionsArea)

        self.setLayout(layout)

    def startIterativeQAGeneration(self):
        topic = self.topicInput.text().strip()
        if not topic:
            self.questionsArea.setText("Please enter a valid topic.")
            return
        self.iterativeQAGeneration(topic)

    def iterativeQAGeneration(self, topic, iteration=3):
        current_topic = topic
        for i in range(iteration):
            QAK = self.fetch10QuestionsAnswersKeyword(current_topic)
            print(f" \nQAK : \n{QAK} \n\n and len(QAK) : {len(QAK)}\n ")
            if len(QAK) == 3:
                questions, answers, keywords = QAK
                self.all_questions.extend(questions)
                self.all_keywords.extend(keywords)

            # if not QAK:
            #     questions, answers, keywords =  i for i in QAK

            self.questionsArea.setText(f"Iteration {i+1}: Completed\nQuestions Generated: {len(self.all_questions)}\nKeywords Identified: {len(self.all_keywords)}\nTotal Responses: {len(self.all_responses)}")

            if i == 9:
                user_decision = self.promptUserContinuation()
                if not user_decision:
                    break

        self.storeData()
        self.storeResponse()

    def fetch10QuestionsAnswersKeyword(self, topic):
        """Fetch 10 questions related to the topic using OpenAI API."""
        messages_str = [
            {
                "role": "user",
                "content": f"Generate 10 questions for {topic}, and give respective answers and summarize a keyword for it. Return dict of dicts for each question, answer and keyword in followig JSON Format question1:(question: \"\", answer:\"\", keyword: \"\" ).",
            }
        ]
        try:
            response = client.chat.completions.create(
                messages=messages_str,
                model="gpt-3.5-turbo"
            )
            response = response.choices[0].message.content.strip().split('\n')
            response_json = json.loads(''.join(response))
            print(f"Response JSON list lenght: {response_json}\n\nLength of response:{len(response_json)}")

            questions = []
            answers = []
            keywords = []
            responses = []

            for i in range(1,11):  # 10 items                
                # Appending values to respective lists
                q = response_json[f"question{i}"]["question"]
                a = response_json[f"question{i}"]["answer"]
                k = response_json[f"question{i}"]["keyword"]
                questions.append(q)
                answers.append(a)
                keywords.append(k)

                response_dict = {"q": q, "a": a, "k": k}  # Construct a dictionary for each question
                responses.append(response_dict) 
            
            self.all_responses.extend(responses)

            # print(f"\nquestions: {questions}\n, \nanswers: {answers}\n, \nkeywords: {keywords}\n")
            return [questions, answers, keywords]
        except Exception as e:
            return [f"Failed to fetch questions: {str(e)}"]

    def promptUserContinuation(self):
        reply = QMessageBox.question(self, 'Continue?', "Do you want to continue for another 10 iterations?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

    def storeData(self):
        # Simplified: Store questions and keywords in a JSON file
        with open('questions_and_keywords.json', 'w') as f:
            json.dump({'questions': self.all_questions, 'keywords': self.all_keywords}, f, indent=4)
        self.questionsArea.append("\nData stored in 'questions_and_keywords.json'.")

    def storeResponse(self):
        # Simplified: Store questions and keywords in a JSON file
        with open('all_responses.json', 'w') as f:
            json.dump({'responses': self.all_responses}, f, indent=4)
        self.questionsArea.append("\nData stored in 'all_responses.json'.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QuestionGeneratorApp()
    ex.show()
    sys.exit(app.exec_())
