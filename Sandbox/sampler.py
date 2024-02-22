import sys, os
from openai import OpenAI
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit

# Initialize OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

class QuestionGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ChatGPT Question Generator')
        self.setGeometry(100, 100, 600, 400)

        # Layout
        layout = QVBoxLayout()

        # Topic Input
        self.topicInput = QLineEdit(self)
        self.topicInput.setPlaceholderText('Enter a topic...')
        layout.addWidget(self.topicInput)

        # Generate Button
        self.generateBtn = QPushButton('Generate Questions', self)
        self.generateBtn.clicked.connect(self.onGenerateClicked)
        layout.addWidget(self.generateBtn)

        # Generate 10 Questions Button
        self.generate10Btn = QPushButton('Generate 10 Questions', self)
        self.generate10Btn.clicked.connect(self.onGenerate10Clicked)
        layout.addWidget(self.generate10Btn)

        # Text Area for Questions
        self.questionsArea = QTextEdit(self)
        self.questionsArea.setReadOnly(True)
        layout.addWidget(self.questionsArea)

        self.setLayout(layout)

    def onGenerate10Clicked(self):
        """Handle Generate 10 Questions Button click."""
        topic = self.topicInput.text().strip()
        if not topic:
            self.questionsArea.setText("Please enter a valid topic.")
            return

        questions = self.fetch10Questions(topic)
        self.questionsArea.setText("\n\n".join(questions))

    def fetch10Questions(self, topic):
        """Fetch 10 questions related to the topic using OpenAI API."""
        messages_str = [
            {
                "role": "user",
                "content": f"Generate 10 questions for {topic}",
            }
        ]
        try:
            response = client.chat.completions.create(
                messages=messages_str,
                model="gpt-3.5-turbo"
            )
            questions = response.choices[0].message.content.strip().split('\n')
            return questions
        except Exception as e:
            return [f"Failed to fetch questions: {str(e)}"]

    def fetchQuestions(self, topic):
        """Fetch questions related to the topic using OpenAI API."""
        messages_str = [
            {
                "role": "user",
                "content": f"{topic}",
            }
        ]
        try:
            response = client.chat.completions.create(
                messages=messages_str,
                model="gpt-3.5-turbo"
            )
            questions = response.choices[0].message.content.strip().split('\n')
            return questions
        except Exception as e:
            return [f"Failed to fetch questions: {str(e)}"]

    def onGenerateClicked(self):
        """Handle Generate Button click."""
        topic = self.topicInput.text().strip()
        if not topic:
            self.questionsArea.setText("Please enter a valid topic.")
            return

        questions = self.fetchQuestions(topic)
        self.questionsArea.setText("\n\n".join(questions))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QuestionGeneratorApp()
    ex.show()
    sys.exit(app.exec_())
