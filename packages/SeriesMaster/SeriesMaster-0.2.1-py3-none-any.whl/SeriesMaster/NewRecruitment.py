"""
NewRecruit - Candidate Filtering System

This module provides a class to filter job applicants based on specified criteria.

Class:
    NewRecruit:
        Filters candidates from a given list based on age, qualifications, expected salary, and experience.

        Methods:
            __init__(people, min_age, qualifications, max_salary, experience):
                Initializes the NewRecruit instance and filters candidates who meet the given conditions.
            
            __repr__() -> str:
                Returns a string representation of the class purpose.
            
            __len__() -> int:
                Returns the number of candidates who meet the criteria.
            
            FullSer() -> list:
                Returns the list of selected candidates.
"""

class NewRecruit:
    """
    A class to filter job applicants based on specific hiring criteria.

    Attributes:
        ser (list): A list of candidates who meet the given conditions.
    """

    def __init__(self, people, min_age, qualifications, max_salary, experience):
        """
        Initializes the NewRecruit class by filtering candidates who meet the specified criteria.

        Args:
            people (list): A list of dictionaries containing candidate details (age, qualification, salary_expected, experience).
            min_age (int): The minimum required age for the position.
            qualifications (list): A list of acceptable qualifications for the role.
            max_salary (int): The maximum salary the employer is willing to offer.
            experience (int): The maximum years of experience allowed for the role.
        """
        self.ser = []

        for i in people:
            x = 0
            if (
                i['age'] < min_age or 
                i['qualification'] not in qualifications or 
                max_salary < i['salary_expected'] or 
                i['experience'] > experience
            ):
                x = 1

            if x == 0:
                self.ser.append(i)

    def __repr__(self):
        """
        Returns a string representation of the class purpose.
        """
        return "Fetching the right application for a post"
    
    def __len__(self):
        """
        Returns the number of selected candidates.
        """
        return len(self.ser)
    
    def FullSer(self):
        """
        Returns the list of selected candidates.
        
        Returns:
            list: A list of candidates who meet the criteria.
        """
        return self.ser
