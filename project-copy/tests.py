
import unittest
# https://docs.python.org/3/library/unittest.html

import requests
from main import check_firstname_lastname, check_email, check_password, check_card, check_address
# unit testing for all data validation functions

class Test_check_firstname_lastname(unittest.TestCase):

    def test_true(self):
        self.assertEqual(check_firstname_lastname('jhdcszdcs', 'sdvsdvsvd'), True, 'First Name and Last Name are correct, output is wrong')
    def test_lastname_numeric(self):
        self.assertEqual(check_firstname_lastname('jhdcszdcs', '456456'), 'Your name can contain only letters. ', 'Last Name contains numbers, output is wrong')
    def test_firstname_numeric(self):
        self.assertEqual(check_firstname_lastname('123643546', 'jhdcszghbnd'), 'Your name can contain only letters. ', 'First Name contains numbers, output is wrong')
    def test_lastname_special_characters(self):
        self.assertEqual(check_firstname_lastname('jhdcszdcs', '##fgb'), 'Your name cannot contain special characters. ', 'Last Name contains special characters, output is wrong')
    def test_firstname_special_characters(self):
        self.assertEqual(check_firstname_lastname("j#*%$fgv", 'jhdcszdcs'), 'Your name cannot contain special characters. ', 'First Name contains special characters, output is wrong')
				
class Test_check_email(unittest.TestCase):

    def test_true(self):
        self.assertEqual(check_email('olesjhb0452@gmail.com'), True, 'Email is correct, output is wrong')
    def test_already_exists(self):
        self.assertEqual(check_email('test1'), 'Email already exists ', 'Email already exists, output is wrong')
    def test_wrong_format(self):
        self.assertEqual(check_email('jhdcszdcsfgfh@ggg66666'), 'Please enter an existing email. ', 'Email in the wrong format, output is wrong')


class Test_check_password(unittest.TestCase):

    def test_true(self):
        self.assertEqual(check_password('dfgrTtt54gg'), True, 'Password is correct, output is wrong')
    def test_wrong_length(self):
        self.assertEqual(check_password('jhjgft'), 'Make sure your password length is min 10 max 20 characters. ', 'Password is oo short/long, output is wrong')
    def test_no_numbers(self):
        self.assertEqual(check_password('fdsalkjhThjnjk'), 'Make sure your password has a number in it. ', 'Password does not have numbers in it, output is wrong')
    def test_upcase_and_lowcase(self):
        self.assertEqual(check_password('fdsalkj4567hjnjk'), 'Make sure your password has one upcase and one lowcase letter. ', 'Password does not have one upcase and one lowcase letter in it, output is wrong')


class Test_check_card_details(unittest.TestCase):

    def test_true(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '12/23', '344'), True, 'Card details are correct, output is wrong')
		
    def test_wrong_card_number_456(self):
        self.assertEqual(check_card('3567845364758675', 'Fhgjfngh FHgjnh', '12/23', '344'), 'Card number is invalid', 'Card number should start with 4,5 or 6, output is wrong')
    def test_wrong_card_number_short(self):
        self.assertEqual(check_card('456784536', 'Fhgjfngh FHgjnh', '12/23', '344'), 'Card number is too long/short', 'Card number is too short, output is wrong')
    def test_wrong_card_number_numeric(self):
        self.assertEqual(check_card('rthrhrhrhrh5654', 'Fhgjfngh FHgjnh', '12/23', '344'), 'Card number is not numeric.', 'Card number is not numeric, output is wrong')
    
    def test_wrong_name_special_characters(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfn#&&*gh', '12/23', '344'), 'Name can only contain letters', 'Name contains special characters, output is wrong')
    def test_wrong_name_numeric(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfn555gh ', '12/23', '344'), 'Name can only contain letters', 'Name has numbers in it, output is wrong')
    
    def test_wrong_cvv_numeric(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '12/23', '34T'), 'CVV is invalid', 'CVV is not numeric, output is wrong')
    def test_wrong_cvv_too_long(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '12/23', '34554'), 'CVV is invalid', 'CVV is too long, output is wrong')
    
    def test_wrong_expity_date_special_characters(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '12/2$', '344'), 'Expiry Date cannot contain special characters', 'Expiry Date contains special characters, output is wrong')
    def test_wrong_expity_date_letters(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '14t25', '344'), 'Expiry Date cannot contain letters', 'Expiry Date contains letters, output is wrong')
    def test_wrong_expity_date_too_short(self):
        self.assertEqual(check_card('4567845364758675', 'Fhgjfngh FHgjnh', '14/6', '344'), 'Expiry Date is too short/long', 'Expiry Date is too short, output is wrong')


class Test_check_address(unittest.TestCase):

    def test_true(self):
        self.assertEqual(check_address("45", "Kings road", 'Birmingham', 'United Kingdom', 'BT45FG'), True, 'Address is correct, output is wrong')
    def test_postcode_too_long(self):
        self.assertEqual(check_address("45", "Kings road", 'Birmingham', 'United Kingdom', 'PDOU76FGH'), 'Postcode is too long.', 'Postcode is too long, output is wrong')
    def test_special_characters(self):
        self.assertEqual(check_address("45", "Kings! road", 'Birming#ham', 'United Kingdom', 'BT45FG'), 'Address cannot contain special characters.', 'Address contains special characters in it, output is wrong')



if __name__ == '__main__':
    unittest.main()