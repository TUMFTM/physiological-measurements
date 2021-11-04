# Copyright Feiler 2021

"""Class should keep track of exclusion intervals"""

class SecondIndexIsSmallerThanFirst(Exception):
    def __init__(self, cur_val, previous_val):
        self.__cur_val = cur_val
        self.__previous_val = previous_val
        super().__init__()

    def __str__(self):
        return f'{self.__cur_val} is smaller than previous val {self.__previous_val}'


class ExclusionTracker:
    def __init__(self):
        self.__exclusion_intervals = []

    def __str__(self):
        output_text = ""
        for elem in self.__exclusion_intervals:
            output_text += f"{elem}\n"
        return output_text

    def process_index(self, index):
        """Store index and run callback, if one is set"""
        if self.current_interval_pair_is_not_finished():
            self.__raise_error_if_val_is_smaller_than_previous(index)
        self.__exclusion_intervals.append(index)

    def current_interval_pair_is_finished(self):
        """Return true, if current exclude interval has two indices"""
        return not self.current_interval_pair_is_not_finished()

    def current_interval_pair_is_not_finished(self):
        """Return true, if current exclude interval misses last index"""
        len_of_interval_list_is_odd = False
        if (len(self.__exclusion_intervals)%2) != 0:
            len_of_interval_list_is_odd = True
        return len_of_interval_list_is_odd

    def get_last_exclusion_pair(self):
        """Return the last two entries of exclusions"""
        return self.__exclusion_intervals[-2], self.__exclusion_intervals[-1]

    def get_all_exclusions(self):
        """Return all my data"""
        return self.__exclusion_intervals

    def __raise_error_if_val_is_smaller_than_previous(self, index):
        previous_index = self.__exclusion_intervals[-1]
        if index <= previous_index:
            raise SecondIndexIsSmallerThanFirst(index, previous_index)
