import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt5.QtCore import Qt
from openai import OpenAI

api_key = os.environ.get('api_key')
if not api_key:
    raise ValueError("API key not found. Please set the 'api_key' environment variable.")

client = OpenAI(api_key=api_key)

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

        layout = QVBoxLayout()

        self.topicInput = QLineEdit(self)
        self.topicInput.setPlaceholderText('Enter a topic...')
        layout.addWidget(self.topicInput)

        self.generateBtn = QPushButton('Start Iterative Q&A Generation', self)
        self.generateBtn.clicked.connect(self.startIterativeQAGeneration)
        layout.addWidget(self.generateBtn)

        self.questionsArea = QTextEdit(self)
        self.questionsArea.setReadOnly(True)
        layout.addWidget(self.questionsArea)

        self.setLayout(layout)

    def startIterativeQAGeneration(self):
        topic = self.topicInput.text().strip()
        if not topic:
            QMessageBox.warning(self, 'Error', 'Please enter a valid topic.')
            return
        self.iterativeQAGeneration(topic)

    def iterativeQAGeneration(self, topic, iteration=3):
        QApplication.setOverrideCursor(Qt.WaitCursor)  # Show the user that a process is running
        try:
            for i in range(iteration):
                result = self.fetch10QuestionsAnswersKeyword(topic)
                if not isinstance(result, list):
                    QMessageBox.critical(self, 'Error', 'Failed to fetch data from OpenAI.')
                    break

                self.questionsArea.append(f"Iteration {i+1}: Completed\nQuestions Generated: {len(self.all_questions)}\nKeywords Identified: {len(self.all_keywords)}\nTotal Responses: {len(self.all_responses)}")

                if i == iteration - 1 or not self.promptUserContinuation():
                    break

            self.storeData()
        finally:
            QApplication.restoreOverrideCursor()

    def fetch10QuestionsAnswersKeyword(self, topic):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Generate questions, answers, and keywords for the topic: {topic}"}]
            )
            print(response.choices[0].message.content.strip().split('\n'))
            response = response.choices[0].message.content.strip().split('\n')

            qa_pairs = []
            keywords = []

            # Process the response
            for i in range(0, len(response) - 1, 3):  # Skip the last item (keywords) and iterate by steps of 3
                question = response[i]
                answer = response[i + 1]
                qa_pairs.append({"question": question, "answer": answer})

            # Extract keywords (assuming the last item contains keywords)
            keywords_str = response[-1]
            keywords = keywords_str.replace('Keywords: ', '').split(', ')

            # Example output
            for pair in qa_pairs:
                self.all_questions.append(pair['question'])
                self.all_questions.append(pair['answer'])
            for item in response:                
                self.all_responses.append(item)
            self.all_keywords.append(keywords)
            
            return response

        except Exception as e:
            print(f"Error: {e}")
            return None

    def promptUserContinuation(self):
        reply = QMessageBox.question(self, 'Continue?', "Do you want to continue for another iteration?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

    def storeData(self):
        with open('iteration_2_questions_and_keywords.json', 'w') as f:
            json.dump({'questions': self.all_questions, 'keywords': self.all_keywords}, f, indent=4)
        with open('iteration_2_all_responses.json.json', 'w') as f:
            json.dump({'responses': self.all_responses}, f, indent=4)
        self.questionsArea.append("\nData stored successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QuestionGeneratorApp()
    ex.show()
    sys.exit(app.exec_())
