
import pytest

from main import check_firstname_lastname, check_email

# https://docs.pytest.org/en/7.1.x/getting-started.html
# unit test example

@pytest.mark.parametrize("firstname, lastname, expected_result", [
    ('jhdcszdcs', 'sdvsdvsvd', True),
    ('jhdcszdcs', '456456', 'Your name can contain only letters. ' ),
    ('4964564', 'fgrjsprR', 'Your name can contain only letters. ' ),
		('jhdcszdcs', '##fgb', 'Your name cannot contain special characters. ' ),
    ('j#*%$fgv', 'jhdcszdcs', 'Your name cannot contain special characters. ' ),

])

def test_check_firstname_lastname(firstname,lastname, expected_result):
    assert check_firstname_lastname(firstname,lastname) == expected_result



if __name__ == '__main__':
    pytest.main()