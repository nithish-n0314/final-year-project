import PyPDF2
import re
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
from decimal import Decimal

class PDFExpenseExtractor:
    def __init__(self):
        # Load Hugging Face sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Category embeddings for semantic matching
        self.category_descriptions = {
            'food': 'restaurant dining meal food eat lunch dinner breakfast cafe',
            'transportation': 'uber taxi bus train gas fuel parking transport travel',
            'shopping': 'store purchase buy retail clothing amazon shopping mall',
            'entertainment': 'movie theater concert game entertainment fun recreation',
            'bills': 'electricity water internet phone bill utility payment',
            'healthcare': 'doctor hospital pharmacy medical health medicine',
            'education': 'school university course book tuition education learning',
            'travel': 'hotel flight airline vacation trip travel booking',
            'groceries': 'grocery supermarket market food shopping walmart target',
            'other': 'miscellaneous other general expense payment'
        }
        
        # Pre-compute category embeddings
        self.category_embeddings = {}
        for category, description in self.category_descriptions.items():
            self.category_embeddings[category] = self.model.encode(description)
    
    def extract_text_from_pdf(self, pdf_file):
        """Extract text content from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def parse_expenses_from_text(self, text):
        """Parse expenses from extracted text using regex patterns"""
        expenses = []
        
        # Common patterns for expense extraction
        patterns = [
            # Pattern: Amount Description Date
            r'(\$?\d+\.?\d*)\s+([A-Za-z\s&\-\']+)\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            # Pattern: Date Description Amount
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+([A-Za-z\s&\-\']+)\s+\$?(\d+\.?\d*)',
            # Pattern: Description $Amount
            r'([A-Za-z\s&\-\']{3,})\s+\$(\d+\.?\d*)',
            # Pattern: Simple amount and description on same line
            r'(\d+\.?\d*)\s+([A-Za-z\s&\-\']{3,})',
        ]
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                
                for match in matches:
                    try:
                        if len(match) == 3:
                            # Pattern with date
                            if '$' in match[0] or '.' in match[0]:
                                # Amount, Description, Date
                                amount_str = match[0].replace('$', '').strip()
                                description = match[1].strip()
                                date_str = match[2].strip()
                            else:
                                # Date, Description, Amount
                                date_str = match[0].strip()
                                description = match[1].strip()
                                amount_str = match[2].replace('$', '').strip()
                        else:
                            # Pattern without date
                            if '.' in match[0] or match[0].isdigit():
                                # Amount, Description
                                amount_str = match[0].replace('$', '').strip()
                                description = match[1].strip()
                            else:
                                # Description, Amount
                                description = match[0].strip()
                                amount_str = match[1].replace('$', '').strip()
                            date_str = None
                        
                        # Validate amount
                        try:
                            amount = float(amount_str)
                            if amount <= 0 or amount > 10000:  # Reasonable limits
                                continue
                        except ValueError:
                            continue
                        
                        # Clean description
                        description = re.sub(r'[^\w\s&\-\']', ' ', description)
                        description = ' '.join(description.split())
                        
                        if len(description) < 3 or len(description) > 100:
                            continue
                        
                        # Parse date if available
                        expense_date = None
                        if date_str:
                            try:
                                # Try different date formats
                                for date_format in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                                    try:
                                        expense_date = datetime.strptime(date_str, date_format).date()
                                        break
                                    except ValueError:
                                        continue
                            except:
                                pass
                        
                        if not expense_date:
                            expense_date = datetime.now().date()
                        
                        expenses.append({
                            'amount': Decimal(str(amount)),
                            'description': description,
                            'date': expense_date
                        })
                        
                    except Exception:
                        continue
        
        # Remove duplicates based on amount and description similarity
        unique_expenses = []
        for expense in expenses:
            is_duplicate = False
            for existing in unique_expenses:
                if (abs(expense['amount'] - existing['amount']) < Decimal('0.01') and 
                    self._similarity(expense['description'], existing['description']) > 0.8):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_expenses.append(expense)
        
        return unique_expenses[:20]  # Limit to 20 expenses per PDF
    
    def categorize_expense_semantic(self, description):
        """Categorize expense using Hugging Face sentence embeddings"""
        try:
            # Encode the expense description
            description_embedding = self.model.encode(description)
            
            # Calculate similarity with each category
            similarities = {}
            for category, category_embedding in self.category_embeddings.items():
                similarity = np.dot(description_embedding, category_embedding) / (
                    np.linalg.norm(description_embedding) * np.linalg.norm(category_embedding)
                )
                similarities[category] = similarity
            
            # Return category with highest similarity
            best_category = max(similarities, key=similarities.get)
            
            # If similarity is too low, return 'other'
            if similarities[best_category] < 0.3:
                return 'other'
            
            return best_category
            
        except Exception:
            return 'other'
    
    def _similarity(self, text1, text2):
        """Calculate simple text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def process_pdf_expenses(self, pdf_file):
        """Main method to process PDF and extract categorized expenses"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_file)
            
            if not text:
                raise Exception("No text could be extracted from the PDF")
            
            # Parse expenses from text
            expenses = self.parse_expenses_from_text(text)
            
            if not expenses:
                raise Exception("No expenses could be identified in the PDF")
            
            # Categorize each expense using semantic similarity
            for expense in expenses:
                expense['category'] = self.categorize_expense_semantic(expense['description'])
            
            return expenses
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")