import unittest
from app.models import db, Question, TestCase, TestResult

class TestModels(unittest.TestCase):
    def setUp(self):
        # Configurar la base de datos de prueba
        db.create_all()

    def tearDown(self):
        # Limpiar después de cada test
        db.session.remove()
        db.drop_all()

    def test_question_creation(self):
        question = Question(
            question_text="Test question?",
            answer="Test answer",
            category="Test Category"
        )
        db.session.add(question)
        db.session.commit()
        
        self.assertIsNotNone(question.id)
        self.assertEqual(question.question_text, "Test question?")
        self.assertEqual(question.answer, "Test answer")
        self.assertEqual(question.category, "Test Category")

    def test_testcase_creation(self):
        testcase = TestCase(
            name="Test Case",
            description="Test Description",
            expected_output="Expected Output"
        )
        db.session.add(testcase)
        db.session.commit()
        
        self.assertIsNotNone(testcase.id)
        self.assertEqual(testcase.name, "Test Case")
        self.assertEqual(testcase.description, "Test Description")
        self.assertEqual(testcase.expected_output, "Expected Output")

    def test_testresult_creation(self):
        testcase = TestCase(
            name="Test Case",
            description="Test Description",
            expected_output="Expected Output"
        )
        db.session.add(testcase)
        db.session.commit()

        result = TestResult(
            testcase_id=testcase.id,
            actual_output="Actual Output",
            passed=True
        )
        db.session.add(result)
        db.session.commit()
        
        self.assertIsNotNone(result.id)
        self.assertEqual(result.testcase_id, testcase.id)
        self.assertEqual(result.actual_output, "Actual Output")
        self.assertTrue(result.passed)

if __name__ == '__main__':
    unittest.main() 