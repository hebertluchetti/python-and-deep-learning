class FileManager:
    ''' Class contains set of methods. The purpose is to handle files in more good-looking way.
    '''
    def track_from_file(self, filename):
        '''
        :param filename: str
            full path
        :return: list
            list of strings, where each string is one line in the file. Order has been preserved.
        '''
        with open(filename, 'rt') as file:
            lines = file.readlines()
            return lines

    def add_point_to_track(self, line, filename):
        ''' Useful when we are writing in one file from many different places in the code.

        :param line: str
        :param filename: str
            full path
        '''
        with open(filename, "a") as file:
            file.write(line + "\n")
            file.close()

    def clear_file(self, filename):
        ''' Clear chosen file.

        :param filename: str
            full path
        '''
        file = open(filename, "w")
        file.close()


class PointConverter:
    ''' Set of converting methods for string points like this : "123.0,234.33" => [123.0,234.33]  or
        the inverse [123.0,234.33] => "123.0,234.33" '''

    def string_to_list(self, line):
        '''
        :param line: str
            contains numbers
        :return: list
            list of lists
        '''

        return [element for element in line.split()]

    def string_to_integer(self, line):
        '''
        :param line: str
            contains numbers
        :return: list
            list of integers
        '''

        return [int(element) for element in line.split()]

    def string_to_float(self, string):
        '''
        :param string: str
            contains numbers
        :return: floats
            list of floating numbers
        '''

        return [float(element) for element in string.split()]

    def integer_to_string(self, point):
        '''
        :param ints: list
            list of integers
        :return: str
            contains numbers
        '''

        result = ""
        for element in point:
            result = result + str(int(element)) + " "
        return result

    def float_to_string(self, floats):
        '''
        :param floats: list
            list of floating numbers
        :return: str
            contains numbers
        '''

        result = ""
        for element in floats:
            result = result + str(element) + " "

        return result