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
    
    def parse_total_amount_from_bill(self, text):
        """Extract only the total amount from bill/invoice text"""
        # Patterns to find total amounts in bills/invoices
        total_patterns = [
            # Common total patterns
            r'total[:\s]*\$?(\d+\.?\d*)',
            r'grand\s+total[:\s]*\$?(\d+\.?\d*)',
            r'amount\s+due[:\s]*\$?(\d+\.?\d*)',
            r'final\s+amount[:\s]*\$?(\d+\.?\d*)',
            r'net\s+amount[:\s]*\$?(\d+\.?\d*)',
            r'balance\s+due[:\s]*\$?(\d+\.?\d*)',
            # Indian currency patterns
            r'total[:\s]*₹?(\d+\.?\d*)',
            r'grand\s+total[:\s]*₹?(\d+\.?\d*)',
            r'amount\s+due[:\s]*₹?(\d+\.?\d*)',
            # Pattern for amounts at end of lines (likely totals)
            r'.*total.*?(\d+\.\d{2})$',
            r'.*amount.*?(\d+\.\d{2})$',
        ]
        
        lines = text.split('\n')
        potential_totals = []
        
        # Look for total amounts
        for line in lines:
            line = line.strip().lower()
            if not line:
                continue
                
            for pattern in total_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        if 1 <= amount <= 100000:  # Reasonable range for bills
                            potential_totals.append({
                                'amount': amount,
                                'line': line,
                                'confidence': self._calculate_total_confidence(line)
                            })
                    except ValueError:
                        continue
        
        if not potential_totals:
            # Fallback: look for largest amount in the document
            all_amounts = re.findall(r'[\$₹]?(\d+\.?\d*)', text)
            amounts = []
            for amount_str in all_amounts:
                try:
                    amount = float(amount_str.replace(',', ''))
                    if 1 <= amount <= 100000:
                        amounts.append(amount)
                except ValueError:
                    continue
            
            if amounts:
                # Return the largest amount as likely total
                max_amount = max(amounts)
                return [{
                    'amount': Decimal(str(max_amount)),
                    'description': 'Bill Payment',
                    'date': datetime.now().date(),
                    'category': 'bills'
                }]
        
        # Sort by confidence and return the most likely total
        if potential_totals:
            potential_totals.sort(key=lambda x: x['confidence'], reverse=True)
            best_total = potential_totals[0]
            
            # Generate description based on the document content
            description = self._generate_bill_description(text)
            
            return [{
                'amount': Decimal(str(best_total['amount'])),
                'description': description,
                'date': self._extract_bill_date(text),
                'category': self._categorize_bill(text, description)
            }]
        
        return []
    
    def _calculate_total_confidence(self, line):
        """Calculate confidence score for a line containing a total amount"""
        confidence = 0
        
        # Higher confidence for lines with "total" keywords
        total_keywords = ['total', 'grand total', 'amount due', 'balance due', 'final amount']
        for keyword in total_keywords:
            if keyword in line:
                confidence += 10
        
        # Higher confidence for lines at the end (totals usually at bottom)
        confidence += 5
        
        # Higher confidence for properly formatted amounts
        if re.search(r'\d+\.\d{2}', line):
            confidence += 3
        
        return confidence
    
    def _generate_bill_description(self, text):
        """Generate a meaningful description for the bill based on content"""
        text_lower = text.lower()
        
        # Look for business/vendor names in the first few lines
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if len(line) > 5 and not re.match(r'^\d', line):
                # Clean up the line to extract business name
                cleaned = re.sub(r'[^\w\s]', ' ', line)
                cleaned = ' '.join(cleaned.split())
                if 3 <= len(cleaned) <= 50:
                    return f"Bill from {cleaned}"
        
        # Categorize based on content
        if any(word in text_lower for word in ['hotel', 'room', 'night', 'stay']):
            return "Hotel Bill"
        elif any(word in text_lower for word in ['restaurant', 'food', 'meal', 'dining']):
            return "Restaurant Bill"
        elif any(word in text_lower for word in ['electricity', 'water', 'gas', 'utility']):
            return "Utility Bill"
        elif any(word in text_lower for word in ['phone', 'mobile', 'internet', 'telecom']):
            return "Telecom Bill"
        elif any(word in text_lower for word in ['medical', 'hospital', 'doctor', 'pharmacy']):
            return "Medical Bill"
        elif any(word in text_lower for word in ['shopping', 'store', 'retail']):
            return "Shopping Bill"
        else:
            return "Bill Payment"
    
    def _extract_bill_date(self, text):
        """Extract date from bill text"""
        # Look for date patterns
        date_patterns = [
            r'date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'invoice\s+date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'bill\s+date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Try different date formats
                    for date_format in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y', '%d/%m/%Y', '%d-%m-%Y']:
                        try:
                            return datetime.strptime(match, date_format).date()
                        except ValueError:
                            continue
                except:
                    continue
        
        # Default to today's date
        return datetime.now().date()
    
    def _categorize_bill(self, text, description):
        """Categorize bill based on content"""
        text_lower = text.lower()
        description_lower = description.lower()
        
        # Hotel/Travel
        if any(word in text_lower for word in ['hotel', 'room', 'night', 'stay', 'booking']):
            return 'travel'
        
        # Food/Restaurant
        if any(word in text_lower for word in ['restaurant', 'food', 'meal', 'dining', 'cafe', 'bar']):
            return 'food'
        
        # Utilities
        if any(word in text_lower for word in ['electricity', 'water', 'gas', 'utility', 'power']):
            return 'bills'
        
        # Telecom
        if any(word in text_lower for word in ['phone', 'mobile', 'internet', 'telecom', 'broadband']):
            return 'bills'
        
        # Medical
        if any(word in text_lower for word in ['medical', 'hospital', 'doctor', 'pharmacy', 'health']):
            return 'healthcare'
        
        # Shopping
        if any(word in text_lower for word in ['shopping', 'store', 'retail', 'purchase']):
            return 'shopping'
        
        # Transportation
        if any(word in text_lower for word in ['taxi', 'uber', 'transport', 'fuel', 'gas']):
            return 'transportation'
        
        # Default to bills
        return 'bills'
    
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
        """Main method to process PDF and extract only the total amount from bills"""
        try:
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_file)
            
            if not text:
                raise Exception("No text could be extracted from the PDF")
            
            # Extract only the total amount from the bill
            expenses = self.parse_total_amount_from_bill(text)
            
            if not expenses:
                raise Exception("No total amount could be identified in the bill")
            
            return expenses
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")