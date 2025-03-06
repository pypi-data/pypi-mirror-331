

class helper:


    @staticmethod
    def checknumber(number):
        if not isinstance(number, int):
            raise TypeError(f"{number} should be a integer")