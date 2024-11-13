
import unittest
import json
import io
from server import app

class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_submit_json(self):
        response = self.app.post('/submit_json', 
                                 data=json.dumps({
                                     'description': 'Test description',
                                     'company': 'Test company',
                                     'email': 'test@example.com'
                                 }),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])
        self.assertIn('JSON received', response.json['message'])

    def test_submit_pdf_no_file(self):
        response = self.app.post('/submit_pdf')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json['status'])
        self.assertIn('No file part', response.json['message'])

    def test_submit_pdf_no_selected_file(self):
        data = {
            'file': (None, '')
        }
        response = self.app.post('/submit_pdf', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json['status'])
        self.assertIn('No selected file', response.json['message'])

    def test_submit_pdf_invalid_file_type(self):
        data = {
            'file': (io.BytesIO(b"fake content"), 'test.txt')
        }
        response = self.app.post('/submit_pdf', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json['status'])
        self.assertIn('Invalid file type', response.json['message'])

    def test_submit_pdf_success(self):
        data = {
            'file': (io.BytesIO(b"%PDF-1.4\n%..."), 'test.pdf')
        }
        response = self.app.post('/submit_pdf', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json['status'])
        self.assertIn('PDF received', response.json['message'])

if __name__ == '__main__':
    unittest.main()